# Loan Agent — Vertical Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hiện thực pipeline thẩm định cho vay multi-agent chạy end-to-end, với tích hợp thật OpenAI + Chroma RAG và test double (mock/keyword) để verify offline.

**Architecture:** LangGraph điều phối: Bootstrap → Intake → Affordability → Pre-checks (knock-out + scorecard) → Deliberation (hội đồng tranh luận, convene check) → Decision Gate (xác định, bất đối xứng) → Review/Human. Quyết định cuối do rule engine; LLM chỉ hội thoại/phân tích. Số do code. Config là dữ liệu có version.

**Tech Stack:** Python 3.11, pydantic v2, pydantic-settings, langgraph, langchain-openai, chromadb, numpy. Test qua `tests/run.py` (pip bị chặn, tương thích pytest sau).

**Spec nguồn:** `docs/superpowers/specs/2026-06-08-loan-agent-design.md` + ADR 0001–0023.

**Ghi chú verify:** Task có nhãn 🟢 verify offline ngay (mock/keyword/deterministic). Task 🔴 cần OpenAI key + mạng → verify ở máy ngoài sandbox (chỉ kiểm tra import/cấu trúc ở đây).

---

## File Structure (khoá phân rã)

```
src/loan_agent/
├── config.py            # Settings(env) + load_decision_table()
├── schemas.py           # Pydantic models
├── state.py             # LoanState (TypedDict)
├── tools/financial.py   # monthly_payment, dti, lti, max_affordable
├── rules/scorecard.py   # knock_out(), score()
├── rules/gate.py        # decide()
├── pii/anonymizer.py    # redact_text(), anonymize_application()
├── llm/base.py          # LLMClient Protocol
├── llm/mock.py          # MockLLM
├── llm/openai_client.py # OpenAILLM (🔴)
├── llm/factory.py       # get_llm() theo config
├── rag/base.py          # PolicyStore Protocol
├── rag/keyword_store.py # KeywordStore
├── rag/chroma_store.py  # ChromaStore (🔴)
├── rag/ingest.py        # load_policies()
├── rag/factory.py       # get_store() theo config
├── agents/intake.py     # extract_and_ask()
├── agents/deliberation.py # convene_check(), run_debate(), judge()
├── nodes.py             # node functions
├── graph.py             # build_graph()
└── cli.py               # main()
config/decision_table.json
data/sample_applications.json · data/policies/*.md
tests/ test_financial.py · test_scorecard.py · test_gate.py · test_pii.py · test_smoke.py · run.py
```

---

## Task 1: Test runner (không cần pytest) 🟢

**Files:** Create `tests/run.py`, modify `tests/conftest.py` (đã có path setup).

- [ ] **Step 1: Viết runner** — `tests/run.py`:
```python
"""Chạy mọi hàm test_* trong tests/test_*.py. Dùng khi chưa cài pytest."""
import importlib, sys, traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

def main() -> int:
    test_files = sorted(p for p in (ROOT / "tests").glob("test_*.py"))
    passed = failed = 0
    for f in test_files:
        mod = importlib.import_module(f"tests.{f.stem}")
        for name in dir(mod):
            if name.startswith("test_"):
                fn = getattr(mod, name)
                try:
                    fn(); passed += 1; print(f"PASS {f.stem}.{name}")
                except Exception:
                    failed += 1; print(f"FAIL {f.stem}.{name}"); traceback.print_exc()
    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0

if __name__ == "__main__":
    raise SystemExit(main())
```
- [ ] **Step 2: Chạy** — `python tests/run.py` → Expected: "0 passed, 0 failed" (chưa có test).
- [ ] **Step 3: Commit** — `git add tests/ && git commit -m "test: add pytest-free runner"`

---

## Task 2: Schemas (Pydantic) 🟢

**Files:** Create `src/loan_agent/schemas.py`, `tests/test_schemas.py`.

