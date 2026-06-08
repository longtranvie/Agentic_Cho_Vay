"""LLMClient giả lập (deterministic) — test double để chạy/test offline.

Không gọi mạng. Output suy ra từ prompt một cách xác định (không random) để
demo/test tái lập được.
"""

from __future__ import annotations

from pydantic import BaseModel

from ..schemas import AgentTurn

_ROLES = ["Risk Analyst", "Advocate", "Skeptic", "Policy", "Judge"]
_STANCE = {"Advocate": "lean_approve", "Skeptic": "lean_reject"}


def _role_from_prompt(prompt: str) -> str:
    for role in _ROLES:
        if role.lower() in prompt.lower():
            return role
    return "Risk Analyst"


class MockLLM:
    def complete(self, prompt: str) -> str:
        return "(mock) " + prompt.strip()[:60]

    def structured(self, prompt: str, schema: type[BaseModel]) -> BaseModel:
        if schema is AgentTurn:
            role = _role_from_prompt(prompt)
            return AgentTurn(
                role=role,
                stance=_STANCE.get(role, "neutral"),
                arguments=[f"(mock) {role} phân tích hồ sơ"],
                flags_raised=[],  # mock không tự raise cờ -> outcome do score quyết
                rebuttals=[],
            )
        # Các schema có default đầy đủ (JudgeVerdict, LoanApplication...) -> dựng rỗng.
        return schema()
