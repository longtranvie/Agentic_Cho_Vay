"""PolicyStore offline (keyword overlap) — test double, không cần embeddings.

Đủ để chạy/test pipeline offline (docs/rag-design.md). Production dùng ChromaStore.
"""

from __future__ import annotations

import re

from ..schemas import PolicyCitation
from ..tools.text import strip_accents


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"\w+", strip_accents(text)))


class KeywordStore:
    def __init__(self, docs: list[dict]):
        self._docs = docs

    def retrieve(self, query: str, k: int = 3) -> list[PolicyCitation]:
        q = _tokens(query)
        scored = []
        for doc in self._docs:
            score = len(q & _tokens(doc["snippet"]))
            if score:
                scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            PolicyCitation(
                source=doc["source"], snippet=doc["snippet"], dieu=doc.get("dieu")
            )
            for _, doc in scored[:k]
        ]
