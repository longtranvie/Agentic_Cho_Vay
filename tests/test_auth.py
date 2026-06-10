import os
import tempfile

from fastapi.testclient import TestClient

import loan_agent.api.app as api_module
from loan_agent.api.sessions import SessionStore
from loan_agent.compliance.audit import AuditLog
from loan_agent.config import load_decision_table, settings
from loan_agent.graph import build_graph
from loan_agent.llm.mock import MockLLM
from loan_agent.rag.keyword_store import KeywordStore

_TMP = tempfile.gettempdir()
api_module._runtime["graph"] = build_graph(MockLLM(), KeywordStore([]), load_decision_table())
api_module._runtime["audit"] = AuditLog(os.path.join(_TMP, "loan_auth_test_audit.jsonl"))
api_module._runtime["sessions"] = SessionStore(os.path.join(_TMP, "loan_auth_test.db"))

client = TestClient(api_module.app)

KEY = "secret-key-123"


def test_health_open_even_with_auth_on():
    settings.api_key = KEY
    try:
        assert client.get("/health").status_code == 200  # /health luôn mở
    finally:
        settings.api_key = ""


def test_protected_route_401_without_key():
    settings.api_key = KEY
    try:
        assert client.post("/sessions").status_code == 401  # không gửi header
        assert client.post("/sessions", headers={"X-API-Key": "sai"}).status_code == 401
    finally:
        settings.api_key = ""


def test_protected_route_ok_with_correct_key():
    settings.api_key = KEY
    try:
        assert client.post("/sessions", headers={"X-API-Key": KEY}).status_code == 200
    finally:
        settings.api_key = ""


def test_auth_off_when_key_empty():
    settings.api_key = ""  # dev: chưa cấu hình khóa → mở
    assert client.post("/sessions").status_code == 200