- [ ] **Step 1: Viết test** (`tests/test_schemas.py`):
```python
from loan_agent.schemas import LoanApplication, DecisionOutcome

def test_missing_required_fields_detects_empty():
    app = LoanApplication()
    assert "loan.amount" in app.missing_required_fields()
    assert not app.is_complete()

def test_complete_application_is_complete():
    app = LoanApplication.model_validate(SAMPLE)
    assert app.is_complete()
    assert app.missing_required_fields() == []

SAMPLE = {
    "loan": {"amount": 10_000_000, "purpose": "mua xe", "term_months": 12},
    "income": {"monthly": 20_000_000, "source": "luong", "stability": "on_dinh"},
    "debt": {"total": 0, "monthly_payment": 0},
    "profile": {"age": 30, "occupation": "ke_toan", "tenure_years": 3},
    "credit_history": {"had_late_payment": False},
}
```
- [ ] **Step 2: Chạy fail** — `python tests/run.py` → FAIL (no module schemas).
- [ ] **Step 3: Implement** — models: enums (IncomeSource, IncomeStability, DecisionOutcome={approve,reject,review}), sub-models (Loan, Income, Debt, Profile, CreditHistory) tất cả field Optional; LoanApplication với `missing_required_fields()` + `is_complete()`; thêm Affordability, RiskResult, PolicyCitation, PolicyResult, AgentTurn, Deliberation, Decision. (Tham khảo `docs/data-schema.md` cho danh sách field; DecisionOutcome enum giá trị approve/reject/review.)
- [ ] **Step 4: Chạy pass** — `python tests/run.py` → PASS 2 tests.
- [ ] **Step 5: Commit** — `git commit -m "feat: add Pydantic schemas"`

---

## Task 3: Config + decision_table.json (expert-set) 🟢

**Files:** Create `src/loan_agent/config.py`, `config/decision_table.json`, `tests/test_config.py`.

- [ ] **Step 1: Viết test:**
```python
from loan_agent.config import load_decision_table
def test_decision_table_has_required_sections():
    t = load_decision_table()
    for k in ["knockout","scorecard","score_bands","interest_rate","convene","blocking_flags"]:
        assert k in t
    assert t["score_bands"]["approve_min"] > t["score_bands"]["review_min"]
```
- [ ] **Step 2: Chạy fail.**
- [ ] **Step 3: Implement** — `config/decision_table.json` với giá trị expert-set (ĐÁNH DẤU placeholder):
```json
{
  "_note": "EXPERT-SET MINH HỌA — chờ rủi ro Vapp duyệt (D1).",
  "version": "expert-0",
  "knockout": {"min_age": 18, "max_age": 70, "min_income": 1, "dti_abs_max": 0.6},
  "scorecard": {
    "capacity": {"dti": [[0.3,30],[0.4,15],[0.5,5],[9,-20]], "lti": [[2,15],[3,5],[99,-10]]},
    "willingness": {"late_payment": {"false":25,"true":-15},
                    "tenure_years": [[1,0],[3,8],[99,15]],
                    "stability": {"on_dinh":15,"khong_on_dinh":0}}
  },
  "score_bands": {"approve_min": 70, "review_min": 40},
  "interest_rate": {"annual": 0.18},
  "convene": {"clear_approve_min": 75, "trust_required": true},
  "blocking_flags": {
    "data_inconsistency": "review", "unverifiable_critical_data": "review",
    "affordability_borderline": "review", "regulatory_concern": "reject",
    "fraud_signal": "reject"
  }
}
```
- `config.py`: `Settings(BaseSettings)` (env_prefix LOAN_, fields: llm_provider, rag_backend, llm_model, llm_decision_model, embedding_model, decision_table path, policy_dir, max_intake_turns, openai_api_key) + `load_decision_table(path=settings.decision_table)` đọc JSON.
- [ ] **Step 4: Chạy pass.**
- [ ] **Step 5: Commit** — `git commit -m "feat: add config + expert-set decision table"`

---

## Task 4: tools/financial (TDD, deterministic) 🟢

**Files:** Create `src/loan_agent/tools/financial.py`, `tests/test_financial.py`.

