# ADR-0010: Node Affordability — tính hạn mức tối đa & counter-offer

- **Trạng thái:** Accepted
- **Ngày:** 2026-06-07

## Bối cảnh
Agent đóng vai nhân viên tín dụng (FR-11). Khi user nói số tiền muốn vay, một
nhân viên giỏi sẽ cho biết ngay *"bạn có thể vay tối đa khoảng X"* và đề xuất
phương án nếu số xin quá cao. Đây là trải nghiệm mong muốn (FR-12, FR-13).

## Quyết định
Tạo một **node Affordability riêng**, chạy **sớm** (ngay khi có thu nhập + nợ +
kỳ hạn), **trước** bước Risk/Decision đầy đủ. Node này:
- Tính **hạn mức gốc tối đa** bằng **phép tính ngược** từ ngưỡng DTI cho phép
  (deterministic, không LLM — nhất quán [ADR-0004](0004-tach-tinh-toan-khoi-llm.md)).
- Nếu số xin > hạn mức → tạo **counter-offer** (giảm số tiền hoặc kéo dài kỳ hạn).
- Kết quả là **ước tính tham khảo**, KHÔNG phải quyết định cho vay.

## Lý do
- Trải nghiệm "nhân viên thật": minh bạch, hữu ích ngay từ đầu hội thoại.
- Là node riêng (không gộp vào Risk) vì mục đích khác nhau: Affordability phục vụ
  **hội thoại** (báo cho user); Risk phục vụ **quyết định**. Tách giúp chạy sớm
  và test độc lập.
- Phép tính thuần → tái lập, kiểm thử được.

## Phương án đã cân nhắc
- **Gộp vào Risk** — chậm (phải đợi đủ thông tin để thẩm định) và lẫn lộn mục đích.
- **Để LLM ước lượng** — sai số, không nhất quán. Loại ([ADR-0004](0004-tach-tinh-toan-khoi-llm.md)).

## Hệ quả
- (+) Counter-offer & minh bạch hạn mức; tái sử dụng công thức trả góp.
- (−) Phải nói rõ "ước tính, chưa phải cam kết duyệt" để tránh hiểu nhầm pháp lý.
- (−) Hạn mức phụ thuộc ngưỡng DTI & lãi suất mẫu → cần Vapp xác nhận (PR-2).
