# Spec — Hệ thống Agentic thẩm định cho vay (Vapp)

- **Ngày:** 2026-06-08
- **Trạng thái:** Draft, chờ user review
- **Nền tảng:** consolidate từ `docs/` (architecture, risk-model, rag-design,
  debate-protocol, integration-infra) + ADR 0001–0023. Spec này là đầu vào cho
  `writing-plans`.

## 1. Mục tiêu

Hiện thực **bản code production-grade** của hệ thống: pipeline thẩm định cho vay
multi-agent (hội thoại → hội đồng tranh luận → cổng quyết định xác định), với
**tích hợp thật** OpenAI + RAG (Chroma local). `mock` LLM và `keyword` RAG là
**test double** để chạy & verify **offline** (không cần key/mạng).

## 2. Phạm vi

**Trong phạm vi:**
- Schemas (Pydantic) cho toàn bộ hợp đồng dữ liệu.
- Deterministic core: tools/financial, rules/scorecard (knock-out + chấm điểm),
  rules/gate (Decision Gate bất đối xứng).
- Config-as-data: `config/decision_table.json` (expert-set, có version).
- LLM adapter: `base` (interface) + `openai_client` (THẬT) + `mock` (test double).
- RAG: `base` (interface) + `chroma_store` (THẬT: chromadb + OpenAI embeddings) +
  `keyword_store` (test double offline).
- PII anonymizer (chạy trước mọi egress).
- Agents: intake (slot-filling) + deliberation (hội đồng tranh luận, convene check).
- Graph LangGraph: nodes + edges + state + checkpointer (SQLite dev).
- CLI/demo + tests deterministic (+ runner không cần pytest).
- Dữ liệu giả lập: hồ sơ mẫu + tài liệu chính sách mẫu.

**Ngoài phạm vi (hoãn — phụ thuộc blocker/hạ tầng):**
- API server (FastAPI) + webhook; hàng đợi human-review; Postgres/pgvector;
  LangSmith; giá trị config thật (D1); kho chính sách thật (D2); quyết định đường
  PII I/II (L1); loại hình Vapp (L2).

## 3. Ràng buộc môi trường (quan trọng)

- Sandbox hiện **chặn mạng + chưa có OpenAI key** → code tích hợp thật **viết được
  nhưng KHÔNG chạy/verify** ở đây. Verify ở máy có key/mạng.
- **Verify được offline ngay:** deterministic core (financial/scorecard/gate) +
  pipeline chạy với `mock` LLM + `keyword` RAG.
- `chromadb` đã cài; `langchain_chroma` chưa có → dùng `chromadb` trực tiếp.

## 4. Kiến trúc (tham chiếu)

Luồng: Bootstrap → Intake → Affordability → Pre-checks (knock-out + scorecard)
→ Deliberation (convene check + hội đồng) → Decision Gate → Review/Human.
Chi tiết & lý do: `docs/architecture.md`, ADR-0021/0022/0023.

**Nguyên tắc bất biến:** quyết định cuối **xác định** (Gate); tranh luận chỉ
**phân tích** (chỉ làm chặt hơn, không tự duyệt); **số do code**; **degrade an
toàn** (LLM/RAG lỗi → không auto-duyệt); **ẩn danh PII** trước egress;
**config là dữ liệu** có version.

## 5. File structure (khoá quyết định phân rã — đầu vào cho writing-plans)

```
src/loan_agent/
├── config.py              # Settings(env) + load decision_table.json
├── schemas.py             # Pydantic models (mọi hợp đồng dữ liệu)
├── state.py               # TypedDict state cho LangGraph
├── tools/financial.py     # monthly_payment, dti, lti, max_affordable (thuần)
├── rules/
│   ├── scorecard.py       # knock_out() + score() đọc config
│   └── gate.py            # decide() — luật bất đối xứng
├── llm/
│   ├── base.py            # LLMClient Protocol + structured() helper
│   ├── openai_client.py   # THẬT (ChatOpenAI)
│   └── mock.py            # test double deterministic
├── pii/anonymizer.py      # redact_text() + anonymize_application()
├── rag/
│   ├── base.py            # PolicyStore Protocol: retrieve()
│   ├── chroma_store.py    # THẬT (chromadb + OpenAIEmbeddings)
│   ├── keyword_store.py   # test double offline
│   └── ingest.py          # nạp data/policies → store
├── agents/
│   ├── intake.py          # extract_and_ask()
│   └── deliberation.py    # convene_check() + run_debate() + judge()
├── nodes.py               # hàm node cho graph
├── graph.py               # build_graph(): wiring + conditional edges
└── cli.py                 # chạy thử một phiên (mock mặc định)

config/decision_table.json # expert-set (placeholder, có version)
data/sample_applications.json · data/policies/*.md
tests/ test_financial.py · test_scorecard.py · test_gate.py · run.py
```

**Factory chọn backend** (qua `config`): `LOAN_LLM_PROVIDER=mock|openai`,
`LOAN_RAG_BACKEND=keyword|chroma`. Đổi backend = đổi env, không sửa caller.

## 6. Data flow & state
State giữ: messages, application, provenance, affordability, risk, deliberation
(transcript), policy, decision, case, meta. Xem `docs/architecture.md §3`.

## 7. Error handling / degrade an toàn (PR-7)
- LLM/RAG timeout/lỗi/output sai schema → set cờ, **không bao giờ** dẫn tới approve;
  cùng lắm đẩy **Review**.
- Mọi gọi LLM bọc try/validate; structured output qua Pydantic (ADR-0007).
- Deterministic core không phụ thuộc LLM → luôn chạy được.

## 8. Testing
- **TDD** cho deterministic core: financial (công thức), scorecard (knock-out +
  điểm theo config), gate (bảng chân lý outcome). Chạy bằng `tests/run.py` (không
  cần pytest) — tương thích pytest sau.
- **Smoke offline:** chạy `cli`/demo với `mock` + `keyword` trên hồ sơ mẫu → ra
  đúng nhãn kỳ vọng (đậu/rớt/review).
- Tích hợp OpenAI/Chroma: verify ở máy có key (ngoài sandbox).

## 9. Placeholder (đánh dấu rõ trong code)
- `config/decision_table.json`: giá trị minh họa, chờ rủi ro Vapp (D1).
- `data/policies/`: vài Điều mẫu, chờ tài liệu thật (D2).
- `openai_client`: đường PII mặc định = ẩn danh (ADR-0019); đường I/II chờ L1.

## 10. Tiêu chí hoàn thành (lát cắt này)
- `tests/run.py` xanh (financial/scorecard/gate).
- `python -m loan_agent.cli` chạy hết pipeline với mock → in quyết định + lý do +
  transcript cho ≥3 hồ sơ mẫu (đậu/rớt/review).
- Đổi `LOAN_LLM_PROVIDER=openai` + key (ngoài sandbox) → chạy được với OpenAI thật
  mà không sửa code orchestration.
