"""Decision Gate xác định (backstop) — ADR-0022, docs/risk-model.md.

Kết hợp knock-out + điểm số + khuyến nghị tranh luận dưới LUẬT BẤT ĐỐI XỨNG:
tranh luận chỉ làm CHẶT hơn (đẩy Review/Từ chối), KHÔNG tự duyệt.
"""

from __future__ import annotations

from ..schemas import (
    Decision,
    DecisionOutcome,
    Deliberation,
    PolicyResult,
    RiskResult,
)


def decide(
    risk: RiskResult,
    policy: PolicyResult,
    deliberation: Deliberation,
    table: dict,
) -> Decision:
    """Quyết định cuối (deterministic). Degrade an toàn: không nhánh nào tự duyệt khi rủi ro."""
    bands = table["score_bands"]
    flags_map = table["blocking_flags"]

    # 1. Knock-out là điều kiện cứng.
    if risk.knocked_out:
        return Decision(
            outcome=DecisionOutcome.reject,
            reasons=["Loại thẳng (knock-out)", *risk.knockout_reasons],
        )

    # 2. Vi phạm chính sách cứng.
    if not policy.compliant:
        return Decision(
            outcome=DecisionOutcome.reject,
            reasons=["Không thỏa điều kiện chính sách", *policy.violations],
        )

    # 3. Cờ rủi ro chặn từ tranh luận — chỉ làm chặt hơn.
    for flag in deliberation.blocking_flags:
        if flags_map.get(flag) == "reject":
            return Decision(
                outcome=DecisionOutcome.reject,
                reasons=[f"Cờ rủi ro nghiêm trọng: {flag}"],
            )
    review_flags = [
        f for f in deliberation.blocking_flags if flags_map.get(f) == "review"
    ]

    # 4. Duyệt cần hội đủ: điểm đạt + sạch chính sách + KHÔNG cờ rủi ro nào.
    if (
        risk.score >= bands["approve_min"]
        and policy.compliant
        and not deliberation.blocking_flags
    ):
        return Decision(
            outcome=DecisionOutcome.approve,
            reasons=["Điểm đạt ngưỡng, thỏa chính sách, không cờ rủi ro"],
        )

    # 5. Điểm quá thấp -> từ chối.
    if risk.score < bands["review_min"]:
        return Decision(
            outcome=DecisionOutcome.reject,
            reasons=["Điểm dưới ngưỡng tối thiểu", *risk.factors],
        )

    # 6. Còn lại -> cần xét duyệt thủ công.
    return Decision(
        outcome=DecisionOutcome.review,
        reasons=["Cần xét duyệt thủ công", *review_flags, *risk.factors],
    )