- [ ] **Step 1: Viết test** (giá trị kiểm bằng tay):
```python
import math
from loan_agent.tools.financial import monthly_payment, debt_to_income, loan_to_annual_income, max_affordable_principal

def test_monthly_payment_zero_rate():
    assert monthly_payment(1_200_000, 0.0, 12) == 100_000

def test_monthly_payment_annuity():
    p = monthly_payment(10_000_000, 0.12, 12)
    assert math.isclose(p, 888_487.9, rel_tol=1e-3)

def test_dti_basic():
    assert math.isclose(debt_to_income(20_000_000, 2_000_000, 3_000_000), 0.25)

def test_dti_zero_income_is_inf():
    assert debt_to_income(0, 0, 100) == float("inf")

def test_lti():
    assert math.isclose(loan_to_annual_income(24_000_000, 2_000_000), 1.0)

def test_max_affordable_inverse():
    # max payment = 0.4*20tr - 0 = 8tr → principal sao cho trả góp 12 tháng @18% ~ 8tr/th
    principal = max_affordable_principal(20_000_000, 0, 0.18, 12, dti_target=0.4)
    p = monthly_payment(principal, 0.18, 12)
    assert math.isclose(p, 8_000_000, rel_tol=1e-6)
```
- [ ] **Step 2: Chạy fail.**
- [ ] **Step 3: Implement:**
```python
def monthly_payment(principal: float, annual_rate: float, term_months: int) -> float:
    if term_months <= 0: raise ValueError("term_months > 0")
    if principal < 0: raise ValueError("principal >= 0")
    if annual_rate == 0: return principal / term_months
    r = annual_rate / 12
    f = (1 + r) ** term_months
    return principal * r * f / (f - 1)

def debt_to_income(monthly_income, existing_payment, new_payment):
    if monthly_income <= 0: return float("inf")
    return (existing_payment + new_payment) / monthly_income

def loan_to_annual_income(loan_amount, monthly_income):
    annual = monthly_income * 12
    return float("inf") if annual <= 0 else loan_amount / annual

def max_affordable_principal(monthly_income, existing_payment, annual_rate, term_months, dti_target):
    max_pay = max(0.0, dti_target * monthly_income - existing_payment)
    if max_pay == 0: return 0.0
    if annual_rate == 0: return max_pay * term_months
    r = annual_rate / 12
    return max_pay * (1 - (1 + r) ** -term_months) / r
```
- [ ] **Step 4: Chạy pass** (6 tests).
- [ ] **Step 5: Commit** — `git commit -m "feat: financial calculations with tests"`

---

## Task 5: rules/scorecard (knock-out + chấm điểm) 🟢

**Files:** Create `src/loan_agent/rules/scorecard.py`, `tests/test_scorecard.py`.

- [ ] **Step 1: Viết test:** ca tốt (đủ điểm, không knock-out), ca knock-out (tuổi 17 → knocked_out=True), ca điểm thấp. Kiểm `compute_risk(app, table)` trả `RiskResult` với `knocked_out`, `score`, `band` (high/medium/low từ score_bands), `factors`.
```python
def test_knockout_underage():
    r = compute_risk(make_app(age=17), TABLE)
    assert r.knocked_out is True

def test_good_profile_high_score():
    r = compute_risk(make_app(), TABLE)
    assert not r.knocked_out and r.score >= 70
```
- [ ] **Step 2: Chạy fail.**
- [ ] **Step 3: Implement** — `knock_out(app, table)->list[str]` (vi phạm); `compute_risk(app, table)->RiskResult` dùng financial + bảng điểm từ table (capacity + willingness), tổng điểm, map band theo score_bands, liệt kê factors. Helper tra bảng `[[ngưỡng, điểm],...]`.
- [ ] **Step 4: Chạy pass.**
- [ ] **Step 5: Commit** — `git commit -m "feat: scorecard knock-out + scoring"`

---

## Task 6: rules/gate (Decision Gate bất đối xứng) 🟢

**Files:** Create `src/loan_agent/rules/gate.py`, `tests/test_gate.py`.

