"""Schema dữ liệu trao đổi giữa các bước (Pydantic) — ADR-0007.

Nguyên tắc: schema là VẬT CHỨA dữ liệu (permissive). Ngưỡng nghiệp vụ (tuổi, thu
nhập tối thiểu, DTI...) nằm ở lớp knock-out đọc config (ADR-0014), KHÔNG hardcode
constraint vào schema — để knock-out làm đúng việc của nó. Xem docs/data-schema.md.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# --- Enums ---------------------------------------------------------------


class IncomeSource(str, Enum):
    luong = "luong"
    kinh_doanh = "kinh_doanh"
    khac = "khac"


class IncomeStability(str, Enum):
    on_dinh = "on_dinh"
    khong_on_dinh = "khong_on_dinh"


class DecisionOutcome(str, Enum):
    approve = "approve"
    reject = "reject"
    review = "review"


# --- Hồ sơ vay (slot-filling) -------------------------------------------


class Loan(BaseModel):
    amount: Optional[float] = None
    purpose: Optional[str] = None
    term_months: Optional[int] = None


class Income(BaseModel):
    monthly: Optional[float] = None
    source: Optional[IncomeSource] = None
    stability: Optional[IncomeStability] = None


class Debt(BaseModel):
    total: Optional[float] = None
    monthly_payment: Optional[float] = None


class Profile(BaseModel):
    age: Optional[int] = None
    occupation: Optional[str] = None
    tenure_years: Optional[float] = None


class CreditHistory(BaseModel):
    had_late_payment: Optional[bool] = None


class LoanApplication(BaseModel):
    """Hồ sơ vay được lấp đầy dần qua hội thoại intake (ADR-0003)."""

    loan: Loan = Field(default_factory=Loan)
    income: Income = Field(default_factory=Income)
    debt: Debt = Field(default_factory=Debt)
    profile: Profile = Field(default_factory=Profile)
    credit_history: CreditHistory = Field(default_factory=CreditHistory)

    def missing_required_fields(self) -> list[str]:
        """Trường core còn thiếu (data-schema.md §1)."""
        required = {
            "loan.amount": self.loan.amount,
            "loan.purpose": self.loan.purpose,
            "loan.term_months": self.loan.term_months,
            "income.monthly": self.income.monthly,
            "income.source": self.income.source,
            "income.stability": self.income.stability,
            "debt.total": self.debt.total,
            "debt.monthly_payment": self.debt.monthly_payment,
            "profile.age": self.profile.age,
            "profile.occupation": self.profile.occupation,
            "profile.tenure_years": self.profile.tenure_years,
            "credit_history.had_late_payment": self.credit_history.had_late_payment,
        }
        return [k for k, v in required.items() if v is None]

    def is_complete(self) -> bool:
        return not self.missing_required_fields()


# --- Kết quả các bước ----------------------------------------------------


class Affordability(BaseModel):
    """Hạn mức tối đa + counter-offer (ADR-0010). Ước tính, không phải quyết định."""

    max_principal: float = 0.0
    requested_amount: float = 0.0
    within_limit: bool = True
    counter_offer_amount: Optional[float] = None


class RiskResult(BaseModel):
    """Knock-out + scorecard (ADR-0014). Số do code, không do LLM."""

    knocked_out: bool = False
    knockout_reasons: list[str] = Field(default_factory=list)
    dti: float = 0.0
    new_monthly_payment: float = 0.0
    loan_to_annual_income: float = 0.0
    capacity_score: int = 0
    willingness_score: int = 0
    score: int = 0
    band: str = ""  # low | medium | high (rủi ro)
    factors: list[str] = Field(default_factory=list)


class PolicyCitation(BaseModel):
    source: str
    snippet: str
    dieu: Optional[str] = None


class PolicyResult(BaseModel):
    """Đối chiếu chính sách (ADR-0016). Điều kiện cứng ở config; RAG để trích dẫn."""

    compliant: bool = True
    violations: list[str] = Field(default_factory=list)
    citations: list[PolicyCitation] = Field(default_factory=list)


class AgentTurn(BaseModel):
    """Một lượt phát biểu của agent trong hội đồng (debate-protocol.md §4)."""

    role: str
    stance: str = "neutral"  # lean_approve | neutral | lean_reject
    arguments: list[str] = Field(default_factory=list)
    flags_raised: list[str] = Field(default_factory=list)
    rebuttals: list[str] = Field(default_factory=list)


class Deliberation(BaseModel):
    """Kết quả hội đồng tranh luận (ADR-0021/0023). Chỉ phân tích, không tự quyết."""

    convened: str = "skip"  # skip | light | full
    transcript: list[dict] = Field(default_factory=list)
    recommendation: str = ""  # lean_approve | lean_review | lean_reject
    confidence: str = "medium"
    blocking_flags: list[str] = Field(default_factory=list)


class JudgeVerdict(BaseModel):
    """Moderator/Judge tổng hợp (debate-protocol.md §5). Không tự chốt outcome."""

    recommendation: str = "lean_review"  # lean_approve | lean_review | lean_reject
    confidence: str = "medium"
    blocking_flags: list[str] = Field(default_factory=list)


class Decision(BaseModel):
    """Quyết định cuối từ Decision Gate (ADR-0022). Outcome do luật xác định."""

    outcome: DecisionOutcome
    reasons: list[str] = Field(default_factory=list)
    rationale: str = ""
