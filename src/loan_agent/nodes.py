"""Hàm node cho graph — docs/architecture.md §2.

Mỗi node nhận state, trả patch dict. Phần phụ thuộc (llm/store/table) được bind
bằng functools.partial trong graph.py.
"""

from __future__ import annotations

from .agents.deliberation import run_deliberation
from .agents.intake import extract_and_ask
from .rules.gate import decide
from .rules.scorecard import compute_risk
from .schemas import (
    Affordability,
    Deliberation,
    LoanApplication,
    PolicyResult,
    RiskResult,
)
from .tools.financial import max_affordable_principal


def bootstrap(state: dict) -> dict:
    """Nạp dữ liệu Vapp (prod). Slice: no-op."""
    return {}


def intake(state: dict, *, llm, max_turns: int) -> dict:
    return extract_and_ask(
        state.get("application"),
        state.get("messages", []),
        state.get("meta", {}),
        llm,
        max_turns,
    )


def affordability(state: dict, *, table: dict) -> dict:
    app = LoanApplication.model_validate(state["application"])
    rate = table["interest_rate"]["annual"]
    ceiling = table["knockout"]["dti_abs_max"]
    max_p = max_affordable_principal(
        app.income.monthly,
        app.debt.monthly_payment or 0.0,
        rate,
        app.loan.term_months,
        ceiling,
    )
    requested = app.loan.amount
    within = requested <= max_p
    aff = Affordability(
        max_principal=round(max_p, 2),
        requested_amount=requested,
        within_limit=within,
        counter_offer_amount=None if within else round(max_p, 2),
    )
    return {"affordability": aff.model_dump()}


def pre_checks(state: dict, *, table: dict) -> dict:
    app = LoanApplication.model_validate(state["application"])
    return {"risk": compute_risk(app, table).model_dump()}


def deliberation(state: dict, *, llm, policy_store, table: dict) -> dict:
    # 'policy_store' (không phải 'store') vì LangGraph reserve tên tham số 'store'.
    risk = RiskResult(**state["risk"])
    app = LoanApplication.model_validate(state["application"])
    # Truy vấn theo khía cạnh chính sách (điều kiện vay/lãi suất) + mục đích vay —
    # không chỉ mục đích, vì mục đích đơn lẻ ("mua xe") không khớp văn bản luật.
    query = f"điều kiện vay vốn lãi suất {app.loan.purpose or ''}".strip()
    citations = policy_store.retrieve(query, k=3)
    policy = PolicyResult(compliant=True, citations=citations)
    delib = run_deliberation(risk, policy, llm, table, app)
    return {
        "deliberation": delib.model_dump(mode="json"),
        "policy": policy.model_dump(mode="json"),
    }


def decision_gate(state: dict, *, table: dict) -> dict:
    risk = RiskResult(**state["risk"])
    policy = PolicyResult(**(state.get("policy") or {"compliant": True}))
    delib = Deliberation(**(state.get("deliberation") or {}))
    return {"decision": decide(risk, policy, delib, table).model_dump(mode="json")}


def review_prep(state: dict) -> dict:
    """Ca Review: tạo case (prod: interrupt + hàng đợi nhân viên — ADR-0012)."""
    return {"case": {"id": "CASE-LOCAL", "status": "queued"}}


def finalize(state: dict) -> dict:
    meta = dict(state.get("meta") or {})
    meta["done"] = True
    return {"meta": meta}
