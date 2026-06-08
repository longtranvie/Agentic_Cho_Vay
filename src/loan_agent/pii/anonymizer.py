"""Bóc/che PII (tên, CCCD, SĐT, email, địa chỉ) khỏi payload & văn bản tự do.

Áp cho mọi egress: OpenAI, LangSmith, log — ADR-0019, docs/integration-infra.md §3.
TODO (skeleton): redact_text(), anonymize_application(); giữ mapping nội bộ.
"""
