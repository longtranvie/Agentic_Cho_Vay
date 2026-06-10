import json
import os
import tempfile

from fastapi.testclient import TestClient

import loan_agent.api.app as api_module
from loan_agent.api.sessions import SessionStore
from loan_agent.compliance.audit import AuditLog
from loan_agent.config import load_decision_table
from loan_agent.graph import build_graph
from loan_agent.llm.mock import MockLLM
from loan_agent.rag.keyword_store import KeywordStore

_TMP = tempfile.gettempdir()
_AUDIT = os.path.join(_TMP, "loan_consent_test_audit.jsonl")

api_module._runtime["graph"] = build_graph(MockLLM(), KeywordStore([]), load_decision_table())
api_module._runtime["audit"] = AuditLog(_AUDIT)
api_module._runtime["sessions"] = SessionStore(os.path.join(_TMP, "loan_consent_test.db"))

client = TestClient(api_module.app)


def _start() -> str:
    return client.post("/sessions").json()["session_id"]


def test_start_returns_consent_notice_not_questions():
    body = client.post("/sessions").json()
    assert body["status"] == "consent_required"
    assert body["consent_notice"]["version"]
    assert "next_question" not in body  # CHƯA hỏi field khi chưa đồng ý


def test_message_blocked_without_consent():
    sid = _start()
    r = client.post(f"/sessions/{sid}/message", json={"profile": {"age": 30}})
    assert r.status_code == 403


def test_consent_then_message_flows():
    sid = _start()
    c = client.post(f"/sessions/{sid}/consent", json={"agreed": True}).json()
    assert c["status"] == "incomplete"
    assert c["next_question"]
    assert client.post(f"/sessions/{sid}/message", json={"profile": {"age": 30}}).status_code == 200


def test_consent_declined_stays_blocked():
    sid = _start()
    c = client.post(f"/sessions/{sid}/consent", json={"agreed": False}).json()
    assert c["status"] == "consent_declined"
    r = client.post(f"/sessions/{sid}/message", json={"profile": {"age": 30}})
    assert r.status_code == 403


def test_consent_given_recorded_in_audit():
    if os.path.exists(_AUDIT):
        os.remove(_AUDIT)
    api_module._runtime["audit"] = AuditLog(_AUDIT)
    sid = _start()
    client.post(f"/sessions/{sid}/consent", json={"agreed": True})
    with open(_AUDIT, encoding="utf-8") as f:
        events = [json.loads(line)["event"] for line in f]
    assert "consent_given" in events


def test_withdraw_blocks_message_again():
    sid = _start()
    client.post(f"/sessions/{sid}/consent", json={"agreed": True})
    assert client.post(f"/sessions/{sid}/message", json={"profile": {"age": 30}}).status_code == 200
    c = client.post(f"/sessions/{sid}/withdraw").json()
    assert c["status"] == "consent_withdrawn"
    # Sau khi rút lại → /message bị chặn như chưa đồng ý.
    assert client.post(f"/sessions/{sid}/message", json={"profile": {"age": 31}}).status_code == 403


def test_withdraw_recorded_in_audit():
    if os.path.exists(_AUDIT):
        os.remove(_AUDIT)
    api_module._runtime["audit"] = AuditLog(_AUDIT)
    sid = _start()
    client.post(f"/sessions/{sid}/consent", json={"agreed": True})
    client.post(f"/sessions/{sid}/withdraw")
    with open(_AUDIT, encoding="utf-8") as f:
        events = [json.loads(line)["event"] for line in f]
    assert "consent_withdrawn" in events


def test_review_request_recorded_in_audit():
    if os.path.exists(_AUDIT):
        os.remove(_AUDIT)
    api_module._runtime["audit"] = AuditLog(_AUDIT)
    sid = _start()
    client.post(f"/sessions/{sid}/consent", json={"agreed": True})
    r = client.post(f"/sessions/{sid}/review-request").json()
    assert r["status"] == "human_review_requested"
    with open(_AUDIT, encoding="utf-8") as f:
        events = [json.loads(line)["event"] for line in f]
    assert "human_review_requested" in events


def test_review_request_unknown_session_404():
    assert client.post("/sessions/khong-co/review-request").status_code == 404
