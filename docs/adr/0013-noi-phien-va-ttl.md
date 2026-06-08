# ADR-0013: Nối lại phiên & TTL cho hồ sơ dở

- **Trạng thái:** Accepted
- **Ngày:** 2026-06-07

## Bối cảnh
User có thể bỏ giữa chừng rồi mở Vapp lại. Cần quyết định: tiếp tục hồ sơ cũ hay
làm lại? Đồng thời dữ liệu tài chính cũ (thu nhập, nợ) có thể đã lỗi thời.

## Quyết định
- **Checkpoint theo `user_id` + `application_id`** (dùng checkpointer LangGraph).
- Mở lại → hỏi user "**tiếp tục hồ sơ đang dở hay làm mới?**" kèm tóm tắt.
- Áp **TTL** cho hồ sơ dở (vd 7–30 ngày): quá hạn → buộc khai lại các trường tài
  chính (tránh quyết định trên số liệu cũ). Ca Review giữ lâu hơn (đang chờ người),
  vẫn có hạn riêng.

## Lý do
- Trải nghiệm tốt: không bắt làm lại từ đầu (FR-16).
- An toàn quyết định: số liệu tài chính phải đủ mới mới đáng tin (NFR-3).
- Tái dùng cơ chế checkpoint vốn đã có ([ADR-0001](0001-su-dung-langgraph.md)).

## Phương án đã cân nhắc
- **Luôn làm lại từ đầu** — an toàn dữ liệu nhưng trải nghiệm kém.
- **Giữ vô thời hạn** — tiện nhưng rủi ro quyết định trên số liệu lỗi thời.

## Hệ quả
- (+) Cân bằng trải nghiệm & độ tin dữ liệu.
- (−) Cần định nghĩa TTL cụ thể (phối hợp Vapp) và logic làm mới trường quá hạn.
