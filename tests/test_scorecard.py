from loan_agent.config import load_decision_table
from loan_agent.rules.scorecard import compute_risk
from loan_agent.schemas import LoanApplication

TABLE = load_decision_table()

BASE = {
    "loan": {"amount": 10_000_000, "purpose": "mua xe", "term_months": 12},
    "income": {"monthly": 20_000_000, "source": "luong", "stability": "on_dinh"},
    "debt": {"total": 0, "monthly_payment": 0},
    "profile": {"age": 30, "occupation": "ke_toan", "tenure_years": 3},
    "credit_history": {"had_late_payment": False},
}


def make_app(**overrides):
    data = {k: dict(v) for k, v in BASE.items()}
    for dotted, value in overrides.items():
        section, field = dotted.split(".")
        data[section][field] = value
    return LoanApplication.model_validate(data)


def test_knockout_underage():
    r = compute_risk(make_app(**{"profile.age": 17}), TABLE)
    assert r.knocked_out is True


def test_good_profile_high_score_not_knocked_out():
    r = compute_risk(make_app(), TABLE)
    assert not r.knocked_out
    assert r.score >= 70
    assert r.band == "low"


def test_late_payment_and_unstable_lowers_score():
    good = compute_risk(make_app(), TABLE).score
    risky = compute_risk(
        make_app(
            **{
                "credit_history.had_late_payment": True,
                "income.stability": "khong_on_dinh",
            }
        ),
        TABLE,
    ).score
    assert risky < good


def test_high_dti_knocked_out():
    # vay rất lớn so với thu nhập -> DTI vượt trần tuyệt đối
    r = compute_risk(
        make_app(**{"loan.amount": 500_000_000, "loan.term_months": 6}), TABLE
    )
    assert r.knocked_out is True


def test_knockout_forbidden_purpose():
    # mục đích bị cấm (Điều 8) — không dấu vẫn khớp config có dấu ("vàng miếng")
    r = compute_risk(make_app(**{"loan.purpose": "mua vang mieng"}), TABLE)
    assert r.knocked_out is True
    assert any("cấm" in reason for reason in r.knockout_reasons)
