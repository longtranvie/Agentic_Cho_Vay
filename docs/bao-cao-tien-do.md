# Báo cáo tiến độ — Hệ thống Agent thẩm định cho vay (Vapp)

**Ngày:** 08/06/2026 · **Người báo cáo:** (Long) · **Giai đoạn:** Thiết kế + Bản chạy thử lõi (vertical slice)

---

## 1. Tóm tắt cho lãnh đạo (đọc 30 giây)

Đã hoàn thành **toàn bộ thiết kế hệ thống** và một **bản chạy thử end-to-end** của lõi
thẩm định: nhập thông tin người vay qua hội thoại → tính khả năng trả nợ → chấm điểm
rủi ro → ra quyết định **Duyệt / Từ chối / Cần xét duyệt tay**. Phần lõi đã có **kiểm
thử tự động đầy đủ (44/44 đạt)** và chạy được offline.

Để lên **production thật cho Vapp**, còn 3 nhóm việc: (a) dựng phần vỏ ngoài kết nối Vapp
(API, cơ sở dữ liệu, triển khai cloud); (b) xác nhận tích hợp AI thật (OpenAI + tìm kiếm
chính sách); (c) **4 quyết định từ phía Vapp/pháp chế/rủi ro** mà kỹ thuật không được tự
quyết. **Nhóm (c) là đường găng — cần lãnh đạo hỗ trợ thúc đẩy.**

> **Mức hoàn thiện:** Lõi nghiệp vụ & thiết kế ~90% · Toàn hệ thống đến mốc production **~35–40%**.

---

## 2. Đã làm được gì (kết quả bàn giao được)

| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| Tài liệu thiết kế + 23 quyết định kiến trúc (ADR) | ✅ Hoàn thành | Phục vụ kiểm toán pháp lý về sau |
| Lõi quyết định tất định (tính trả nợ, chấm điểm, lớp loại thẳng, cổng quyết định) | ✅ Hoàn thành + kiểm thử | Quyết định **bằng quy tắc**, không để AI tự duyệt |
| Quy trình điều phối đa-agent (hội thoại khai thác → hội đồng phân tích → ra quyết định) | ✅ Chạy thử end-to-end | Có cơ chế "hội đồng tranh luận" để soi ca rủi ro |
| Ẩn danh dữ liệu cá nhân trước khi gửi AI | ✅ Hoàn thành | Tuân thủ Nghị định 13/2023 |
| Kiểm thử tự động | ✅ **44/44 đạt** | Chạy được không cần mạng |

**Nguyên tắc thiết kế then chốt:** AI chỉ **hội thoại và phân tích**; **con số và quyết
định cuối do bộ quy tắc tất định** đảm nhiệm. Đây là lựa chọn bắt buộc với sản phẩm tài
chính (tránh AI "ảo giác" duyệt sai, đảm bảo giải trình được khi thanh tra).

---

## 3. Còn thiếu để lên production

| Hạng mục | Mức hiện tại | Vì sao cần |
|---|---|---|
| **Xác nhận tích hợp AI thật** (OpenAI + tìm kiếm chính sách) | Code đã viết, **chưa chạy thật lần nào** | Môi trường dev bị proxy chặn; cần mạng sạch để kiểm chứng |
| **Cơ sở dữ liệu lưu trữ** (PostgreSQL) | Mới có thiết kế | Hiện restart là **mất hồ sơ dở** — không chấp nhận được ở production |
| **API kết nối Vapp** | Mới có thiết kế | Vapp cần điểm kết nối để gọi vào hệ thống |
| **Triển khai cloud** (Docker + AWS) | Mới có thiết kế | Đưa hệ thống lên môi trường vận hành |
| **Lớp chất lượng & vận hành** (bộ đo chuẩn, giám sát, hàng đợi xét duyệt tay) | Mới có thiết kế | Đảm bảo độ chính xác + theo dõi khi chạy thật |

> Lưu ý quan trọng: **các phần còn thiếu chủ yếu là "vỏ ngoài", không phải sửa lõi.**
> Lõi nghiệp vụ đã ổn định và có kiểm thử.

