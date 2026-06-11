"""Hội đồng tranh luận — ADR-0021/0023, docs/debate-protocol.md.

convene_check (deterministic) → vòng phát biểu/phản biện (mock/openai) → Judge tổng
hợp. Tranh luận chỉ PHÂN TÍCH; outcome do Decision Gate. Cờ rủi ro CHỈ nhận từ tập
khóa cấu hình (decision_table["blocking_flags"]) — cờ ngoài danh sách bị loại.
"""

from __future__ import annotations

from ..schemas import (
    AgentTurn,
    Deliberation,
    JudgeVerdict,
    LoanApplication,
    PolicyResult,
    Recommendation,
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


def _case_brief(app: LoanApplication, risk: RiskResult) -> str:
    return (
        f"Khoản vay {app.loan.amount:,.0f}đ, kỳ hạn {app.loan.term_months} tháng, "
        f"mục đích '{app.loan.purpose}'. Thu nhập {app.income.monthly:,.0f}đ/tháng, "
        f"trả nợ hiện tại {app.debt.monthly_payment or 0:,.0f}đ/tháng. "
        f"Điểm rủi ro {risk.score}/100, DTI {risk.dti:.2f}, band '{risk.band}'."
    )


def _format_citations(policy: PolicyResult) -> str:
    if not policy.citations:
        return "(không có trích dẫn chính sách)"
    return "\n".join(
        f"- [{c.source}] {c.dieu or ''}: {c.snippet}" for c in policy.citations
    )


def _format_transcript(transcript: list[dict]) -> str:
    """Render các lượt đã phát biểu để đưa vào prompt agent sau / Judge (tạo tương tác)."""
    if not transcript:
        return "(chưa có ai phát biểu)"
    return "\n".join(
        f"- {t.get('role')} ({t.get('stance')}): {'; '.join(t.get('arguments', []))}"
        for t in transcript
    )


def run_deliberation(
    risk: RiskResult,
    policy: PolicyResult,
    llm,
    table: dict,
    app: LoanApplication,
    rounds: int = 1,
) -> Deliberation:
    mode = convene_check(risk, policy, table)
    if mode == "skip":
        rec = (
            Recommendation.lean_reject
            if risk.score < table["score_bands"]["review_min"]
            else Recommendation.lean_approve
        )
        return Deliberation(convened="skip", recommendation=rec, blocking_flags=[])

    brief = _case_brief(app, risk)
    cites = _format_citations(policy)
    roles = _ROLES_LIGHT if mode == "light" else _ROLES_FULL
    transcript: list[dict] = []
    # Mỗi agent ĐỌC các lượt trước (transcript) → phản biện nhau. Nhiều vòng = tranh luận sâu hơn.
    for _ in range(max(1, rounds)):
        for role in roles:
            prompt = (
                f"Bạn là {role} trong HỘI ĐỒNG THẨM ĐỊNH KHOẢN VAY.\n"
                f"Hồ sơ: {brief}\n"
                f"Chính sách liên quan:\n{cites}\n"
                f"Các phát biểu trước trong hội đồng:\n{_format_transcript(transcript)}\n"
                f"Nêu quan điểm (stance: lean_approve / neutral / lean_reject) và lập luận "
                f"ngắn, BÁM dữ liệu hồ sơ và chính sách. Nếu KHÔNG đồng ý với phát biểu nào "
                f"ở trên, PHẢN BIỆN cụ thể (điền rebuttals)."
            )
            transcript.append(llm.structured(prompt, AgentTurn).model_dump(mode="json"))

    allowed = ", ".join(table["blocking_flags"].keys())
    verdict_prompt = (
        f"Bạn là Judge tổng hợp HỘI ĐỒNG THẨM ĐỊNH KHOẢN VAY.\n"
        f"Hồ sơ: {brief}\n"
        f"Toàn bộ tranh luận của hội đồng:\n{_format_transcript(transcript)}\n"
        f"TỔNG HỢP các lập luận trên thành khuyến nghị (recommendation: lean_approve / "
        f"lean_review / lean_reject). CHỈ nêu cờ rủi ro (blocking_flags) NẾU thực sự có vấn "
        f"đề, và phải chọn TRONG danh sách: [{allowed}]. TUYỆT ĐỐI không tạo cờ ngoài danh "
        f"sách; không có thì để rỗng."
    )
    verdict = llm.structured(verdict_prompt, JudgeVerdict)
    # Lọc cờ: chỉ giữ cờ thuộc bảng cấu hình (LLM thật có thể bịa cờ ngoài danh sách).
    flags = [f for f in verdict.blocking_flags if f in table["blocking_flags"]]
    return Deliberation(
        convened=mode,
        transcript=transcript,
        recommendation=verdict.recommendation,
        confidence=verdict.confidence,
        blocking_flags=flags,
    )
