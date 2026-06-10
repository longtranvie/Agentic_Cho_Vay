"""Lưu phiên hội thoại intake nhiều lượt — SQLite (thư viện chuẩn, không cần cài).

Giữ hồ-sơ-đang-dở + lịch sử chat theo session_id để khách khai dần qua nhiều lượt
HTTP; thoát ra rồi vào lại vẫn còn (ADR-0013 nối phiên & TTL). Đổi sang Postgres sau
khi chốt hợp đồng API với Vapp (open-questions T1).
"""

from __future__ import annotations

import json
import sqlite3
import time
import uuid
from pathlib import Path


class SessionStore:
    """CRUD phiên trên một file SQLite. Mỗi phiên: hồ sơ dở + messages + mốc thời gian."""

    def __init__(self, db_path: str):
        self._db = str(db_path)
        Path(self._db).parent.mkdir(parents=True, exist_ok=True)
        self._exec(
            """CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                application TEXT NOT NULL,
                messages TEXT NOT NULL,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )"""
        )

    def _exec(self, sql: str, params: tuple = (), fetch: bool = False):
        conn = sqlite3.connect(self._db)
        try:
            cur = conn.execute(sql, params)
            row = cur.fetchone() if fetch else None
            conn.commit()
            return row
        finally:
            conn.close()

    def create(self) -> str:
        sid = uuid.uuid4().hex[:16]
        now = time.time()
        self._exec(
            "INSERT INTO sessions (id, application, messages, created_at, updated_at)"
            " VALUES (?,?,?,?,?)",
            (sid, "{}", "[]", now, now),
        )
        return sid

    def get(self, sid: str) -> dict | None:
        row = self._exec(
            "SELECT application, messages, created_at, updated_at FROM sessions WHERE id=?",
            (sid,),
            fetch=True,
        )
        if not row:
            return None
        return {
            "id": sid,
            "application": json.loads(row[0]),
            "messages": json.loads(row[1]),
            "created_at": row[2],
            "updated_at": row[3],
        }

    def save(self, sid: str, application: dict, messages: list) -> None:
        self._exec(
            "UPDATE sessions SET application=?, messages=?, updated_at=? WHERE id=?",
            (
                json.dumps(application, ensure_ascii=False),
                json.dumps(messages, ensure_ascii=False),
                time.time(),
                sid,
            ),
        )

    def purge_expired(self, ttl_seconds: float) -> int:
        """Xóa phiên quá hạn TTL (ADR-0013). Giá trị TTL chốt ở open-questions B3.

        Chưa tự gọi định kỳ — để caller quyết lịch chạy. Trả số phiên đã xóa.
        """
        cutoff = time.time() - ttl_seconds
        row = self._exec(
            "SELECT count(*) FROM sessions WHERE updated_at < ?", (cutoff,), fetch=True
        )
        self._exec("DELETE FROM sessions WHERE updated_at < ?", (cutoff,))
        return row[0] if row else 0