- [ ] **Step 1: Viết test (bảng chân lý):**
```python
def test_knockout_rejects():
    assert decide(risk(knocked_out=True), policy_ok(), delib_ok(), TABLE).outcome == "reject"
def test_policy_violation_rejects():
    assert decide(risk(band="low",score=80), policy_bad(), delib_ok(), TABLE).outcome == "reject"
def test_blocking_flag_downgrades_to_review():
    d = decide(risk(band="low",score=80), policy_ok(), delib(flags=["affordability_borderline"]), TABLE)
    assert d.outcome == "review"
def test_clean_high_score_approves():
    assert decide(risk(band="low",score=80), policy_ok(), delib_ok(), TABLE).outcome == "approve"
def test_mid_score_reviews():
    assert decide(risk(band="medium",score=55), policy_ok(), delib_ok(), TABLE).outcome == "review"
```
- [ ] **Step 2: Chạy fail.**
- [ ] **Step 3: Implement** `decide(risk, policy, deliberation, table) -> Decision`:
  - knocked_out → reject. not policy.compliant → reject.
  - bất kỳ blocking flag có ánh xạ "reject" → reject; "review" → review.
  - score >= approve_min AND policy.compliant AND no blocking → approve.
  - score < review_min → reject. còn lại → review.
  - reasons gom từ risk.factors + policy.violations + flags.
- [ ] **Step 4: Chạy pass.**
- [ ] **Step 5: Commit** — `git commit -m "feat: decision gate (asymmetric backstop)"`

---

## Task 7: pii/anonymizer 🟢

**Files:** Create `src/loan_agent/pii/anonymizer.py`, `tests/test_pii.py`.

- [ ] **Step 1: Test:** `redact_text("SĐT 0901234567, CCCD 012345678901")` → không còn chuỗi số đó; email bị che; tên trong field bị thay token.
- [ ] **Step 2: Chạy fail.**
- [ ] **Step 3: Implement** — regex redact: SĐT VN (`0\d{9}`), CCCD/CMND (`\d{9,12}`), email; `anonymize_application(app)` bóc các field định danh → trả dict "sạch" + mapping (giữ nội bộ). Áp cho mọi payload trước khi gửi LLM.
- [ ] **Step 4: Chạy pass.** **Step 5: Commit** `feat: PII anonymizer`.

---

## Task 8: llm/base + mock + factory 🟢

**Files:** Create `src/loan_agent/llm/base.py`, `mock.py`, `factory.py`, `tests/test_llm_mock.py`.

- [ ] **Step 1: Test:** `MockLLM().structured(prompt, schema=AgentTurn)` trả AgentTurn hợp lệ; deterministic (gọi 2 lần ra giống nhau).
- [ ] **Step 2: Chạy fail.**
- [ ] **Step 3: Implement:**
  - `base.py`: `class LLMClient(Protocol)` với `complete(prompt)->str` và `structured(prompt, schema)->BaseModel`.
  - `mock.py`: `MockLLM` suy output từ nội dung prompt một cách deterministic (vd cho intake: trích field theo regex đơn giản; cho debate: stance/flags suy từ điểm số gắn trong prompt). Không random.
  - `factory.py`: `get_llm(settings)` → MockLLM nếu provider=mock, else OpenAILLM.
- [ ] **Step 4: Chạy pass.** **Step 5: Commit** `feat: LLM adapter + mock`.

---

## Task 9: llm/openai_client (THẬT) 🔴

**Files:** Create `src/loan_agent/llm/openai_client.py`.

- [ ] **Step 1:** Implement `OpenAILLM` dùng `langchain_openai.ChatOpenAI`; `structured()` dùng `.with_structured_output(schema)`; model rẻ cho analyst, `llm_decision_model` cho judge; đọc key từ settings; **ẩn danh PII trước khi gửi** (gọi anonymizer). Bọc try/except → raise lỗi rõ ràng (degrade ở node).
- [ ] **Step 2 (verify ngoài sandbox):** với key thật, `OpenAILLM().structured("...", AgentTurn)` trả model hợp lệ. Trong sandbox chỉ kiểm `python -c "import loan_agent.llm.openai_client"` OK.
- [ ] **Step 3: Commit** `feat: OpenAI LLM client`.

---

