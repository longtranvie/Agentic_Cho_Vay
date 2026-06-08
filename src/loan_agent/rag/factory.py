"""Chọn RAG backend theo config (đổi backend = đổi env) — ADR-0005/0016."""

from __future__ import annotations

from ..config import settings as default_settings
from .ingest import load_policies
from .keyword_store import KeywordStore


def get_store(settings=None):
    s = settings or default_settings
    docs = load_policies(s.policy_dir)
    if s.rag_backend == "chroma":
        from .chroma_store import ChromaStore

        return ChromaStore(docs, s)
    return KeywordStore(docs)
