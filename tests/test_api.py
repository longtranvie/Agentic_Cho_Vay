import os
import tempfile

from fastapi.testclient import TestClient

import loan_agent.api.app as api_module
from loan_agent.compliance.audit import AuditLog
from loan_agent.config import load_decision_table
from loan_agent.graph import build_graph
from loan_agent.llm.mock import MockLLM
from loan_agent.rag.keyword_store import KeywordStore

# Bơm graph mock vào runtime để test API offline (không gọi OpenAI dù .env đặt gì).
api_module._runtime["graph"] = build_graph(MockLLM(), KeywordStore([]), load_decision_table())
api_module._runtime["audit"] = AuditLog(
    os.path.join(tempfile.gettempdir(), "loan_api_test_audit.jsonl")
)

client = TestClient(api_module.app)

COMPLETE = {
    "loan": {"amount": 10_000_000, "purpose": "mua xe", "term_months": 12},
    "income": {"monthly": 30_000_000, "source": "luong", "stability": "on_dinh"},
    "debt": {"total": 0, "monthly_payment": 0},
    "profile": {"age": 32, "occupation": "ky su", "tenure_years": 5},
    "credit_history": {"had_late_payment": False},
}


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_assess_complete_returns_decision_and_notice():
    r = client.post("/assess", json=COMPLETE)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "completed"
    assert body["decision"]["outcome"] in {"approve", "reject", "review"}
    assert body["transparency_notice"]["xu_ly_tu_dong"] is True


def test_assess_incomplete_returns_missing_fields():
    r = client.post("/assess", json={"loan": {"amount": 10_000_000}})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "incomplete"
    assert "loan.purpose" in body["missing_required_fields"]
