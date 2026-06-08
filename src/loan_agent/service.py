"""Điều phối thẩm định dùng chung cho CLI và API + ghi nhật ký xử lý (NĐ356).

Tách khỏi cli.py để API tái dùng đúng một luồng (không trùng logic audit/cross-border).
"""

from __future__ import annotations

from .compliance.audit import AuditLog, subject_ref
from .config import settings


def run_assessment(graph, application: dict, audit: AuditLog) -> dict:
    """Chạy pipeline thẩm định cho 1 hồ sơ + ghi nhật ký xử lý dữ liệu cá nhân."""
    subj = subject_ref(application)
    audit.record(
        "processing_started",
        subject=subj,
        purpose="tham_dinh_vay",
        data_categories=sorted(application.keys()),
    )
    result = graph.invoke({"application": application, "messages": [], "meta": {}})
    delib = result.get("deliberation") or {}
    if settings.llm_provider == "openai" and delib.get("convened") not in (None, "skip"):
        audit.record(
            "cross_border_transfer",
            subject=subj,
            recipient="OpenAI",
            data="anonymized",
            basis="consent+impact_assessment+DPA",
        )
    audit.record(
        "automated_decision",
        subject=subj,
        outcome=result.get("decision", {}).get("outcome"),
    )
    return result
