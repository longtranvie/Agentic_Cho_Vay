# Agentic thẩm định cho vay (Vapp)

Hệ thống multi-agent quyết định có cho vay hay không: hội thoại khai thác thông tin
→ hội đồng agent tranh luận phân tích → cổng luật xác định ra quyết định.

> **Trạng thái: SKELETON** — đang dựng khung (cấu trúc thư mục + file stub). Logic
> sẽ điền sau khi duyệt cấu trúc. Thiết kế đầy đủ ở [docs/](docs/) (đọc
> [docs/design-review.md](docs/design-review.md) trước).

## Cấu trúc

```
src/loan_agent/
├── config.py            # cấu hình (env) + nạp decision table
├── schemas.py           # Pydantic models (ADR-0007)
├── state.py             # state của LangGraph (ADR-0001)
├── graph.py             # build graph: nodes + edges (ADR-0001/0021/0023)
├── nodes.py             # hàm từng node
├── cli.py               # chạy thử một phiên
├── tools/financial.py   # phép tính thuần, deterministic (ADR-0004)
├── rules/
│   ├── scorecard.py     # knock-out + chấm điểm (ADR-0014)
│   └── gate.py          # Decision Gate backstop (ADR-0022)
├── llm/                 # adapter LLM: base + mock + openai (ADR-0006/0019)
├── pii/anonymizer.py    # ẩn danh PII trước egress (ADR-0019)
├── rag/store.py         # truy hồi chính sách (ADR-0005/0016)
└── agents/
    ├── intake.py        # nhân viên ảo, slot-filling (ADR-0003/0011)
    └── deliberation.py  # hội đồng tranh luận (ADR-0021/0023)

config/decision_table.json   # tham số quyết định (expert-set, có version)
data/                        # dữ liệu giả lập: applications + policies
tests/                       # test deterministic core (+ runner không cần pytest)
docs/                        # tài liệu thiết kế + ADR
```

## Chạy (sau khi điền logic)

```bash
pip install -r requirements.txt          # (môi trường hiện chặn mạng)
cp .env.example .env                      # mặc định LLM provider = mock (offline)
python -m loan_agent.cli                  # chạy thử một phiên
python tests/run.py                       # chạy test (không cần pytest)
```

## Nguyên tắc thiết kế (tóm tắt)
- Quyết định **xác định** (rule engine), agent tranh luận chỉ **phân tích** (ADR-0009/0022).
- **Số do code**, không do LLM (ADR-0004). **Degrade an toàn**: lỗi → không auto-duyệt.
- **Ẩn danh PII** trước khi gửi ra ngoài (ADR-0019). Tham số ở **config có version**.
