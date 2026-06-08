"""Chọn LLM backend theo config (đổi backend = đổi env) — ADR-0006/0019."""

from __future__ import annotations

from ..config import settings as default_settings
from .mock import MockLLM


def get_llm(settings=None, *, decision: bool = False):
    s = settings or default_settings
    if s.llm_provider == "openai":
        from .openai_client import OpenAILLM

        return OpenAILLM(s, decision=decision)
    return MockLLM()
