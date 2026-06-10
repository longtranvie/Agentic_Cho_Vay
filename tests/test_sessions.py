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

# Bơm graph mock + store phiên tạm vào runtime (test offline, không đụng OpenAI/DB thật).
api_module._runtime["graph"] = build_graph(MockLLM(), KeywordStore([]), load_decision_table())
api_module._runtime["audit"] = AuditLog(os.path.join(_TMP, "loan_sess_test_audit.jsonl"))
api_module._runtime["sessions"] = SessionStore(os.path.join(_TMP, "loan_sess_test.db"))

client = TestClient(api_module.app)


def test_session_store_roundtrip():
    store = SessionStore(os.path.join(_TMP, "loan_sess_unit.db"))
    sid = store.create()
    assert store.get(sid)["application"] == {}
    store.save(sid, {"profile": {"age": 30}}, [{"role": "assistant", "content": "hi"}])
    got = store.get(sid)
    assert got["application"]["profile"]["age"] == 30
    assert got["messages"][0]["content"] == "hi"
    assert store.get("khong-ton-tai") is None


def test_multi_turn_fills_then_decides():
    sid = client.post("/sessions").json()["session_id"]
    client.post(f"/sessions/{sid}/consent", json={"agreed": True})  # đồng ý trước

    # Lượt 1: chỉ khai phần loan → vẫn thiếu, được hỏi tiếp.
    r = client.post(
        f"/sessions/{sid}/message",
        json={"loan": {"amount": 10_000_000, "purpose": "mua xe", "term_months": 12}},
    )
    body = r.json()
    assert body["status"] == "incomplete"
    assert "income.monthly" in body["missing_required_fields"]
    assert body["next_question"]

    # Lượt 2: khai nốt → đủ field → ra quyết định.
    r = client.post(
        f"/sessions/{sid}/message",
        json={
            "income": {"monthly": 30_000_000, "source": "luong", "stability": "on_dinh"},
            "debt": {"total": 0, "monthly_payment": 0},
            "profile": {"age": 32, "occupation": "ky su", "tenure_years": 5},
            "credit_history": {"had_late_payment": False},
        },
    )
    body = r.json()
    assert body["status"] == "completed"
    assert body["decision"]["outcome"] in {"approve", "reject", "review"}
    assert body["transparency_notice"]["xu_ly_tu_dong"] is True


def test_session_persists_partial_state():
    sid = client.post("/sessions").json()["session_id"]
    client.post(f"/sessions/{sid}/consent", json={"agreed": True})  # đồng ý trước
    client.post(f"/sessions/{sid}/message", json={"profile": {"age": 40}})
    r = client.get(f"/sessions/{sid}")
    body = r.json()
    assert body["application"]["profile"]["age"] == 40
    assert body["status"] == "incomplete"
    assert any(m["role"] == "user" for m in body["messages"])


def test_unknown_session_returns_404():
    assert client.post("/sessions/khong-co/message", json={"profile": {"age": 30}}).status_code == 404
    assert client.get("/sessions/khong-co").status_code == 404
