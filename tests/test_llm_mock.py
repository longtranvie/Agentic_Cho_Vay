from loan_agent.llm.mock import MockLLM
from loan_agent.schemas import AgentTurn, JudgeVerdict


def test_mock_agentturn_skeptic_leans_reject():
    t = MockLLM().structured("Bạn là Skeptic, hãy phản biện", AgentTurn)
    assert isinstance(t, AgentTurn)
    assert t.stance == "lean_reject"


def test_mock_agentturn_advocate_leans_approve():
    t = MockLLM().structured("Bạn là Advocate", AgentTurn)
    assert t.stance == "lean_approve"


def test_mock_deterministic():
    a = MockLLM().structured("Advocate", AgentTurn).model_dump()
    b = MockLLM().structured("Advocate", AgentTurn).model_dump()
    assert a == b


def test_mock_no_blocking_flags():
    t = MockLLM().structured("Skeptic", AgentTurn)
    assert t.flags_raised == []


def test_mock_judge_defaults():
    v = MockLLM().structured("Judge tổng hợp", JudgeVerdict)
    assert v.blocking_flags == []
