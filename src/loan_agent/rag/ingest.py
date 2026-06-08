"""Nạp tài liệu chính sách từ data/policies/*.md → chunk theo '## Điều'.

docs/rag-design.md §2 (chunk theo Điều/Khoản). Mỗi chunk: {source, dieu, snippet}.
"""

from __future__ import annotations

from pathlib import Path


def _chunk_markdown(text: str, source: str) -> list[dict]:
    chunks: list[dict] = []
    current_dieu: str | None = None
    buffer: list[str] = []

    def flush():
        if buffer and "".join(buffer).strip():
            chunks.append(
                {
                    "source": source,
                    "dieu": current_dieu,
                    "snippet": " ".join(buffer).strip(),
                }
            )

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            flush()
            buffer = []
            current_dieu = stripped.lstrip("# ").strip()
        elif not stripped.startswith("# "):
            buffer.append(stripped)
    flush()
    return chunks


def load_policies(policy_dir: str) -> list[dict]:
    docs: list[dict] = []
    for path in sorted(Path(policy_dir).glob("*.md")):
        docs.extend(_chunk_markdown(path.read_text(encoding="utf-8"), path.stem))
    return docs
