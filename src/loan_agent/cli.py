"""Entry point chạy thử — mock LLM mặc định (offline).

Batch:  python -m loan_agent.cli data/sample_applications.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from .config import load_decision_table, settings
from .graph import build_graph
from .llm.factory import get_llm
from .rag.factory import get_store


def run_batch(path: str) -> None:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    graph = build_graph(
        get_llm(), get_store(), load_decision_table(), max_turns=settings.max_intake_turns
    )
    for case in data.get("applications", []):
        result = graph.invoke(
            {"application": case["application"], "messages": [], "meta": {}}
        )
        decision = result["decision"]
        aff = result.get("affordability", {})
        print(f"\n=== {case.get('name', '?')} ===")
        print(f"  kỳ vọng : {case.get('expected_outcome', '-')}")
        print(f"  kết quả : {decision['outcome']}  (provider={settings.llm_provider})")
        if aff:
            print(f"  hạn mức ~: {aff.get('max_principal'):,.0f} VND")
        for reason in decision["reasons"]:
            print(f"   - {reason}")


def main() -> None:
    try:  # console Windows mặc định cp1252 -> ép UTF-8 để in tiếng Việt
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if len(sys.argv) > 1:
        run_batch(sys.argv[1])
    else:
        print("Cách dùng: python -m loan_agent.cli data/sample_applications.json")


if __name__ == "__main__":
    main()