## Task 10: rag (base + keyword + chroma + ingest + factory) 🟢/🔴

**Files:** Create `src/loan_agent/rag/base.py`, `keyword_store.py`, `chroma_store.py`, `ingest.py`, `factory.py`, `tests/test_rag_keyword.py`.

- [ ] **Step 1: Test (keyword):** ingest 2 đoạn chính sách, `retrieve("điều kiện vay vốn", k=1)` trả đoạn liên quan + metadata (van_ban, dieu).
- [ ] **Step 2: Chạy fail.**
- [ ] **Step 3: Implement:**
  - `base.py`: `class PolicyStore(Protocol)` với `retrieve(query, k)->list[PolicyCitation]`.
  - `ingest.py`: `load_policies(dir)->list[dict]` đọc `data/policies/*.md`, chunk theo heading "## Điều", gắn metadata.
  - `keyword_store.py`: `KeywordStore` chấm điểm overlap từ khoá (offline, 🟢).
  - `chroma_store.py`: `ChromaStore` dùng `chromadb` + `OpenAIEmbeddings` (🔴, verify ngoài sandbox).
  - `factory.py`: `get_store(settings)` theo `rag_backend`.
- [ ] **Step 4: Chạy pass (keyword).** **Step 5: Commit** `feat: RAG stores (keyword + chroma)`.

---

## Task 11: agents/intake 🟢 (với mock)

**Files:** Create `src/loan_agent/agents/intake.py`, `tests/test_intake.py`.

- [ ] **Step 1: Test:** với MockLLM + tin nhắn "vay 10tr mua xe, lương 20tr", `extract_and_ask(state)` cập nhật application các field trích được, set câu hỏi tiếp nếu thiếu; đủ field → `ready=True`.
- [ ] **Step 2: Chạy fail.**
- [ ] **Step 3: Implement** `extract_and_ask(state, llm)`: gọi llm.structured để trích field từ messages, merge vào application, validate, nếu `missing_required_fields()` → sinh câu hỏi (giới hạn max_intake_turns); else `ready=True`. Đếm turns trong meta.
- [ ] **Step 4: Chạy pass.** **Step 5: Commit** `feat: intake agent`.

---

## Task 12: agents/deliberation 🟢 (với mock)

**Files:** Create `src/loan_agent/agents/deliberation.py`, `tests/test_deliberation.py`.

- [ ] **Step 1: Test:** `convene_check(risk, policy, table)` → "skip"/"light"/"full" đúng theo điểm; `run_deliberation(state, llm, store)` trả Deliberation có recommendation + blocking_flags + transcript (với MockLLM).
- [ ] **Step 2: Chạy fail.**
- [ ] **Step 3: Implement:**
  - `convene_check`: dùng table["convene"] + risk.score + policy + provenance(trust).
  - `run_deliberation`: nếu skip → Deliberation rỗng (no flags); nếu full → gọi llm cho từng vai (Risk/Advocate/Skeptic/Policy dùng store.retrieve) qua ≤2 vòng, rồi judge() tổng hợp → recommendation + blocking_flags + transcript. Cap vòng.
- [ ] **Step 4: Chạy pass.** **Step 5: Commit** `feat: deliberation council`.

---

## Task 13: state + nodes 🟢

**Files:** Create `src/loan_agent/state.py`, `src/loan_agent/nodes.py`.

- [ ] **Step 1:** `state.py`: `LoanState(TypedDict)` với messages (Annotated add), application(dict), provenance, affordability, risk, deliberation, policy, decision, case, meta.
- [ ] **Step 2:** `nodes.py`: hàm cho mỗi node — `bootstrap`, `intake`, `affordability` (dùng financial.max_affordable + counter-offer), `pre_checks` (compute_risk), `deliberation`, `decision_gate` (rules.gate.decide), `review_prep`, `finalize`. Mỗi node nhận/đọc state, trả patch dict. Inject llm/store qua closure/partials.
- [ ] **Step 3:** không test riêng (sẽ test qua graph smoke). **Commit** `feat: state + node functions`.

---

## Task 14: graph (LangGraph wiring) 🟢

