# Architecture Decision Records (ADR)

Mỗi ADR ghi lại **một quyết định kiến trúc**: bối cảnh, lựa chọn, lý do và hệ quả.
ADR là bất biến — khi đổi quyết định, tạo ADR mới và đánh dấu cái cũ là
`Superseded` (thay thế bởi ADR-XXXX), không sửa lịch sử.

## Chỉ mục

| # | Quyết định | Trạng thái |
|---|-----------|-----------|
| [0001](0001-su-dung-langgraph.md) | Dùng LangGraph làm lớp điều phối | Accepted |
| [0002](0002-kien-truc-multi-agent.md) | Kiến trúc multi-agent có Supervisor | ⚠️ Superseded by 0021 |
| [0003](0003-intake-hoi-thoai-slot-filling.md) | Intake hội thoại theo slot-filling có schema | Accepted |
| [0004](0004-tach-tinh-toan-khoi-llm.md) | Tách tính toán tài chính khỏi LLM | Accepted |
| [0005](0005-rag-cho-chinh-sach.md) | RAG chỉ dùng cho chính sách cho vay | Accepted |
| [0006](0006-llm-provider-openai.md) | Dùng OpenAI làm LLM provider | Accepted |
| [0007](0007-structured-output-pydantic.md) | Structured output bằng Pydantic | Accepted |
| [0008](0008-human-in-the-loop.md) | Human-in-the-loop cho ca biên | Accepted |
| [0009](0009-ranh-gioi-trach-nhiem-quyet-dinh.md) | Rule engine ra quyết định cuối, LLM hỗ trợ | Accepted (tinh chỉnh bởi 0022) |
| [0010](0010-affordability-counter-offer.md) | Node Affordability — hạn mức tối đa & counter-offer | Accepted |
| [0011](0011-schema-2-tang.md) | Schema 2 tầng (core fields + review fields) | Accepted |
| [0012](0012-co-che-review.md) | Cơ chế Review — interrupt, case queue, resume | Accepted |
| [0013](0013-noi-phien-va-ttl.md) | Nối lại phiên & TTL cho hồ sơ dở | Accepted |
| [0014](0014-mo-hinh-rui-ro-scorecard.md) | Mô hình rủi ro: knock-out + scorecard, tham số hóa | Accepted |
| [0015](0015-lai-suat-co-dinh.md) | Lãi suất cố định (giai đoạn đầu) | Accepted |
| [0016](0016-vai-tro-rag-phu-tro.md) | RAG là phụ trợ, không trên đường quyết định cứng | Accepted |
| [0017](0017-api-contract.md) | Hợp đồng API: REST theo phiên + streaming + webhook | Accepted |
| [0018](0018-postgres-luu-tru.md) | Postgres làm xương sống lưu trữ | Accepted |
| [0019](0019-an-danh-pii.md) | Ẩn danh hóa PII trước khi gửi ra ngoài | Accepted |
| [0020](0020-trien-khai-docker-aws.md) | Triển khai Docker trên AWS | Accepted |
| [0021](0021-hoi-dong-tranh-luan.md) | Mô hình hội đồng tranh luận (debate multi-agent) | Accepted |
| [0022](0022-quyet-dinh-tranh-luan-co-cong.md) | Tranh luận + cổng xác định backstop (2b) | Accepted |
| [0023](0023-giao-thuc-tranh-luan.md) | Giao thức tranh luận: convene check + round-robin có cap | Accepted |

## Trạng thái có thể có

`Proposed` · `Accepted` · `Deprecated` · `Superseded by ADR-XXXX`

## Template

```markdown
# ADR-XXXX: <Tiêu đề quyết định>

- **Trạng thái:** Proposed | Accepted | Deprecated | Superseded by ADR-YYYY
- **Ngày:** YYYY-MM-DD

## Bối cảnh
Vấn đề là gì? Ràng buộc, yêu cầu liên quan?

## Quyết định
Chúng ta chọn làm gì?

## Lý do
Vì sao chọn cái này thay vì phương án khác?

## Phương án đã cân nhắc
- Phương án A — vì sao loại.
- Phương án B — vì sao loại.

## Hệ quả
Mặt lợi, mặt hại, và những gì phải đánh đổi.
```
