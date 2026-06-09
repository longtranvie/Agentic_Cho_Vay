"""Eval golden set — đo độ đúng của QUYẾT ĐỊNH (không phải logic chạy được).

Khác test đơn vị: ở đây chạy cả pipeline cho từng hồ sơ mẫu rồi so outcome thực tế
với nhãn kỳ vọng. Thuần dữ liệu + so khớp → tái dùng cho test gate và runner báo cáo.
Nhãn theo 3 tầng (xem data/eval/golden_set.json): high · needs_expert · known_gap.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable


def load_golden(path: str | Path) -> list[dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return data["cases"]


def evaluate(run_one: Callable[[dict], dict], cases: list[dict]) -> list[dict]:
    """Chạy từng ca qua `run_one(application)->state` và so outcome với nhãn kỳ vọng."""
    results: list[dict] = []
    for c in cases:
        state = run_one(c["application"])
        actual = (state.get("decision") or {}).get("outcome")
        results.append(
            {
                "id": c["id"],
                "name": c.get("name", ""),
                "tier": c.get("tier", "high"),
                "expected": c["expected_outcome"],
                "actual": actual,
                "match": actual == c["expected_outcome"],
                "basis": c.get("basis", ""),
            }
        )
    return results


def summarize(results: list[dict]) -> dict:
    """Tổng hợp accuracy toàn bộ + theo từng tầng tin cậy."""
    by_tier: dict[str, dict] = {}
    for r in results:
        t = by_tier.setdefault(r["tier"], {"total": 0, "match": 0})
        t["total"] += 1
        t["match"] += 1 if r["match"] else 0
    return {
        "overall": {
            "total": len(results),
            "match": sum(1 for r in results if r["match"]),
        },
        "by_tier": by_tier,
    }
