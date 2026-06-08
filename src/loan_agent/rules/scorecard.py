"""Knock-out (loại thẳng) + scorecard chấm điểm — ADR-0014, docs/risk-model.md.

Deterministic, tham số từ decision table (config). Tính 2 chiều: capacity (khả
năng trả) + willingness (thiện chí trả).
"""

from __future__ import annotations

from ..schemas import LoanApplication, RiskResult
from ..tools.financial import (
    debt_to_income,
    loan_to_annual_income,
    monthly_payment,
)


def _lookup_band(value: float, bands: list[list]) -> int:
    """Tra bảng [[ngưỡng, điểm], ...] tăng dần: trả điểm của ngưỡng đầu >= value."""
    for threshold, points in bands:
        if value <= threshold:
            return int(points)
    return int(bands[-1][1])


def _metrics(app: LoanApplication, table: dict) -> tuple[float, float, float]:
    rate = table["interest_rate"]["annual"]
    payment = monthly_payment(app.loan.amount, rate, app.loan.term_months)
    dti = debt_to_income(app.income.monthly, app.debt.monthly_payment or 0.0, payment)
    lti = loan_to_annual_income(app.loan.amount, app.income.monthly)
    return payment, dti, lti


def knock_out(app: LoanApplication, table: dict) -> list[str]:
    """Điều kiện cứng — vi phạm là loại thẳng (đọc config)."""
    ko = table["knockout"]
    reasons: list[str] = []

    age = app.profile.age
    if age is None or age < ko["min_age"] or age > ko["max_age"]:
        reasons.append(f"Tuổi ngoài khoảng [{ko['min_age']}, {ko['max_age']}]")
    if (app.income.monthly or 0) < ko["min_income"]:
        reasons.append("Thu nhập dưới mức tối thiểu")

    max_loan = ko.get("max_loan_amount")
    if max_loan is not None and (app.loan.amount or 0) > max_loan:
        reasons.append(f"Khoản vay vượt trần {max_loan:,.0f}đ")

    _, dti, _ = _metrics(app, table)
    if dti > ko["dti_abs_max"]:
        reasons.append(f"DTI vượt trần tuyệt đối ({dti:.2f} > {ko['dti_abs_max']})")
    return reasons


def compute_risk(app: LoanApplication, table: dict) -> RiskResult:
    """Tính rủi ro: knock-out + scorecard 2 chiều. Yêu cầu hồ sơ đã đủ core fields."""
    assert app.is_complete(), "compute_risk cần hồ sơ đủ core fields"

    payment, dti, lti = _metrics(app, table)
    knockout_reasons = knock_out(app, table)

    sc = table["scorecard"]
    factors: list[str] = []

    # Capacity (khả năng trả)
    capacity = _lookup_band(dti, sc["capacity"]["dti"]) + _lookup_band(
        lti, sc["capacity"]["lti"]
    )
    if dti >= 0.4:
        factors.append(f"DTI cao ({dti:.2f})")
    if lti >= 3:
        factors.append(f"Khoản vay lớn so với thu nhập ({lti:.2f} năm)")

    # Willingness (thiện chí trả)
    w = sc["willingness"]
    late = bool(app.credit_history.had_late_payment)
    willingness = w["late_payment"][str(late).lower()]
    willingness += _lookup_band(app.profile.tenure_years or 0, w["tenure_years"])
    stability = (
        app.income.stability.value if app.income.stability else "khong_on_dinh"
    )
    willingness += w["stability"].get(stability, 0)
    if late:
        factors.append("Có lịch sử trả nợ trễ")
    if stability == "khong_on_dinh":
        factors.append("Thu nhập không ổn định")

    score = capacity + willingness
    bands = table["score_bands"]
    if score >= bands["approve_min"]:
        band = "low"
    elif score >= bands["review_min"]:
        band = "medium"
    else:
        band = "high"

    return RiskResult(
        knocked_out=bool(knockout_reasons),
        knockout_reasons=knockout_reasons,
        dti=dti if dti != float("inf") else 999.0,
        new_monthly_payment=round(payment, 2),
        loan_to_annual_income=lti if lti != float("inf") else 999.0,
        capacity_score=capacity,
        willingness_score=willingness,
        score=score,
        band=band,
        factors=factors,
    )
