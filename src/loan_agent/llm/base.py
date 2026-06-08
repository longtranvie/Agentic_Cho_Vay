"""Interface LLMClient (Protocol) — ADR-0006/0007.

mock & openai cùng tuân theo để đổi provider/đường PII (I)/(II) mà không sửa caller.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import BaseModel


@runtime_checkable
class LLMClient(Protocol):
    def complete(self, prompt: str) -> str: ...

    def structured(self, prompt: str, schema: type[BaseModel]) -> BaseModel: ...
