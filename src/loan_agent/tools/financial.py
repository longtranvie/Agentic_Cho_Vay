"""Phép tính tài chính thuần (deterministic) — ADR-0004, docs/risk-model.md.

Tất cả hàm không gọi mạng/LLM, kiểm thử được. Phần này tính SỐ; quyết định
Duyệt/Từ chối nằm ở rules/ (ADR-0009).
"""

from __future__ import annotations


def monthly_payment(principal: float, annual_rate: float, term_months: int) -> float:
    """Trả góp hàng tháng theo công thức annuity. annual_rate dạng thập phân (0.18)."""
    if term_months <= 0:
        raise ValueError("term_months phải > 0")
    if principal < 0:
        raise ValueError("principal phải >= 0")
    if annual_rate == 0:
        return principal / term_months
    monthly_rate = annual_rate / 12
    factor = (1 + monthly_rate) ** term_months
    return principal * monthly_rate * factor / (factor - 1)


def debt_to_income(
    monthly_income: float, existing_payment: float, new_payment: float
) -> float:
    """DTI sau vay = (nghĩa vụ hiện tại + khoản mới) / thu nhập tháng. Income<=0 -> inf."""
    if monthly_income <= 0:
        return float("inf")
    return (existing_payment + new_payment) / monthly_income


def loan_to_annual_income(loan_amount: float, monthly_income: float) -> float:
    """Tỉ lệ khoản vay / thu nhập một năm. Thu nhập<=0 -> inf."""
    annual_income = monthly_income * 12
    if annual_income <= 0:
        return float("inf")
    return loan_amount / annual_income


def max_affordable_principal(
    monthly_income: float,
    existing_payment: float,
    annual_rate: float,
    term_months: int,
    dti_target: float,
) -> float:
    """Hạn mức gốc tối đa (phép tính ngược) sao cho DTI <= dti_target (ADR-0010)."""
    max_pay = max(0.0, dti_target * monthly_income - existing_payment)
    if max_pay == 0:
        return 0.0
    if annual_rate == 0:
        return max_pay * term_months
    monthly_rate = annual_rate / 12
    return max_pay * (1 - (1 + monthly_rate) ** -term_months) / monthly_rate
