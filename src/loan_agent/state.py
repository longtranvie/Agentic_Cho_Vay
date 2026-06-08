"""State của LangGraph mang theo toàn phiên — ADR-0001, docs/architecture.md §3.

`messages` dùng reducer add (append); các field khác ghi đè (last-write-wins).
"""

from __future__ import annotations

from operator import add
from typing import Annotated, TypedDict


class LoanState(TypedDict, total=False):
    messages: Annotated[list, add]
    application: dict
    provenance: dict
    affordability: dict
    risk: dict
    deliberation: dict
    policy: dict
    decision: dict
    case: dict
    meta: dict
