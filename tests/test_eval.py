"""Gate eval golden set: mọi ca tầng 'high' phải đúng (regression).

Ca needs_expert/known_gap KHÔNG chặn ở đây — chúng được runner báo cáo (eval/run_eval.py).
"""

import os
import tempfile
from pathlib import Path

from loan_agent.compliance.audit import AuditLog
from loan_agent.config import load_decision_table
from loan_agent.eval import evaluate, load_golden, summarize
from loan_agent.graph import build_graph
from loan_agent.llm.mock import MockLLM
from loan_agent.rag.keyword_store import KeywordStore
from loan_agent.service import run_assessment

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "data" / "eval" / "golden_set.json"


def _run():
    graph = build_graph(MockLLM(), KeywordStore([]), load_decision_table())
    audit = AuditLog(os.path.join(tempfile.gettempdir(), "loan_eval_test_audit.jsonl"))
    return evaluate(lambda app: run_assessment(graph, app, audit), load_golden(GOLDEN))


def test_golden_high_confidence_cases_all_pass():
    results = _run()
    high = [r for r in results if r["tier"] == "high"]
    assert high, "golden set phải có ca tầng 'high'"
    failed = [r["id"] for r in high if not r["match"]]
    assert not failed, f"Ca high-confidence sai (regression): {failed}"


def test_golden_set_covers_all_tiers():
    cases = load_golden(GOLDEN)
    tiers = {c.get("tier") for c in cases}
    assert {"high", "needs_expert", "known_gap"} <= tiers


def test_summarize_counts_match():
    results = _run()
    s = summarize(results)
    assert s["overall"]["total"] == len(results)
    assert s["overall"]["match"] == sum(1 for r in results if r["match"])
