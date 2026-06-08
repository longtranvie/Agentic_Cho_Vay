# ADR-0003: Intake hội thoại theo slot-filling có schema

- **Trạng thái:** Accepted
- **Ngày:** 2026-06-07

## Bối cảnh
Người dùng bắt đầu bằng yêu cầu tự nhiên (*"Tôi muốn vay 10 triệu"*). Cần khai
thác đủ thông tin trước khi thẩm định, nhưng hội thoại tự do dễ hỏi lan man,
thiếu/thừa thông tin, hoặc rơi vào vòng lặp.

## Quyết định
Intake là **agent hội thoại** nhưng bị ràng buộc bởi một **schema trường bắt
buộc** (slot-filling). Agent loop: còn thiếu trường → hỏi tiếp; **đủ + hợp lệ →
mới chuyển bước**. Quyết định "đã đủ thông tin chưa" dựa trên **schema**, không
để LLM tự phán.

## Lý do
- Giữ trải nghiệm hội thoại tự nhiên nhưng đảm bảo bước sau luôn đủ dữ liệu (FR-5).
- Kiểm soát được, dễ đoán, dễ kiểm thử.
- Validate sớm tránh dữ liệu rác lọt xuống thẩm định (FR-4).

## Phương án đã cân nhắc
- **Form cứng** — kiểm soát tốt nhưng trải nghiệm kém, mất ưu thế của agentic.
- **LLM tự quyết đã đủ thông tin chưa** — linh hoạt nhưng khó đoán, dễ thiếu/thừa.
  → Loại cho bản đầu; có thể xem xét lại sau khi có dữ liệu vận hành.

## Hệ quả
- (+) Hội thoại tự nhiên + đảm bảo đủ dữ liệu; loop có giới hạn.
- (−) Phải bảo trì schema trường bắt buộc (xem `../data-schema.md`).
