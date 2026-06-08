"""LLMClient dùng OpenAI (THẬT) — ADR-0006. 🔴 cần API key + mạng để chạy.

Ẩn danh PII trước khi gửi (ADR-0019). Import langchain_openai trong __init__ để
môi trường không cấu hình vẫn import được module này.
"""

from __future__ import annotations

from pydantic import BaseModel

from ..pii.anonymizer import redact_text


class OpenAILLM:
    def __init__(self, settings, *, decision: bool = False):
        from langchain_openai import ChatOpenAI

        model = settings.llm_decision_model if decision else settings.llm_model
        self._chat = ChatOpenAI(
            model=model, api_key=settings.openai_api_key, temperature=0
        )

    def complete(self, prompt: str) -> str:
        return self._chat.invoke(redact_text(prompt)).content

    def structured(self, prompt: str, schema: type[BaseModel]) -> BaseModel:
        # with_structured_output ép model trả đúng schema (ADR-0007).
        return self._chat.with_structured_output(schema).invoke(redact_text(prompt))
