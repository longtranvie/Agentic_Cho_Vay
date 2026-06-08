"""Interface PolicyStore (Protocol) — ADR-0005/0016, docs/rag-design.md.

keyword (offline) & chroma (thật) cùng tuân theo → đổi backend không sửa caller.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..schemas import PolicyCitation


@runtime_checkable
class PolicyStore(Protocol):
    def retrieve(self, query: str, k: int = 3) -> list[PolicyCitation]: ...
