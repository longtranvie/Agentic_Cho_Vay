"""Tiện ích văn bản tiếng Việt dùng chung (RAG keyword + so khớp mục đích)."""

from __future__ import annotations

import unicodedata


def strip_accents(text: str) -> str:
    """Bỏ dấu + thường hóa (đ→d) để khớp bất kể có/không dấu ('phân'≈'phan')."""
    text = text.lower().replace("đ", "d")
    nfd = unicodedata.normalize("NFD", text)
    return "".join(c for c in nfd if not unicodedata.combining(c))
