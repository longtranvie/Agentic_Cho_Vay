"""FastAPI skeleton bọc pipeline thẩm định — ADR-0017 (hợp đồng API).

⚠️ SKELETON: đường dẫn + schema request/response có thể đổi theo hợp đồng API thật với
Vapp (open-questions T1). Chạy dev:
    uvicorn loan_agent.api.app:app --reload     (PYTHONPATH=src)
Tài liệu tự sinh tại /docs.
"""

from __future__ import annotations

from fastapi import FastAPI

from ..compliance.audit import AuditLog
from ..compliance.transparency import build_notice
from ..config import load_decision_table, settings
from ..graph import build_graph
from ..llm.factory import get_llm
from ..rag.factory import get_store
from ..schemas import LoanApplication
from ..service import run_assessment

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


@app.post("/assess")
def assess(application: LoanApplication) -> dict:
    """Thẩm định 1 hồ sơ ĐỦ field. Thiếu field core → trả danh sách thiếu (để hỏi tiếp).

    Hội thoại intake nhiều lượt sẽ thêm sau khi chốt T1 (cần lưu phiên — Postgres).
    """
    missing = application.missing_required_fields()
    if missing:
        return {"status": "incomplete", "missing_required_fields": missing}

    graph, audit = _engine()
    result = run_assessment(graph, application.model_dump(mode="json"), audit)
    return {
        "status": "completed",
        "decision": result["decision"],
        "affordability": result.get("affordability"),
        "transparency_notice": build_notice(result),
        "policy_citations": (result.get("policy") or {}).get("citations", []),
    }
