"""Cấu hình hệ thống (env/.env) + nạp decision table (config có version).

ADR-0006/0014. Xem .env.example.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DECISION_TABLE = PROJECT_ROOT / "config" / "decision_table.json"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="LOAN_", extra="ignore"
    )

    # Backend selection (đổi backend = đổi env, không sửa caller)
    llm_provider: str = "mock"  # mock | openai
    rag_backend: str = "keyword"  # keyword | chroma

    # Models (ADR-0006) — chỉ dùng khi provider=openai
    llm_model: str = "gpt-4o-mini"
    llm_decision_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-large"

    # Đường dẫn dữ liệu
    decision_table: str = str(DEFAULT_DECISION_TABLE)
    policy_dir: str = str(PROJECT_ROOT / "data" / "policies")

    # Hội thoại intake (ADR-0003)
    max_intake_turns: int = 12

    openai_api_key: str = ""

    def model_post_init(self, __context) -> None:
        if not self.openai_api_key:
            object.__setattr__(self, "openai_api_key", os.getenv("OPENAI_API_KEY", ""))


settings = Settings()


def load_decision_table(path: str | None = None) -> dict:
    """Nạp decision table (JSON). Resolve tương đối theo project root."""
    p = Path(path or os.environ.get("LOAN_DECISION_TABLE", DEFAULT_DECISION_TABLE))
    if not p.is_absolute():
        p = PROJECT_ROOT / p
    return json.loads(p.read_text(encoding="utf-8"))
