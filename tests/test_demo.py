import json
from pathlib import Path

from loan_agent.config import load_decision_table, settings
from loan_agent.graph import build_graph
from loan_agent.llm.mock import MockLLM
from loan_agent.rag.ingest import load_policies
from loan_agent.rag.keyword_store import KeywordStore

ROOT = Path(__file__).resolve().parents[1]


def test_sample_applications_match_expected_outcome():
    data = json.loads(
        (ROOT / "data" / "sample_applications.json").read_text(encoding="utf-8")
    )
    store = KeywordStore(load_policies(settings.policy_dir))
    graph = build_graph(MockLLM(), store, load_decision_table())
    for case in data["applications"]:
        result = graph.invoke(
            {"application": case["application"], "messages": [], "meta": {}}
        )
        outcome = result["decision"]["outcome"]
        assert outcome == case["expected_outcome"], (
            f"{case['name']}: got {outcome}, expected {case['expected_outcome']}"
        )
