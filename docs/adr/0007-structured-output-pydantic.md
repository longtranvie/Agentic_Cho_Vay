# ADR-0007: Structured output bằng Pydantic

- **Trạng thái:** Accepted
- **Ngày:** 2026-06-07

## Bối cảnh
Hồ sơ vay và quyết định cuối cần định dạng ổn định để các agent trao đổi, để
validate, và để audit. Parse text tự do từ LLM dễ vỡ và khó kiểm thử.

## Quyết định
Định nghĩa toàn bộ dữ liệu trao đổi (hồ sơ vay, kết quả rủi ro, quyết định) bằng
**Pydantic models**. LLM trả về theo schema qua **function calling / structured
output** của OpenAI.

## Lý do
- Validate tự động, lỗi sớm, rõ ràng (FR-10, FR-4).
- Hợp đồng dữ liệu tường minh giữa các agent.
- Dễ kiểm thử và serialize cho audit trail (NFR-5).

## Phương án đã cân nhắc
- **Parse JSON/text thủ công** — dễ vỡ, nhiều xử lý ngoại lệ.
- **Dict tự do** — không có validate, lỗi phát hiện muộn.

## Hệ quả
- (+) Dữ liệu nhất quán, có validate, dễ test.
- (−) Phải bảo trì schema khi yêu cầu thay đổi.
