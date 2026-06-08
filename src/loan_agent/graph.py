"""Xây dựng LangGraph: nodes + conditional edges — ADR-0001/0021/0023.

Luồng: bootstrap → intake → affordability → pre_checks → (knock-out? gate :
deliberation) → decision_gate → (review? review_prep : finalize) → END.
"""

from __future__ import annotations

from functools import partial

from langgraph.graph import END, START, StateGraph

from . import nodes
from .state import LoanState


def _route_intake(state: dict):
    return "affordability" if state.get("meta", {}).get("intake_ready") else END


def _route_prechecks(state: dict):
    return "decision_gate" if state["risk"]["knocked_out"] else "deliberation"


def _route_decision(state: dict):
    return "review_prep" if state["decision"]["outcome"] == "review" else "finalize"


def build_graph(llm, store, table, *, max_turns: int = 12, checkpointer=None):
    g = StateGraph(LoanState)

    g.add_node("bootstrap", nodes.bootstrap)
    g.add_node("intake", partial(nodes.intake, llm=llm, max_turns=max_turns))
    g.add_node("affordability", partial(nodes.affordability, table=table))
    g.add_node("pre_checks", partial(nodes.pre_checks, table=table))
    g.add_node(
        "deliberation",
        partial(nodes.deliberation, llm=llm, policy_store=store, table=table),
    )
    g.add_node("decision_gate", partial(nodes.decision_gate, table=table))
    g.add_node("review_prep", nodes.review_prep)
    g.add_node("finalize", nodes.finalize)

    g.add_edge(START, "bootstrap")
    g.add_edge("bootstrap", "intake")
    g.add_conditional_edges(
        "intake", _route_intake, {"affordability": "affordability", END: END}
    )
    g.add_edge("affordability", "pre_checks")
    g.add_conditional_edges(
        "pre_checks",
        _route_prechecks,
        {"decision_gate": "decision_gate", "deliberation": "deliberation"},
    )
    g.add_edge("deliberation", "decision_gate")
    g.add_conditional_edges(
        "decision_gate",
        _route_decision,
        {"review_prep": "review_prep", "finalize": "finalize"},
    )
    g.add_edge("review_prep", "finalize")
    g.add_edge("finalize", END)

    return g.compile(checkpointer=checkpointer)
