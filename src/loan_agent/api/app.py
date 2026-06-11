"""FastAPI skeleton bọc pipeline thẩm định — ADR-0017 (hợp đồng API).

⚠️ SKELETON: đường dẫn + schema request/response có thể đổi theo hợp đồng API thật với
Vapp (open-questions T1). Chạy dev:
    uvicorn loan_agent.api.app:app --reload     (PYTHONPATH=src)
Tài liệu tự sinh tại /docs.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from ..compliance.audit import AuditLog
from ..compliance.consent import build_consent_notice
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


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Chặn truy cập khi đã cấu hình LOAN_API_KEY. Rỗng = tắt auth (dev/test/offline).

    Production BẮT BUỘC đặt LOAN_API_KEY. /health để mở (load balancer cần thăm dò).
    """
    if settings.api_key and x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Thiếu hoặc sai API key (header X-API-Key).")


def _audit() -> AuditLog:
    if "audit" not in _runtime:
        _runtime["audit"] = AuditLog(settings.audit_log_path)
    return _runtime["audit"]


def _engine():
    """Khởi tạo graph LƯỜI (tránh gọi mạng/embedding lúc import module)."""
    if "graph" not in _runtime:
        _runtime["graph"] = build_graph(
            get_llm(),
            get_store(),
            load_decision_table(),
            max_turns=settings.max_intake_turns,
        )
    return _runtime["graph"], _audit()


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "llm_provider": settings.llm_provider,
        "rag_backend": settings.rag_backend,
    }


@app.get("/demo", response_class=HTMLResponse)
def demo() -> str:
    """Trang demo (chat trợ lý ảo) — phục vụ cùng origin để gọi API không vướng CORS."""
    return (Path(__file__).parent / "demo.html").read_text(encoding="utf-8")


def _completed_response(result: dict) -> dict:
    """Khối phản hồi khi đã ra quyết định (dùng chung cho /assess và /sessions)."""
    return {
        "status": "completed",
        "decision": result["decision"],
        "affordability": result.get("affordability"),
        "transparency_notice": build_notice(result),
        "policy_citations": (result.get("policy") or {}).get("citations", []),
    }


@app.post("/assess", dependencies=[Depends(require_api_key)])
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


class ConsentDecision(BaseModel):
    agreed: bool


def _consent_ok(sess: dict) -> bool:
    c = sess.get("consent")
    return bool(c and c.get("agreed"))


@app.post("/sessions", dependencies=[Depends(require_api_key)])
def start_session() -> dict:
    """Mở phiên mới. CHƯA thu thập dữ liệu — trả bản đồng ý để khách xác nhận trước."""
    sid = _session_store().create()
    return {
        "session_id": sid,
        "status": "consent_required",
        "consent_notice": build_consent_notice(),
    }


@app.post("/sessions/{session_id}/consent", dependencies=[Depends(require_api_key)])
def session_consent(session_id: str, decision: ConsentDecision) -> dict:
    """Ghi nhận đồng ý/từ chối xử lý dữ liệu (NĐ356 Đ.6) TRƯỚC khi hỏi field nào.

    Đồng ý → mở khóa intake + audit `consent_given`. Từ chối → phiên khóa, không xử lý.
    """
    store = _session_store()
    sess = store.get(session_id)
    if sess is None:
        raise HTTPException(status_code=404, detail="session không tồn tại")

    notice = build_consent_notice()
    store.set_consent(
        session_id,
        {
            "agreed": decision.agreed,
            "version": notice["version"],
            "at": datetime.now(timezone.utc).isoformat(),
        },
    )
    _audit().record(
        "consent_given" if decision.agreed else "consent_declined",
        subject=f"sess_{session_id}",
        consent_version=notice["version"],
        agreed=decision.agreed,
    )
    if not decision.agreed:
        return {
            "session_id": session_id,
            "status": "consent_declined",
            "thong_bao": "Bạn đã từ chối. Hệ thống sẽ không xử lý hồ sơ của bạn.",
        }
    missing = LoanApplication().missing_required_fields()
    return {
        "session_id": session_id,
        "status": "incomplete",
        "consent_recorded": True,
        "missing_required_fields": missing,
        "next_question": _next_question(missing),
    }


