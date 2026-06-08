"""Entry point chạy thử — mock LLM mặc định (offline).

Batch:        python -m loan_agent.cli data/sample_applications.json
Hội thoại:    python -m loan_agent.cli            (nhân viên ảo hỏi từng thông tin)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from .config import load_decision_table, settings
from .graph import build_graph
from .llm.factory import get_llm
from .rag.factory import get_store
from .schemas import LoanApplication


def _print_result(result: dict) -> None:
    decision = result["decision"]
    aff = result.get("affordability", {})
    print(f"  kết quả : {decision['outcome']}  (provider={settings.llm_provider})")
    if aff:
        print(f"  hạn mức ~: {aff.get('max_principal'):,.0f} VND")
    for reason in decision["reasons"]:
        print(f"   - {reason}")

    delib = result.get("deliberation") or {}
    if delib.get("convened") and delib["convened"] != "skip":
        line = f"  hội đồng : {delib['convened']} → {delib.get('recommendation', '')}"
        if delib.get("blocking_flags"):
            line += f" (cờ: {', '.join(delib['blocking_flags'])})"
        print(line)

    citations = (result.get("policy") or {}).get("citations") or []
    if citations:
        print("  chính sách dẫn chiếu:")
        for c in citations:
            print(f"   • [{c['source']}] {c.get('dieu') or '?'}: {c['snippet'][:80]}…")


def run_batch(path: str) -> None:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    graph = build_graph(
        get_llm(), get_store(), load_decision_table(), max_turns=settings.max_intake_turns
    )
    for case in data.get("applications", []):
        result = graph.invoke(
            {"application": case["application"], "messages": [], "meta": {}}
        )
        print(f"\n=== {case.get('name', '?')} ===")
        print(f"  kỳ vọng : {case.get('expected_outcome', '-')}")
        _print_result(result)


# --- Hội thoại offline ---------------------------------------------------
# Mock LLM không bóc tách câu tiếng Việt tự do, nên chế độ này hỏi tuần tự
# từng trường còn thiếu và parse câu trả lời (xác định, không cần OpenAI).

_QUESTIONS: dict[str, tuple[str, str]] = {
    "loan.amount": ("Bạn muốn vay bao nhiêu? (vd: 10tr, 50 triệu)", "money"),
    "loan.purpose": ("Mục đích vay là gì? (vd: mua xe, kinh doanh)", "str"),
    "loan.term_months": ("Vay trong bao nhiêu tháng? (vd: 12)", "int"),
    "income.monthly": ("Thu nhập hàng tháng của bạn? (vd: 20tr)", "money"),
    "income.source": ("Nguồn thu nhập? [1] lương  [2] kinh doanh  [3] khác", "source"),
    "income.stability": (
        "Thu nhập có ổn định không? [1] ổn định  [2] không ổn định", "stability"
    ),
    "debt.total": ("Tổng dư nợ hiện tại? (chưa có thì nhập 0)", "money"),
    "debt.monthly_payment": ("Mỗi tháng đang trả nợ bao nhiêu? (chưa có thì nhập 0)", "money"),
    "profile.age": ("Bạn bao nhiêu tuổi?", "int"),
    "profile.occupation": ("Nghề nghiệp của bạn?", "str"),
    "profile.tenure_years": ("Làm công việc hiện tại được mấy năm? (vd: 3)", "float"),
    "credit_history.had_late_payment": (
        "Bạn từng trả nợ trễ hạn chưa? [1] chưa  [2] đã từng", "bool"
    ),
}


def _parse_money(raw: str) -> float:
    s = raw.strip().lower().replace(",", "").replace(".", "").replace(" ", "")
    for kw, mult in (
        ("triệu", 1_000_000), ("trieu", 1_000_000), ("tr", 1_000_000),
        ("nghìn", 1000), ("nghin", 1000), ("ngàn", 1000), ("ngan", 1000), ("k", 1000),
    ):
        if s.endswith(kw):
            return float(s[: -len(kw)]) * mult
    return float(s)


def _parse_source(raw: str) -> str:
    return {
        "1": "luong", "luong": "luong", "lương": "luong",
        "2": "kinh_doanh", "kinh_doanh": "kinh_doanh", "kinh doanh": "kinh_doanh",
        "3": "khac", "khac": "khac", "khác": "khac",
    }[raw.strip().lower()]


def _parse_stability(raw: str) -> str:
    return {
        "1": "on_dinh", "on_dinh": "on_dinh", "ổn định": "on_dinh", "on dinh": "on_dinh",
        "2": "khong_on_dinh", "khong_on_dinh": "khong_on_dinh",
        "không ổn định": "khong_on_dinh", "khong on dinh": "khong_on_dinh",
    }[raw.strip().lower()]


def _parse_bool(raw: str) -> bool:
    s = raw.strip().lower()
    if s in ("1", "chưa", "chua", "không", "khong", "n", "no"):
        return False
    if s in ("2", "đã từng", "da tung", "đã", "da", "có", "co", "y", "yes"):
        return True
    raise ValueError(raw)


def _parse(kind: str, raw: str):
    if kind == "money":
        return _parse_money(raw)
    if kind == "int":
        return int(raw.strip())
    if kind == "float":
        return float(raw.strip())
    if kind == "str":
        if not raw.strip():
            raise ValueError("rỗng")
        return raw.strip()
    if kind == "source":
        return _parse_source(raw)
    if kind == "stability":
        return _parse_stability(raw)
    if kind == "bool":
        return _parse_bool(raw)
    raise ValueError(kind)


def run_interactive() -> None:
    print("Xin chào! Mình là nhân viên tín dụng ảo của Vapp.")
    print("Mình hỏi vài thông tin để xem bạn vay được không. (Ctrl+C để thoát)\n")
    app: dict = {}
    while True:
        missing = LoanApplication.model_validate(app).missing_required_fields()
        if not missing:
            break
        field = missing[0]
        question, kind = _QUESTIONS[field]
        try:
            raw = input(f"  {question}\n  > ")
        except (EOFError, KeyboardInterrupt):
            print("\nĐã thoát.")
            return
        try:
            value = _parse(kind, raw)
        except (ValueError, KeyError):
            print("  (Mình chưa hiểu, bạn nhập lại giúp nhé)\n")
            continue
        section, key = field.split(".")
        app.setdefault(section, {})[key] = value
        print()

    print("Cảm ơn bạn! Mình thẩm định nhé...\n")
    graph = build_graph(
        get_llm(), get_store(), load_decision_table(), max_turns=settings.max_intake_turns
    )
    result = graph.invoke({"application": app, "messages": [], "meta": {}})
    print("=== KẾT QUẢ ===")
    _print_result(result)


def main() -> None:
    for stream in (sys.stdout, sys.stdin):  # ép UTF-8 để in/đọc tiếng Việt trên Windows
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except Exception:
            pass
    if len(sys.argv) > 1:
        run_batch(sys.argv[1])
    else:
        run_interactive()


if __name__ == "__main__":
    main()
