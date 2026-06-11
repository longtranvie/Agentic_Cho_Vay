"""Sinh bộ hồ sơ vay VN giả lập (đa dạng) cho eval/demo — KHÔNG phải dữ liệu thật.

⚠️ Nhãn `expected_outcome` do ORACLE luật-định suy ra (knock-out + heuristic), KHÔNG phải
kết quả vỡ nợ thật → chỉ dùng test coverage / demo / xem phân phối quyết định. KHÔNG
calibrate được trọng số scorecard (việc đó cần dữ liệu vay-trả thật — open-questions D5).

Tầng nhãn (như golden_set):
  high         = suy chắc từ luật (knock-out rõ / hồ sơ sạch mạnh) — đáng tin để regression
  needs_expert = ca biên, phán đoán dev — KHÔNG phải chân lý
  known_gap    = offline không bắt được (mâu thuẫn logic) — cần hội đồng LLM

Có seed (tái lập). Chạy: python eval/generate_synthetic.py
"""

from __future__ import annotations

import json
import os
import random
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from loan_agent.compliance.audit import AuditLog  # noqa: E402
from loan_agent.config import load_decision_table  # noqa: E402
from loan_agent.eval import evaluate, summarize  # noqa: E402
from loan_agent.graph import build_graph  # noqa: E402
from loan_agent.llm.mock import MockLLM  # noqa: E402
from loan_agent.rag.keyword_store import KeywordStore  # noqa: E402
from loan_agent.service import run_assessment  # noqa: E402
from loan_agent.tools.financial import debt_to_income, monthly_payment  # noqa: E402
from loan_agent.tools.text import strip_accents  # noqa: E402

OCCUPATIONS = [
    "nhan vien van phong", "cong nhan", "giao vien", "ky su", "ban hang",
    "tai xe", "ke toan", "buon ban nho", "lao dong tu do", "y ta",
]
PURPOSES_OK = [
    "mua xe may", "sua nha", "hoc phi", "chi phi y te", "mua do gia dung",
    "cuoi hoi", "du lich", "mua dien thoai",
]
PURPOSES_BANNED = ["mua vang mieng", "dao no vay khac", "gui tien tiet kiem"]


def _oracle(app: dict, table: dict) -> tuple[str, str, str]:
    """Suy nhãn kỳ vọng từ LUẬT (độc lập với trọng số scorecard chưa hiệu chỉnh)."""
    ko = table["knockout"]
    loan, inc, debt, prof, ch = (
        app["loan"], app["income"], app["debt"], app["profile"], app["credit_history"],
    )
    age, income = prof["age"], inc["monthly"]

    # --- Hard rules (luật) → reject, đáng tin (high) ---
    if age < ko["min_age"] or age > ko["max_age"]:
        return "reject", "high", f"Tuổi {age} ngoài [{ko['min_age']},{ko['max_age']}] → knock-out"
    if income < ko["min_income"]:
        return "reject", "high", "Thu nhập dưới sàn tối thiểu → knock-out"
    if loan["amount"] > ko["max_loan_amount"]:
        return "reject", "high", "Vượt trần khoản vay → knock-out"
    purpose = strip_accents(loan["purpose"])
    for term in ko.get("forbidden_purposes", []):
        if strip_accents(term) in purpose:
            return "reject", "high", f"Mục đích cấm ('{term}') Điều 8 → knock-out"
    payment = monthly_payment(loan["amount"], table["interest_rate"]["annual"], loan["term_months"])
    dti = debt_to_income(income, debt["monthly_payment"], payment)
    if dti > ko["dti_abs_max"]:
        return "reject", "high", f"DTI {dti:.2f} > {ko['dti_abs_max']} → knock-out"

    # --- Mâu thuẫn logic → offline không bắt (known_gap) ---
    if prof["tenure_years"] > max(0, age - 18):
        return "review", "known_gap", "Thâm niên > số năm có thể đi làm (mâu thuẫn) → cần hội đồng LLM"

    # --- Hồ sơ sạch mạnh → approve, đáng tin (high) ---
    if dti < 0.2 and not ch["had_late_payment"] and inc["stability"] == "on_dinh" and prof["tenure_years"] >= 3:
        return "approve", "high", f"DTI {dti:.2f} thấp, sạch, ổn định, thâm niên ≥3 → rõ ràng đủ điều kiện"

    # --- Ca biên → phán đoán dev (needs_expert, KHÔNG phải chân lý) ---
    if ch["had_late_payment"] or inc["stability"] == "khong_on_dinh" or dti >= 0.4:
        return "review", "needs_expert", "Có tín hiệu rủi ro (trễ/không ổn định/DTI cao) → kỳ vọng xét tay (phán đoán dev)"
    return "approve", "needs_expert", "Hồ sơ trung bình, không cờ rõ → kỳ vọng đậu (phán đoán dev)"


