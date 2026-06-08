# ADR-0015: Lãi suất cố định (giai đoạn đầu)

- **Trạng thái:** Accepted
- **Ngày:** 2026-06-07

## Bối cảnh
Affordability ([ADR-0010](0010-affordability-counter-offer.md)) và việc ước tính
trả góp cần một lãi suất. Có hai hướng: lãi cố định theo sản phẩm, hoặc risk-based
pricing (lãi thay đổi theo rủi ro).

## Quyết định
Dùng **lãi suất cố định** theo sản phẩm cho giai đoạn đầu. Mức lãi là **tham số
config có version** ([ADR-0014](0014-mo-hinh-rui-ro-scorecard.md)), tuân trần lãi
theo quy định NHNN (do pháp chế Vapp nạp).

## Lý do
- Đơn giản, dễ giải thích cho user và dễ audit.
- Affordability/Decision không phụ thuộc một biến lãi động → quyết định ổn định hơn.
- Risk-based pricing cần dữ liệu rủi ro đáng tin (PD) — chưa có ở giai đoạn này.

## Phương án đã cân nhắc
- **Risk-based pricing** — linh hoạt, tối ưu lợi nhuận/rủi ro, nhưng phức tạp,
  cần mô hình PD và minh bạch pháp lý. Để xem lại khi có dữ liệu (cùng lộ trình ML).

## Hệ quả
- (+) Đơn giản, minh bạch, dễ tính hạn mức.
- (−) Không tối ưu theo từng mức rủi ro; chấp nhận đánh đổi này ở giai đoạn đầu.
