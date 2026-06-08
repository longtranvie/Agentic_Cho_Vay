from loan_agent.config import load_decision_table
from loan_agent.graph import build_graph
from loan_agent.llm.mock import MockLLM
from loan_agent.rag.keyword_store import KeywordStore

COMPLETE = {
    "loan": {"amount": 10_000_000, "purpose": "mua xe", "term_months": 12},
    "income": {"monthly": 30_000_000, "source": "luong", "stability": "on_dinh"},
    "debt": {"total": 0, "monthly_payment": 0},
    "profile": {"age": 32, "occupation": "ky su", "tenure_years": 5},
    "credit_history": {"had_late_payment": False},
}


def _graph():
    return build_graph(MockLLM(), KeywordStore([]), load_decision_table())


def test_graph_runs_end_to_end():
    result = _graph().invoke({"application": COMPLETE, "messages": [], "meta": {}})
    assert result["decision"]["outcome"] in {"approve", "reject", "review"}
    assert "risk" in result and "affordability" in result


def test_good_profile_approves():
    result = _graph().invoke({"application": COMPLETE, "messages": [], "meta": {}})
    assert result["decision"]["outcome"] == "approve"


def test_incomplete_application_waits_for_user():
    # thiếu field -> intake chưa ready -> không chạy tới decision
    partial_app = {"loan": {"amount": 10_000_000}}
    result = _graph().invoke({"application": partial_app, "messages": [], "meta": {}})
    assert result.get("meta", {}).get("intake_ready") is False
    assert "decision" not in result