def _random_app(rng: random.Random) -> dict:
    income = rng.choice([3_500_000, 5_000_000, 8_000_000, 12_000_000, 18_000_000,
                         25_000_000, 35_000_000, 50_000_000])
    amount = rng.choice([5, 10, 15, 20, 30, 40, 60, 80, 110, 130]) * 1_000_000
    has_debt = rng.random() < 0.45
    purpose = rng.choice(PURPOSES_OK) if rng.random() < 0.9 else rng.choice(PURPOSES_BANNED)
    return {
        "loan": {"amount": amount, "purpose": purpose, "term_months": rng.choice([6, 12, 18, 24, 36])},
        "income": {
            "monthly": income,
            "source": rng.choice(["luong", "kinh_doanh", "khac"]),
            "stability": rng.choice(["on_dinh", "on_dinh", "khong_on_dinh"]),
        },
        "debt": {
            "total": 0,
            "monthly_payment": rng.choice([0, 1_000_000, 2_000_000, 4_000_000]) if has_debt else 0,
        },
        "profile": {
            "age": rng.randint(19, 65),
            "occupation": rng.choice(OCCUPATIONS),
            "tenure_years": rng.randint(0, 20),
        },
        "credit_history": {"had_late_payment": rng.random() < 0.25},
    }


def generate(n: int = 100, seed: int = 42) -> list[dict]:
    rng = random.Random(seed)
    table = load_decision_table()
    cases: list[dict] = []
    for i in range(n):
        app = _random_app(rng)
        expected, tier, basis = _oracle(app, table)
        cases.append({
            "id": f"syn-{i:03d}",
            "name": f"Giả lập #{i:03d} ({app['loan']['purpose']})",
            "tier": tier,
            "expected_outcome": expected,
            "basis": basis,
            "application": app,
        })
    return cases


def main() -> int:
    cases = generate()
    out = ROOT / "data" / "eval" / "synthetic_set.json"
    out.write_text(
        json.dumps(
            {
                "_note": "BỘ GIẢ LẬP do eval/generate_synthetic.py sinh (seed=42). Nhãn do oracle "
                "luật-định, KHÔNG phải vỡ nợ thật → test/demo/xem phân phối, KHÔNG calibrate "
                "(cần data thật D5). Tái tạo: python eval/generate_synthetic.py",
                "cases": cases,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    graph = build_graph(MockLLM(), KeywordStore([]), load_decision_table())
    audit = AuditLog(os.path.join(tempfile.gettempdir(), "loan_synth_audit.jsonl"))
    results = evaluate(lambda app: run_assessment(graph, app, audit), cases)
    s = summarize(results)

    print(f"\n=== ĐÃ SINH {len(cases)} hồ sơ → {out.relative_to(ROOT)} ===")
    print("\n--- Phân phối nhãn kỳ vọng (oracle) ---")
    for t in ("high", "needs_expert", "known_gap"):
        print(f"  {t:13} {sum(1 for c in cases if c['tier'] == t)}")
    print("\n--- Phân phối quyết định THỰC TẾ của máy ---")
    for outcome in ("approve", "review", "reject"):
        print(f"  {outcome:9} {sum(1 for r in results if r['actual'] == outcome)}")
    print("\n--- Khớp nhãn theo tầng (high nên ~100%; needs_expert/known_gap lệch là bình thường) ---")
    for tier, t in sorted(s["by_tier"].items()):
        print(f"  {tier:13} {t['match']}/{t['total']}")
    print(f"  {'TỔNG':13} {s['overall']['match']}/{s['overall']['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
