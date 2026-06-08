import math

from loan_agent.tools.financial import (
    debt_to_income,
    loan_to_annual_income,
    max_affordable_principal,
    monthly_payment,
)


def test_monthly_payment_zero_rate():
    assert monthly_payment(1_200_000, 0.0, 12) == 100_000


def test_monthly_payment_annuity():
    p = monthly_payment(10_000_000, 0.12, 12)
    assert math.isclose(p, 888_487.9, rel_tol=1e-3)


def test_monthly_payment_invalid_term():
    try:
        monthly_payment(1_000_000, 0.1, 0)
        assert False, "phải raise ValueError"
    except ValueError:
        pass


def test_dti_basic():
    assert math.isclose(debt_to_income(20_000_000, 2_000_000, 3_000_000), 0.25)


def test_dti_zero_income_is_inf():
    assert debt_to_income(0, 0, 100) == float("inf")


def test_lti():
    assert math.isclose(loan_to_annual_income(24_000_000, 2_000_000), 1.0)


def test_lti_zero_income_is_inf():
    assert loan_to_annual_income(1_000_000, 0) == float("inf")


def test_max_affordable_inverse():
    principal = max_affordable_principal(20_000_000, 0, 0.18, 12, dti_target=0.4)
    p = monthly_payment(principal, 0.18, 12)
    assert math.isclose(p, 8_000_000, rel_tol=1e-6)


def test_max_affordable_zero_when_overburdened():
    # nghĩa vụ hiện tại đã vượt ngưỡng -> hạn mức 0
    assert max_affordable_principal(10_000_000, 9_000_000, 0.18, 12, 0.4) == 0.0
