"""Bóc/che PII trước khi gửi ra dịch vụ ngoài — ADR-0019.

Áp cho MỌI egress (OpenAI, LangSmith, log). Lưu ý: redact văn bản tự do không
tuyệt đối 100% (xem ADR-0019); số tài chính < 9 chữ số được giữ.
"""

from __future__ import annotations

import re

_PATTERNS = [
    (re.compile(r"\b0\d{9}\b"), "[SĐT]"),  # SĐT VN: 10 số bắt đầu 0
    (re.compile(r"\b\d{9,12}\b"), "[CCCD]"),  # CMND/CCCD: 9-12 số
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[EMAIL]"),
]


def redact_text(text: str) -> str:
    """Che SĐT, CCCD/CMND, email trong văn bản tự do."""
    for pattern, replacement in _PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def anonymize(value):
    """Đệ quy redact mọi chuỗi trong dict/list (defense-in-depth)."""
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, dict):
        return {k: anonymize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [anonymize(v) for v in value]
    return value


def anonymize_application(app: dict) -> dict:
    """Ẩn danh hồ sơ trước khi đưa vào prompt LLM."""
    return anonymize(app)
