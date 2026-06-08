from loan_agent.pii.anonymizer import anonymize_application, redact_text


def test_redact_phone():
    assert "0901234567" not in redact_text("gọi mình 0901234567 nhé")


def test_redact_cccd():
    assert "012345678901" not in redact_text("CCCD 012345678901")


def test_redact_email():
    assert "a@b.com" not in redact_text("mail a@b.com")


def test_redact_keeps_normal_text():
    out = redact_text("tôi muốn vay 10 triệu mua xe")
    assert "vay 10 triệu mua xe" in out


def test_anonymize_application_recurses():
    app = {"profile": {"occupation": "gọi 0901234567"}}
    out = anonymize_application(app)
    assert "0901234567" not in out["profile"]["occupation"]
