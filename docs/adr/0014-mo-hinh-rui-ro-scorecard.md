# ADR-0014: Mô hình rủi ro — Knock-out + Scorecard (tham số hóa, có version)

- **Trạng thái:** Accepted
- **Ngày:** 2026-06-07

## Bối cảnh
Cần chọn cách rule engine ([ADR-0009](0009-ranh-gioi-trach-nhiem-quyet-dinh.md))
ra quyết định. Đã phân tích 3 hướng: (A) rule ngưỡng if/else, (B) scorecard chấm
điểm, (C) ML credit model. Vapp là sản phẩm mới → **chưa có dữ liệu vay-trả lịch
sử**, và là production tài chính VN → bắt buộc **giải thích được + audit + fairness**.

## Quyết định
Mô hình rủi ro gồm **2 lớp, đều xác định (deterministic), không LLM**:

1. **Lớp Knock-out (loại thẳng)** — chạy trước. Vi phạm điều kiện cứng → từ chối
   / bất hợp lệ ngay, không cần chấm điểm (vd: tuổi ngoài khoảng, thu nhập = 0,
   vi phạm chính sách cứng, nợ xấu CIC khi có tích hợp).
2. **Lớp Scorecard (B)** — với hồ sơ qua được knock-out: mỗi yếu tố cộng/trừ điểm
   theo trọng số → tổng điểm rơi vào dải → Duyệt / Review / Từ chối.

Scorecard tính **cả hai chiều rủi ro**: **khả năng trả** (capacity: DTI, hạn mức —
liên quan [ADR-0010](0010-affordability-counter-offer.md)) và **thiện chí trả**
(willingness: lịch sử trả nợ, ổn định việc làm). Một chiều tốt không che được
chiều kia.

**Tham số hóa & version:** toàn bộ ngưỡng knock-out, bảng điểm, dải điểm, và các
con số pháp lý (trần lãi, giới hạn theo NHNN) nằm ở **decision table dạng config
có version** (PR-6), do bộ phận rủi ro & pháp chế Vapp sở hữu — đổi không cần sửa
code logic.

**Lộ trình tiến tới ML (C):** giai đoạn đầu trọng số do chuyên gia đặt
(expert-set); khi Vapp tích đủ dữ liệu vay-trả → hiệu chỉnh trọng số; sau nữa có
thể thêm ML chạy **shadow mode** để so sánh trước khi dùng. Phần "tính điểm rủi
ro" được tách sau một interface để đổi cách tính bên trong mà output không đổi.

## Lý do
- Cold-start: chưa có data lịch sử → loại C ở giai đoạn này (yếu tố quyết định,
  không phải sở thích).
- Scorecard mềm dẻo hơn rule thuần (không "vách đá"), vẫn giải thích được bằng
  reason codes — hợp ADR-0009 và NFR-1, NFR-2.
- Knock-out cứng ở chỗ cần cứng; scorecard mềm ở chỗ cần mềm.
- Tham số hóa → pháp chế/rủi ro làm chủ con số đúng luật, kỹ thuật không quyết hộ.

## Phương án đã cân nhắc
- **A. Rule ngưỡng thuần** — đơn giản nhưng cứng, khó mở rộng nhiều yếu tố. Dùng
  một phần ở lớp knock-out, không dùng cho phần chấm điểm chính.
- **C. ML ngay** — bất khả thi do thiếu dữ liệu; nặng giải thích & pháp lý. Để sau.

## Hệ quả
- (+) Quyết định xác định, giải thích được, audit & version được; mở đường cho ML.
- (−) Cần thiết kế & bảo trì bảng điểm; trọng số ban đầu là ước lượng chuyên gia,
  phải theo dõi và hiệu chỉnh dần.
- (−) Cần Vapp cung cấp/duyệt bộ tham số (xem [data-requirements](../data-requirements.md) — nhóm B).
