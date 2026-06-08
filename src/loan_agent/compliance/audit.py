"""Nhật ký xử lý dữ liệu cá nhân — NĐ356/2025 (ghi nhật ký toàn bộ hoạt động xử lý).

PII-safe: KHÔNG ghi giá trị thô (ADR-0019) — chỉ ghi loại dữ liệu, pseudonym chủ thể,
mục đích, thời điểm, sự kiện. Sink hiện tại = JSONL append-only; production thay bằng
kho append-only (Postgres/WORM) và đặt hook tại từng node thay vì ở lớp điều phối.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def subject_ref(application: dict) -> str:
    """Pseudonym ổn định cho chủ thể dữ liệu (không lộ danh tính) để gắn các sự kiện."""
    basis = json.dumps(application or {}, sort_keys=True, ensure_ascii=False)
    return "subj_" + hashlib.sha256(basis.encode("utf-8")).hexdigest()[:12]


class AuditLog:
    """Ghi sự kiện xử lý ra JSONL. Mỗi dòng 1 sự kiện, không chứa PII thô."""

    def __init__(self, path: str):
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, event: str, *, subject: str, **fields) -> dict:
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "subject": subject,
            **fields,
        }
        with self._path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry
