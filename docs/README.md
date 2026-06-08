# Tài liệu dự án — Hệ thống Agentic thẩm định cho vay

Hệ thống multi-agent quyết định **có cho người dùng vay hay không**, sử dụng
LangGraph (điều phối), RAG (tra cứu chính sách cho vay) và LLM (OpenAI).

## Cấu trúc thư mục

```
docs/
├── README.md                  # File này — chỉ mục tài liệu
├── design-review.md           # ⭐ Bản tóm tắt toàn thiết kế (đọc trước/trình bày)
├── requirements.md            # Yêu cầu chức năng & phi chức năng
├── architecture.md            # Kiến trúc tổng thể & các agent
├── data-schema.md             # Schema hồ sơ vay & slot-filling
├── risk-model.md              # Mô hình rủi ro: knock-out + scorecard
├── rag-design.md              # Thiết kế RAG (kho chính sách)
├── debate-protocol.md         # Giao thức hội đồng tranh luận (multi-agent)
├── integration-infra.md       # Tích hợp Vapp & hạ tầng (API, DB, deploy, PII)
├── data-requirements.md       # Yêu cầu dữ liệu + nguồn thật đã khảo sát
├── open-questions.md          # Câu hỏi mở cho Vapp/pháp chế (mang đi họp)
└── adr/                       # Architecture Decision Records
    ├── README.md              # Chỉ mục ADR + template
    ├── 0001-su-dung-langgraph.md
    ├── ...
    └── 0015-lai-suat-co-dinh.md   # (xem adr/README.md cho danh sách đầy đủ)
```

## Đọc theo thứ tự nào

0. [design-review.md](design-review.md) — ⭐ **đọc trước**: tóm tắt toàn thiết kế (1–2 trang).
1. [requirements.md](requirements.md) — hệ thống cần làm gì.
2. [architecture.md](architecture.md) — làm bằng cách nào (các agent, luồng).
3. [data-schema.md](data-schema.md) — dữ liệu vào/ra trông như thế nào.
4. [risk-model.md](risk-model.md) — quyết định cho vay được tính thế nào.
5. [rag-design.md](rag-design.md) — kho chính sách & cách tra cứu.
6. [debate-protocol.md](debate-protocol.md) — hội đồng agent tranh luận thế nào.
7. [integration-infra.md](integration-infra.md) — Vapp gọi thế nào & chạy ở đâu.
8. [data-requirements.md](data-requirements.md) — cần dữ liệu gì, lấy ở đâu.
9. [open-questions.md](open-questions.md) — còn vướng gì cần Vapp quyết.
10. [adr/](adr/) — vì sao chọn cách làm đó (lịch sử quyết định).

## Trạng thái

> Giai đoạn: **Thiết kế** — chưa có code. Tài liệu là nguồn sự thật cho
> những quyết định đã chốt trước khi triển khai.
