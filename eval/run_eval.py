"""Chạy eval golden set offline + in báo cáo. Dùng: python eval/run_eval.py

Tất định (MockLLM + KeywordStore) nên tái lập được. Thoát mã != 0 nếu có ca tầng
'high' sai (regression gate). Ca 'needs_expert'/'known_gap' chỉ báo cáo, không chặn.
"""

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # tránh lỗi cp1252 trên Windows

from loan_agent.compliance.audit import AuditLog  # noqa: E402
from loan_agent.config import load_decision_table  # noqa: E402
from loan_agent.eval import evaluate, load_golden, summarize  # noqa: E402
from loan_agent.graph import build_graph  # noqa: E402
from loan_agent.llm.mock import MockLLM  # noqa: E402
from loan_agent.rag.ingest import load_policies  # noqa: E402
from loan_agent.rag.keyword_store import KeywordStore  # noqa: E402
from loan_agent.service import run_assessment  # noqa: E402


def main() -> int:
    cases = load_golden(ROOT / "data" / "eval" / "golden_set.json")
    store = KeywordStore(load_policies(str(ROOT / "data" / "policies")))
    graph = build_graph(MockLLM(), store, load_decision_table())
    audit = AuditLog(os.path.join(tempfile.gettempdir(), "loan_eval_audit.jsonl"))

    results = evaluate(lambda app: run_assessment(graph, app, audit), cases)

    print("\n=== EVAL GOLDEN SET (offline, tất định) ===\n")
    print(f"{'ID':20} {'TẦNG':13} {'KỲ VỌNG':8} {'THỰC TẾ':8} KQ")
    print("-" * 60)
    for r in results:
        mark = "✓" if r["match"] else "✗"
        print(
            f"{r['id']:20} {r['tier']:13} {r['expected']:8} {str(r['actual']):8} {mark}"
        )

    s = summarize(results)
    o = s["overall"]
    print("\n--- Accuracy theo tầng ---")
    for tier, t in sorted(s["by_tier"].items()):
        print(f"  {tier:13} {t['match']}/{t['total']}")
    print(f"  {'TỔNG':13} {o['match']}/{o['total']}")

    mism = [r for r in results if not r["match"]]
    if mism:
        print("\n--- Lệch (đọc kỹ: high=bug · needs_expert/known_gap=phát hiện) ---")
        for r in mism:
            print(f"  [{r['tier']}] {r['id']}: kỳ vọng {r['expected']} ≠ máy {r['actual']}")
            print(f"      → {r['basis']}")

    high_fail = [r for r in results if r["tier"] == "high" and not r["match"]]
    if high_fail:
        print(f"\n❌ REGRESSION: {len(high_fail)} ca high-confidence sai.")
        return 1
    print("\n✅ Mọi ca high-confidence đúng. (Lệch needs_expert/known_gap là chủ đích.)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
