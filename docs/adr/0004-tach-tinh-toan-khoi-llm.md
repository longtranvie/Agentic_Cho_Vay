# ADR-0004: Tách tính toán tài chính khỏi LLM

- **Trạng thái:** Accepted
- **Ngày:** 2026-06-07

## Bối cảnh
Quyết định cho vay phụ thuộc vào các chỉ số tài chính (DTI, khả năng trả nợ, tỉ
lệ khoản vay/thu nhập…). LLM nổi tiếng dễ sai số học và không nhất quán.

## Quyết định
Mọi **phép tính số** được thực hiện bằng **code Python (tools)** với công thức
tường minh. LLM chỉ **điều phối** và **diễn giải** kết quả, không tự tính số.

## Lý do
- Đảm bảo tính đúng tài chính, kết quả tái lập được (NFR-3).
- Công thức kiểm thử được bằng unit test.
- Giảm rủi ro "ảo số" ảnh hưởng trực tiếp tới quyết định tiền bạc.

## Phương án đã cân nhắc
- **Để LLM tự tính** — đơn giản nhưng rủi ro sai số cao, không kiểm thử được.

## Hệ quả
- (+) Số liệu chính xác, có test, audit rõ ràng.
- (−) Phải viết và bảo trì các hàm tính + bộ test tương ứng.
