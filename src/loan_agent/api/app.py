"""FastAPI skeleton bọc pipeline thẩm định — ADR-0017 (hợp đồng API).

⚠️ SKELETON: đường dẫn + schema request/response có thể đổi theo hợp đồng API thật với
Vapp (open-questions T1). Chạy dev:
    uvicorn loan_agent.api.app:app --reload     (PYTHONPATH=src)
Tài liệu tự sinh tại /docs.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException

from ..compliance.audit import AuditLog
from ..compliance.transparency import build_notice
from ..config import load_decision_table, settings
from ..graph import build_graph
from ..llm.factory import get_llm
from ..rag.factory import get_store
from ..schemas import LoanApplication
from ..service import run_assessment
from .sessions import SessionStore

app = FastAPI(title="Loan Agent API (skeleton)", version="0.1.0")

_runtime: dict = {}


def _engine():
    """Khởi tạo graph + audit LƯỜI (tránh gọi mạng/embedding lúc import module)."""
    if "graph" not in _runtime:
        _runtime["graph"] = build_graph(
            get_llm(),
            get_store(),
            load_decision_table(),
            max_turns=settings.max_intake_turns,
        )
        _runtime["audit"] = AuditLog(settings.audit_log_path)
    return _runtime["graph"], _runtime["audit"]


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "llm_provider": settings.llm_provider,
        "rag_backend": settings.rag_backend,
    }


def _completed_response(result: dict) -> dict:
    """Khối phản hồi khi đã ra quyết định (dùng chung cho /assess và /sessions)."""
    return {
        "status": "completed",
        "decision": result["decision"],
        "affordability": result.get("affordability"),
        "transparency_notice": build_notice(result),
        "policy_citations": (result.get("policy") or {}).get("citations", []),
    }


@app.post("/assess")
def assess(application: LoanApplication) -> dict:
    """Thẩm định 1 hồ sơ ĐỦ field một phát. Thiếu field core → trả danh sách thiếu.

    Hội thoại nhiều lượt (khai dần, lưu phiên): dùng các cửa /sessions bên dưới.
    """
    missing = application.missing_required_fields()
    if missing:
        return {"status": "incomplete", "missing_required_fields": missing}

    graph, audit = _engine()
    result = run_assessment(graph, application.model_dump(mode="json"), audit)
    return _completed_response(result)


# --- Hội thoại nhiều lượt + lưu phiên (ADR-0013) ------------------------------

# Câu hỏi cho từng field core — "nhân viên ảo" hỏi từng bước (khớp run_interactive CLI).
_QUESTIONS = {
    "loan.amount": "Bạn muốn vay số tiền bao nhiêu (VND)?",
    "loan.purpose": "Bạn vay để làm gì (mục đích)?",
    "loan.term_months": "Bạn muốn vay trong bao nhiêu tháng?",
    "income.monthly": "Thu nhập hằng tháng của bạn khoảng bao nhiêu (VND)?",
    "income.source": "Nguồn thu nhập của bạn là gì (luong/kinh_doanh/khac)?",
    "income.stability": "Thu nhập có ổn định không (on_dinh/khong_on_dinh)?",
    "debt.total": "Tổng dư nợ hiện tại bao nhiêu (VND)? (0 nếu không có)",
    "debt.monthly_payment": "Mỗi tháng đang trả nợ bao nhiêu (VND)? (0 nếu không có)",
    "profile.age": "Bạn bao nhiêu tuổi?",
    "profile.occupation": "Nghề nghiệp của bạn là gì?",
    "profile.tenure_years": "Bạn làm công việc hiện tại được bao nhiêu năm?",
    "credit_history.had_late_payment": "Bạn từng trả nợ trễ hạn chưa (true/false)?",
}


def _next_question(missing: list[str]) -> str | None:
    if not missing:
        return None
    return _QUESTIONS.get(missing[0], f"Bạn bổ sung giúp: {missing[0]}?")


def _merge_app(stored: dict, patch: dict) -> dict:
    """Deep-merge patch (chỉ field khác None) vào hồ sơ dở theo từng section."""
    merged = {section: dict(fields) for section, fields in stored.items()}
    for section, fields in patch.items():
        if isinstance(fields, dict):
            merged.setdefault(section, {}).update(fields)
    return merged


def _session_store() -> SessionStore:
    if "sessions" not in _runtime:
        _runtime["sessions"] = SessionStore(settings.session_db_path)
    return _runtime["sessions"]


@app.post("/sessions")
def start_session() -> dict:
    """Mở phiên intake mới. Trả session_id + field còn thiếu + câu hỏi đầu tiên."""
    sid = _session_store().create()
    missing = LoanApplication().missing_required_fields()
    return {
        "session_id": sid,
        "status": "incomplete",
        "missing_required_fields": missing,
        "next_question": _next_question(missing),
    }


@app.post("/sessions/{session_id}/message")
def session_message(session_id: str, patch: LoanApplication) -> dict:
    """Gửi thêm thông tin cho phiên → merge vào hồ sơ dở, hỏi tiếp hoặc ra quyết định.

    `patch` là LoanApplication một phần (mọi field optional); chỉ field khác None được
    ghi đè. Offline gửi field có cấu trúc; có OpenAI thật sẽ trích từ câu chữ tự do.
    """
    store = _session_store()
    sess = store.get(session_id)
    if sess is None:
        raise HTTPException(status_code=404, detail="session không tồn tại")

    provided = patch.model_dump(mode="json", exclude_none=True)
    merged = _merge_app(sess["application"], provided)
    messages = sess["messages"]
    filled = [
        f"{section}.{field}"
        for section, fields in provided.items()
        if isinstance(fields, dict)
        for field in fields
    ]
    if filled:
        messages.append({"role": "user", "content": "Đã cung cấp: " + ", ".join(filled)})

    missing = LoanApplication.model_validate(merged).missing_required_fields()
    if missing:
        question = _next_question(missing)
        messages.append({"role": "assistant", "content": question})
        store.save(session_id, merged, messages)
        return {
            "session_id": session_id,
            "status": "incomplete",
            "missing_required_fields": missing,
            "next_question": question,
            "application": merged,
        }

    store.save(session_id, merged, messages)
    graph, audit = _engine()
    result = run_assessment(graph, merged, audit)
    return {"session_id": session_id, **_completed_response(result)}


@app.get("/sessions/{session_id}")
def get_session(session_id: str) -> dict:
    """Xem lại phiên (nối phiên: thoát ra rồi vào lại vẫn còn hồ sơ dở)."""
    store = _session_store()
    sess = store.get(session_id)
    if sess is None:
        raise HTTPException(status_code=404, detail="session không tồn tại")
    missing = LoanApplication.model_validate(sess["application"]).missing_required_fields()
    return {
        "session_id": session_id,
        "status": "ready" if not missing else "incomplete",
        "application": sess["application"],
        "messages": sess["messages"],
        "missing_required_fields": missing,
    }