@app.post("/sessions/{session_id}/withdraw", dependencies=[Depends(require_api_key)])
def session_withdraw(session_id: str) -> dict:
    """Khách rút lại đồng ý (NĐ356 Đ.6) → khóa lại xử lý. KHÔNG hồi tố phần đã xử lý."""
    store = _session_store()
    sess = store.get(session_id)
    if sess is None:
        raise HTTPException(status_code=404, detail="session không tồn tại")
    store.set_consent(
        session_id,
        {
            "agreed": False,
            "version": build_consent_notice()["version"],
            "withdrawn_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    _audit().record("consent_withdrawn", subject=f"sess_{session_id}")
    return {
        "session_id": session_id,
        "status": "consent_withdrawn",
        "thong_bao": "Đã rút lại đồng ý. Hệ thống dừng xử lý (không hồi tố phần đã xử lý).",
    }


@app.post("/sessions/{session_id}/review-request", dependencies=[Depends(require_api_key)])
def session_review_request(session_id: str) -> dict:
    """Khách yêu cầu nhân viên xét duyệt lại quyết định tự động (quyền ở transparency notice).

    Ghi nhận yêu cầu (audit + nhật ký phiên). Định tuyến tới hàng đợi xét duyệt của nhân
    viên là việc vận hành Vapp (open-questions T3) — ngoài phạm vi code hiện tại.
    """
    store = _session_store()
    sess = store.get(session_id)
    if sess is None:
        raise HTTPException(status_code=404, detail="session không tồn tại")
    messages = sess["messages"]
    messages.append(
        {"role": "system", "content": "Khách yêu cầu nhân viên xét duyệt lại quyết định."}
    )
    store.save(session_id, sess["application"], messages)
    _audit().record("human_review_requested", subject=f"sess_{session_id}")
    return {
        "session_id": session_id,
        "status": "human_review_requested",
        "thong_bao": "Đã ghi nhận yêu cầu xét duyệt thủ công. Nhân viên sẽ xem lại hồ sơ của bạn.",
    }


@app.post("/sessions/{session_id}/message", dependencies=[Depends(require_api_key)])
def session_message(session_id: str, patch: LoanApplication) -> dict:
    """Gửi thêm thông tin cho phiên → merge vào hồ sơ dở, hỏi tiếp hoặc ra quyết định.

    `patch` là LoanApplication một phần (mọi field optional); chỉ field khác None được
    ghi đè. Offline gửi field có cấu trúc; có OpenAI thật sẽ trích từ câu chữ tự do.
    """
    store = _session_store()
    sess = store.get(session_id)
    if sess is None:
        raise HTTPException(status_code=404, detail="session không tồn tại")
    if not _consent_ok(sess):
        raise HTTPException(
            status_code=403,
            detail="Cần đồng ý xử lý dữ liệu trước (POST /sessions/{id}/consent).",
        )

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
    result = run_assessment(graph, merged, audit, consent=True)
    return {"session_id": session_id, **_completed_response(result)}


@app.get("/sessions/{session_id}", dependencies=[Depends(require_api_key)])
def get_session(session_id: str) -> dict:
    """Xem lại phiên (nối phiên: thoát ra rồi vào lại vẫn còn hồ sơ dở)."""
    store = _session_store()
    sess = store.get(session_id)
    if sess is None:
        raise HTTPException(status_code=404, detail="session không tồn tại")
    missing = LoanApplication.model_validate(sess["application"]).missing_required_fields()
    if not _consent_ok(sess):
        status = "consent_required"
    else:
        status = "ready" if not missing else "incomplete"
    return {
        "session_id": session_id,
        "status": status,
        "consent": sess.get("consent"),
        "application": sess["application"],
        "messages": sess["messages"],
        "missing_required_fields": missing,
    }
