# Agentic thẩm định cho vay (Vapp)

Hệ thống multi-agent quyết định có cho vay hay không: hội thoại khai thác thông tin
→ hội đồng agent tranh luận phân tích → cổng luật xác định ra quyết định.

> **Trạng thái: VERTICAL SLICE chạy được** (mock LLM + keyword RAG, offline). Tích
> hợp thật OpenAI + Chroma đã code sẵn, bật bằng env (cần API key + mạng để chạy).
> Thiết kế đầy đủ ở [docs/](docs/) — đọc [docs/design-review.md](docs/design-review.md)
> và [docs/superpowers/](docs/superpowers/) (spec + plan).

## Chạy

```bash
# (tùy chọn) cài deps nếu chạy OpenAI/Chroma thật:
pip install -r requirements.txt

# Demo offline (mock + keyword, KHÔNG cần key/mạng):
PYTHONPATH=src python -m loan_agent.cli data/sample_applications.json

# Test (runner không cần pytest):
python tests/run.py        # 42 test

# Chạy với OpenAI thật (máy có key):
#   set LOAN_LLM_PROVIDER=openai, LOAN_RAG_BACKEND=chroma, OPENAI_API_KEY=...
```

## Cấu trúc

```
src/loan_agent/
├── config.py            # Settings(env) + load_decision_table()
├── schemas.py           # Pydantic models (ADR-0007)
├── state.py             # LoanState cho LangGraph (ADR-0001)
├── graph.py             # build_graph(): nodes + conditional edges
├── nodes.py             # hàm từng node
├── cli.py               # chạy thử (batch)
├── tools/financial.py   # phép tính thuần, deterministic (ADR-0004)
├── rules/
│   ├── scorecard.py     # knock-out + chấm điểm (ADR-0014)
│   └── gate.py          # Decision Gate bất đối xứng (ADR-0022)
├── llm/                 # base + mock (offline) + openai_client (thật) + factory
├── pii/anonymizer.py    # ẩn danh PII trước egress (ADR-0019)
├── rag/                 # base + keyword (offline) + chroma (thật) + ingest + factory
└── agents/
    ├── intake.py        # nhân viên ảo, slot-filling (ADR-0003/0011)
    └── deliberation.py  # hội đồng tranh luận + convene check (ADR-0021/0023)

config/decision_table.json   # tham số expert-set, có version (chờ D1 duyệt)
data/                        # hồ sơ mẫu + tài liệu chính sách mẫu
tests/                       # 42 test + runner
docs/                        # thiết kế + 23 ADR + spec/plan
```

## Nguyên tắc thiết kế
- Quyết định **xác định** (rule engine); agent tranh luận chỉ **phân tích** — chỉ làm
  chặt hơn, không tự duyệt (ADR-0009/0022).
- **Số do code**, không do LLM (ADR-0004). **Degrade an toàn**: lỗi → không auto-duyệt.
- **Ẩn danh PII** trước khi gửi ra ngoài (ADR-0019). Tham số ở **config có version**.
- Đổi backend (mock↔openai, keyword↔chroma) = **đổi env, không sửa caller**.
