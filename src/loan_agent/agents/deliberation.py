"""Hội đồng tranh luận — ADR-0021/0023, docs/debate-protocol.md.

convene_check (deterministic) → vòng phát biểu/phản biện (mock/openai) → Judge tổng
hợp. Tranh luận chỉ PHÂN TÍCH; outcome do Decision Gate. Mock không tự raise cờ.
"""

from __future__ import annotations

from ..schemas import (
    AgentTurn,
    Deliberation,
    JudgeVerdict,
    PolicyResult,
    RiskResult,
)

_ROLES_FULL = ["Risk Analyst", "Advocate", "Skeptic", "Policy"]
_ROLES_LIGHT = ["Skeptic"]


def convene_check(risk: RiskResult, policy: PolicyResult, table: dict) -> str:
    """Quyết định có họp hội đồng không: skip | light | full (ADR-0023)."""
    conv = table["convene"]
    bands = table["score_bands"]
    if risk.knocked_out:
        return "skip"
    if risk.score >= conv["clear_approve_min"] and policy.compliant:
        return "light"
    if risk.score < bands["review_min"]:
        return "skip"
    return "full"


def run_deliberation(
    risk: RiskResult, policy: PolicyResult, llm, table: dict
) -> Deliberation:
    mode = convene_check(risk, policy, table)
    if mode == "skip":
        rec = (
            "lean_reject"
            if risk.score < table["score_bands"]["review_min"]
            else "lean_approve"
        )
        return Deliberation(convened="skip", recommendation=rec, blocking_flags=[])

    roles = _ROLES_LIGHT if mode == "light" else _ROLES_FULL
    transcript: list[dict] = []
    for role in roles:
        context = (
            f"Bạn là {role}. Điểm rủi ro {risk.score}, DTI {risk.dti:.2f}. "
            f"Phân tích hồ sơ và nêu quan điểm."
        )
        transcript.append(llm.structured(context, AgentTurn).model_dump())

    verdict = llm.structured(
        f"Bạn là Judge. Tổng hợp tranh luận, điểm {risk.score}. Cho khuyến nghị + cờ rủi ro.",
        JudgeVerdict,
    )
    return Deliberation(
        convened=mode,
        transcript=transcript,
        recommendation=verdict.recommendation,
        confidence=verdict.confidence,
        blocking_flags=verdict.blocking_flags,
    )
