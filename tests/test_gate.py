from loan_agent.config import load_decision_table
from loan_agent.rules.gate import decide
from loan_agent.schemas import Deliberation, PolicyResult, RiskResult

TABLE = load_decision_table()


def risk(knocked_out=False, band="low", score=80, factors=None):
    return RiskResult(
        knocked_out=knocked_out, band=band, score=score, factors=factors or []
    )


def policy_ok():
    return PolicyResult(compliant=True)


def policy_bad():
    return PolicyResult(compliant=False, violations=["Vượt hạn mức sản phẩm"])


def delib_ok():
    return Deliberation(blocking_flags=[])


def delib(flags):
    return Deliberation(blocking_flags=flags)


def test_knockout_rejects():
    d = decide(risk(knocked_out=True), policy_ok(), delib_ok(), TABLE)
    assert d.outcome == "reject"


def test_policy_violation_rejects():
    d = decide(risk(score=80), policy_bad(), delib_ok(), TABLE)
    assert d.outcome == "reject"


def test_reject_flag_rejects_even_high_score():
    d = decide(risk(score=90), policy_ok(), delib(["fraud_signal"]), TABLE)
    assert d.outcome == "reject"


def test_blocking_flag_downgrades_to_review():
    d = decide(risk(score=80), policy_ok(), delib(["affordability_borderline"]), TABLE)
    assert d.outcome == "review"


def test_clean_high_score_approves():
    d = decide(risk(score=80), policy_ok(), delib_ok(), TABLE)
    assert d.outcome == "approve"


def test_mid_score_reviews():
    d = decide(risk(band="medium", score=55), policy_ok(), delib_ok(), TABLE)
    assert d.outcome == "review"


def test_low_score_rejects():
    d = decide(risk(band="high", score=20), policy_ok(), delib_ok(), TABLE)
    assert d.outcome == "reject"
