from loan_agent.config import load_decision_table


def test_decision_table_has_required_sections():
    t = load_decision_table()
    for key in [
        "knockout",
        "scorecard",
        "score_bands",
        "interest_rate",
        "convene",
        "blocking_flags",
    ]:
        assert key in t, f"thiếu section {key}"


def test_score_bands_ordered():
    t = load_decision_table()
    assert t["score_bands"]["approve_min"] > t["score_bands"]["review_min"]