**Files:** Create `src/loan_agent/graph.py`, `tests/test_smoke.py`.

- [ ] **Step 1: Test smoke:** `build_graph(llm=MockLLM, store=KeywordStore)` compile OK; chạy với 1 hồ sơ ĐỦ (complete) → kết thúc, có `decision.outcome` thuộc {approve,reject,review}.
- [ ] **Step 2: Chạy fail.**
- [ ] **Step 3: Implement** `build_graph(llm, store, checkpointer=None)`:
  - add nodes; edges: START→bootstrap→intake; intake conditional (ready? → affordability : END[chờ user]); affordability→pre_checks; pre_checks conditional (knocked_out? → decision_gate : deliberation); deliberation→decision_gate; decision_gate conditional (review? → review_prep→END : finalize→END).
  - checkpointer mặc định `MemorySaver` (SQLite tùy chọn).
- [ ] **Step 4: Chạy pass.** **Step 5: Commit** `feat: LangGraph wiring + smoke test`.

---

## Task 15: dữ liệu giả lập + CLI/demo 🟢

**Files:** Create `data/sample_applications.json`, `data/policies/tt39-trich.md`, `data/policies/vapp-policy-mau.md`, `src/loan_agent/cli.py`, `tests/test_demo.py`.

- [ ] **Step 1:** `sample_applications.json`: ≥3 hồ sơ — 1 đậu (lương cao, sạch), 1 rớt (knock-out/điểm thấp), 1 review (biên). Mỗi hồ sơ kèm `expected_outcome`.
- [ ] **Step 2:** policies: vài "## Điều" trích TT39 (điều kiện vay) + 1 policy Vapp mẫu.
- [ ] **Step 3: Test demo:** chạy từng hồ sơ qua graph (mock+keyword) → `decision.outcome == expected_outcome`.
- [ ] **Step 4:** `cli.py main()`: nạp config, build graph (factory theo env), nếu có arg file → chạy batch in kết quả; else hội thoại stdin.
- [ ] **Step 5: Chạy** `python tests/run.py` (toàn bộ xanh) + `python -m loan_agent.cli data/sample_applications.json`. **Commit** `feat: sample data + CLI demo`.

---

## Task 16: README cập nhật + dọn stub cũ 🟢

**Files:** Modify `README.md`; xóa docstring-only stub đã được thay bằng impl.

- [ ] **Step 1:** Cập nhật README phần "Chạy" cho khớp (mock mặc định, lệnh demo, đổi sang openai).
- [ ] **Step 2:** Bảo đảm không còn file stub trống nghĩa. **Commit** `docs: update README for runnable slice`.

---

## Self-Review (writing-plans)

**1. Spec coverage:** Tất cả thành phần trong spec §5 đều có task (schemas T2, config T3, financial T4, scorecard T5, gate T6, pii T7, llm T8-9, rag T10, intake T11, deliberation T12, state/nodes T13, graph T14, data/cli T15). Tiêu chí hoàn thành spec §10 ↔ T14/T15 (smoke + demo). ✅

**2. Placeholder scan:** Code deterministic (T4/T5/T6) có code đầy đủ. T9/T10-chroma là 🔴 (chỉ verify ngoài sandbox) — đã nêu rõ lý do, không phải placeholder ẩn. Các task lớn (T5/T11/T12) mô tả hành vi + interface cụ thể; code chi tiết điền khi thực thi theo TDD.

**3. Type consistency:** `RiskResult` dùng `score`,`band`,`knocked_out`,`factors` xuyên T5→T6→T12. `Decision.outcome` ∈ {approve,reject,review} (T2 enum) dùng nhất quán T6/T14/T15. `PolicyCitation` dùng ở T2/T10/T12. `Deliberation` có `recommendation`,`blocking_flags`,`transcript` (T2/T12/T6). ✅

## Execution Handoff
Sau khi duyệt plan, chọn cách thực thi:
1. **Subagent-Driven (khuyến nghị)** — mỗi task một subagent mới, review giữa các task.
2. **Inline (executing-plans)** — thực thi trong phiên này, có checkpoint review.
