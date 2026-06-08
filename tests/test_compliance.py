import json
import os
import tempfile

from loan_agent.compliance.audit import AuditLog, subject_ref
from loan_agent.compliance.transparency import build_notice

APP = {"profile": {"age": 30}, "income": {"monthly": 20_000_000}}


def test_subject_ref_pseudonymous_and_stable():
    ref = subject_ref(APP)
    assert ref.startswith("subj_")
    assert ref == subject_ref(APP)  # ổn định
    assert len(ref) == len("subj_") + 12  # chỉ là pseudonym hash ngắn
    assert "20000000" not in ref  # không nhúng giá trị thu nhập thô
    assert subject_ref(APP) != subject_ref({"profile": {"age": 99}})  # khác chủ thể → khác ref


def test_audit_record_appends_pii_safe():
    path = os.path.join(tempfile.gettempdir(), "loan_audit_test.jsonl")
    if os.path.exists(path):
        os.remove(path)
    log = AuditLog(path)
    subj = subject_ref(APP)
    log.record("processing_started", subject=subj, data_categories=["income", "profile"])
    log.record("automated_decision", subject=subj, outcome="approve")
    with open(path, encoding="utf-8") as f:
        lines = f.read().strip().splitlines()
    os.remove(path)
    assert len(lines) == 2
    e0 = json.loads(lines[0])
    assert e0["event"] == "processing_started" and e0["subject"] == subj and "ts" in e0
    # PII-safe: không ghi giá trị thu nhập thô
    assert "20000000" not in lines[0] and "20000000" not in lines[1]


def test_transparency_notice_flags_automated():
    result = {
        "decision": {"outcome": "approve", "reasons": ["Điểm đạt ngưỡng"]},
        "risk": {"score": 80, "dti": 0.3},
    }
    n = build_notice(result)
    assert n["xu_ly_tu_dong"] is True
    assert n["ket_qua"] == "ĐỀ XUẤT DUYỆT"
    assert "356" in n["co_so_phap_ly"]