---

## 4. ⛔ Quyết định cần Vapp ra — ĐƯỜNG GĂNG (cần lãnh đạo thúc đẩy)

Đây là phần **chặn tiến độ lớn nhất** và nằm ngoài tầm quyết của kỹ thuật:

| Mã | Nội dung cần quyết | Hỏi ai | Vì sao gấp |
|---|---|---|---|
| **L1** | Dữ liệu cá nhân gửi sang OpenAI: chọn **(I) tuân thủ cross-border đầy đủ** (xin đồng ý + hồ sơ đánh giá tác động gửi Bộ Công an + ký DPA) hay **(II) giữ dữ liệu trong nước** (dùng model nội bộ)? | **Pháp chế** | Hai hướng = **hai kiến trúc khác nhau**. Quyết muộn → phải làm lại phần lõi gọi AI |
| **L2** | Vapp là **ngân hàng / công ty tài chính / fintech trung gian**? | **Pháp chế** | Quyết định trần vay (vd 100tr/khách), quy tắc loại, tài liệu áp dụng |
| **D1** | **Ai cấp bộ tham số quyết định** (bảng điểm, ngưỡng duyệt, lãi suất)? | **Bộ phận Rủi ro** | Đây là **chính sách tín dụng** — kỹ thuật không được tự đặt (rủi ro pháp lý + tiền thật). Hiện đang dùng số mẫu, **không được lên production** với số mẫu |
| **D2** | **Tài liệu chính sách nội bộ Vapp** đã có dạng văn bản chưa? | **Sản phẩm/Pháp chế** | Để hệ thống trích dẫn đúng chính sách riêng của Vapp, không chỉ luật chung |

> **Đề xuất:** L1 + L2 hỏi pháp chế **cùng một buổi, càng sớm càng tốt** (vì có thể đổi
> kiến trúc). D1 + D2 thu thập **song song**.

---

## 5. Rủi ro chính

- **Rủi ro pháp lý (cao):** Chưa chốt L1/L2 mà code tiếp phần kết nối AI → nguy cơ làm lại.
  *Giảm thiểu:* chốt L1/L2 trước khi dựng vỏ ngoài.
- **Rủi ro "số chưa được duyệt" (cao):** Tham số quyết định hiện là giá trị mẫu của kỹ
  thuật. *Giảm thiểu:* không go-live tới khi Rủi ro Vapp ký duyệt (D1).
- **Rủi ro tích hợp AI chưa kiểm chứng (trung bình):** *Giảm thiểu:* việc này kỹ thuật
  chủ động xử lý được ngay khi có mạng sạch.

---

## 6. Đề xuất bước tiếp theo

| Ưu tiên | Việc | Phụ thuộc | Ai làm |
|---|---|---|---|
| 1 | Xác nhận tích hợp AI thật trên mạng sạch | (không) | Kỹ thuật — **làm ngay** |
| 2 | Họp pháp chế chốt **L1 + L2** | Lãnh đạo sắp lịch | Pháp chế + Kỹ thuật |
| 3 | Thu thập **D1** (tham số) + **D2** (tài liệu) | (song song) | Rủi ro + Sản phẩm |
| 4 | Dựng vỏ ngoài tối thiểu (API + cơ sở dữ liệu) | **Sau khi có L1** | Kỹ thuật |
| 5 | Triển khai cloud + lớp giám sát/chất lượng | Sau bước 4 | Kỹ thuật + Hạ tầng |

> *Ước lượng thời gian sẽ chốt được sau khi gỡ L1 (vì L1 quyết khối lượng phần lõi AI).*

---

## 7. Đề nghị lãnh đạo hỗ trợ

1. **Sắp lịch họp pháp chế** để chốt L1 + L2 — đây là đường găng số 1.
2. **Chỉ định đầu mối bộ phận Rủi ro** để cấp tham số quyết định (D1).
3. **Xác nhận** tài liệu chính sách nội bộ Vapp ở dạng văn bản (D2).

*Chi tiết kỹ thuật đầy đủ: xem `docs/` (requirements, architecture, các ADR, open-questions).*
