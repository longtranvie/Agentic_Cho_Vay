# ADR-0017: Hợp đồng API — REST theo phiên + streaming + webhook

- **Trạng thái:** Accepted
- **Ngày:** 2026-06-07

## Bối cảnh
Vapp (đã xác thực user) gọi hệ thống thẩm định. Đây là **hội thoại nhiều lượt**
(intake → affordability → quyết định), có ca **Review** chờ người (bất đồng bộ).

## Quyết định
**REST API theo phiên (session-based):**

```
POST /applications                 → tạo phiên (kèm user_id), trả application_id
POST /applications/{id}/messages   → gửi tin nhắn user, nhận phản hồi agent + trạng thái
GET  /applications/{id}            → lấy trạng thái/kết quả hiện tại
POST /applications/{id}/resume     → (nội bộ) nhân viên quyết xong → nối tiếp ca Review
```

- **Streaming** từng token cho phản hồi hội thoại qua **SSE/WebSocket** (agent đóng
  vai nhân viên trò chuyện — FR-11 — nên hiện chữ dần như chat).
- **Webhook**: ca Review trả ngay trạng thái "đang xử lý"; khi người quyết xong,
  hệ thống **callback** về Vapp (hoặc Vapp poll `GET`).
- **Xác thực dịch vụ** Vapp↔hệ thống (API key/JWT/mTLS); `user_id` do Vapp truyền
  (đã xác thực phía Vapp). Có **request id/idempotency** cho an toàn gọi lại.

## Lý do
- REST đơn giản, phổ biến, đủ dùng; không cần gRPC ở giai đoạn này.
- Session khớp bản chất hội thoại nhiều lượt + cơ chế checkpoint (ADR-0013).
- Webhook khớp ca Review bất đồng bộ (ADR-0012) — không bắt user chờ đồng bộ.

## Phương án đã cân nhắc
- **gRPC** — nhanh hơn nhưng phức tạp, chưa cần.
- **Một request đồng bộ duy nhất** — không hợp hội thoại nhiều lượt & ca Review.

## Hệ quả
- (+) Giao tiếp rõ ràng, hợp hội thoại + Review; trải nghiệm chat mượt.
- (−) Cần hạ tầng streaming + webhook; phải định nghĩa hợp đồng request/response chi tiết với Vapp.
