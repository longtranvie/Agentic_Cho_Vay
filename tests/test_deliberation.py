from loan_agent.agents.deliberation import convene_check, run_deliberation
from loan_agent.config import load_decision_table
from loan_agent.schemas import (
    AgentTurn,
    JudgeVerdict,
    LoanApplication,
    PolicyResult,
    Recommendation,
    RiskResult,
)

TABLE = load_decision_table()

APP = LoanApplication.model_validate(
    {
        "loan": {"amount": 50_000_000, "purpose": "mua xe", "term_months": 24},
        "income": {"monthly": 30_000_000, "source": "luong", "stability": "on_dinh"},
        "debt": {"total": 0, "monthly_payment": 0},
        "profile": {"age": 32, "occupation": "ky su", "tenure_years": 5},
        "credit_history": {"had_late_payment": False},
    }
)


class _NoisyLLM:
    """Giả lập LLM thật 'ồn ào': judge trả 1 cờ hợp lệ + 2 cờ bịa ngoài danh sách."""

    def complete(self, prompt: str) -> str:
        return ""

    def structured(self, prompt: str, schema):
        if schema is AgentTurn:
            return AgentTurn(role="Skeptic", stance="lean_reject")
        return JudgeVerdict(
            recommendation="lean_review",
            blocking_flags=["fraud_signal", "Thiếu bằng chứng từ bên B", "abc"],
        )


def _mid_risk():  # điểm vùng giữa -> convene "full"
    return RiskResult(score=55, band="medium", dti=0.4)


def test_convene_full_for_mid_score():
    assert convene_check(_mid_risk(), PolicyResult(compliant=True), TABLE) == "full"


def test_blocking_flags_filtered_to_known_keys():
    delib = run_deliberation(_mid_risk(), PolicyResult(compliant=True), _NoisyLLM(), TABLE, APP)
    assert delib.blocking_flags == ["fraud_signal"]  # cờ bịa bị loại


def test_recommendation_is_valid_enum_value():
    delib = run_deliberation(_mid_risk(), PolicyResult(compliant=True), _NoisyLLM(), TABLE, APP)
    assert delib.recommendation in set(Recommendation)
