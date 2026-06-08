from loan_agent.schemas import Decision, DecisionOutcome, LoanApplication

SAMPLE = {
    "loan": {"amount": 10_000_000, "purpose": "mua xe", "term_months": 12},
    "income": {"monthly": 20_000_000, "source": "luong", "stability": "on_dinh"},
    "debt": {"total": 0, "monthly_payment": 0},
    "profile": {"age": 30, "occupation": "ke_toan", "tenure_years": 3},
    "credit_history": {"had_late_payment": False},
}


def test_missing_required_fields_detects_empty():
    app = LoanApplication()
    assert "loan.amount" in app.missing_required_fields()
    assert not app.is_complete()


def test_complete_application_is_complete():
    app = LoanApplication.model_validate(SAMPLE)
    assert app.is_complete()
    assert app.missing_required_fields() == []


def test_decision_outcome_compares_to_string():
    d = Decision(outcome=DecisionOutcome.approve)
    assert d.outcome == "approve"
