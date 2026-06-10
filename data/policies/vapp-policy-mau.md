# Chính sách cho vay tiêu dùng Vapp (BẢN POC — MẪU GIẢ LẬP)

> ⚠️ **BẢN POC do dev dựng để demo** — KHÔNG phải chính sách tín dụng chính thức của Vapp.
> Mục tiêu: có một chính sách **đầy đủ** để hệ thống tra cứu/trích dẫn khi chưa được cấp
> tài liệu thật. Giá trị số khớp `decision_table.json` phiên bản `fintech-research-1`
> (xem [docs/decision-table-rationale.md]). Chỗ đánh dấu **[Vapp chốt]** là quyết định
> kinh doanh **bắt buộc rủi ro + pháp chế Vapp rà & ký** trước khi cho vay tiền thật.
> Bối cảnh: Vapp = **fintech vay tiêu dùng tín chấp** (không tài sản bảo đảm).

## Điều 1. Đối tượng và điều kiện vay
Khách hàng cá nhân đã định danh điện tử (eKYC) trên Vapp, có năng lực hành vi dân sự đầy
đủ, **tuổi 20–60** tại thời điểm vay, cư trú hợp pháp tại Việt Nam. Thu nhập hợp pháp,
tối thiểu **4.500.000đ/tháng** (neo lương tối thiểu vùng 2026 — NĐ 293/2025). Mục đích
vay hợp pháp (Điều 7 [tt39-hopnhat-2026.md]).

## Điều 2. Danh mục sản phẩm và hạn mức
Cho vay tiêu dùng **không tài sản bảo đảm** bằng đồng Việt Nam. Tổng dư nợ một khách hàng
tại Vapp **không vượt 100.000.000đ** (khoản vay giá trị nhỏ — TT 12/2024; trần cho vay
tiêu dùng công ty tài chính — Điều 3 [tt43-2016.md]). Khung sản phẩm POC:

| Sản phẩm | Hạn mức | Kỳ hạn |
|---|---|---|
| Vay tiêu dùng nhanh | 3 – 30 triệu | 3 – 12 tháng |
| Vay tiêu dùng tiêu chuẩn | 30 – 100 triệu | 6 – 36 tháng |

*[Vapp chốt] danh mục sản phẩm, hạn mức/kỳ hạn từng loại theo khẩu vị rủi ro thật.*

## Điều 3. Hồ sơ và chứng từ
Tối thiểu: định danh eKYC (sinh trắc học khi áp dụng — TT 12/2024), thông tin thu nhập,
đồng ý tra cứu CIC. Khoản vay nhỏ được **giảm nhẹ** yêu cầu phương án sử dụng vốn (TT
12/2024) nhưng vẫn phải chứng minh khả năng tài chính (Điều 9 [tt39-hopnhat-2026.md]).
*[Vapp chốt] chứng từ thu nhập bắt buộc (sao kê lương / xác minh việc làm).*

## Điều 4. Khả năng trả nợ (DTI)
Tổng nghĩa vụ trả nợ hằng tháng (dư nợ cũ + khoản đề nghị) trên thu nhập tháng — chỉ số
DTI — **không vượt 60%**; vượt là loại (knock-out) do rủi ro vỡ nợ tăng mạnh.

## Điều 5. Lãi suất và phí
Lãi suất cố định **18%/năm**, dưới trần **20%/năm** (Điều 468 [blds-2015.md]); tính trên
dư nợ thực tế và thời gian vay thực tế (Điều 13 [tt39-hopnhat-2026.md]). Lãi nợ quá hạn
≤ **150%** lãi trong hạn; lãi trên lãi chậm trả ≤ **10%/năm**. Minh bạch toàn bộ phí,
không thu phí ẩn. *[Vapp chốt] phí trả trước hạn, phí dịch vụ (nếu có).*

## Điều 6. Mục đích vay bị từ chối
Không cho vay cho nhu cầu bị cấm tại Điều 8 [tt39-hopnhat-2026.md]: ngành nghề bị cấm,
**mua vàng miếng**, đảo nợ tại chính tổ chức cho vay, gửi tiền, góp vốn/mua phần vốn
doanh nghiệp chưa niêm yết. Hồ sơ rơi vào nhóm này gắn cờ `regulatory_concern` → từ chối.

## Điều 7. Lịch sử tín dụng và phân loại nợ
Tham chiếu nhóm nợ CIC theo [tt11-2021.md]. Khách đang có **nợ nhóm 3–5 (nợ xấu)** bị từ
chối. Lịch sử trễ hạn làm giảm điểm thiện chí khi chấm điểm.

## Điều 8. Phòng chống gian lận
Tín hiệu nghi vấn: dữ liệu **mâu thuẫn logic** (vd thâm niên > số năm có thể đi làm), danh
tính không khớp eKYC, hành vi bất thường → gắn cờ `data_inconsistency` / `fraud_signal`
→ chuyển xét duyệt thủ công hoặc từ chối. *[Vapp chốt] bộ quy tắc phát hiện gian lận.*

## Điều 9. Quy trình thẩm định và quyết định
Mỗi hồ sơ được **chấm điểm 0–100** (khả năng trả + thiện chí): **≥70 đề xuất duyệt ·
40–69 chuyển xét duyệt thủ công · <40 từ chối**. Theo Điều 17 [tt39-hopnhat-2026.md]:
**tách chức năng thẩm định khỏi quyết định cho vay**; thông báo lý do khi khách yêu cầu.
Quyết định cuối do **bộ quy tắc tất định** đưa ra, không do mô hình ngôn ngữ.

## Điều 10. Phân quyền phê duyệt và ngoại lệ
- Điểm **≥75 + sạch chính sách** → hệ thống **tự duyệt** (qua hội đồng rà soát rút gọn).
- Điểm 40–74 hoặc có cờ rủi ro → **nhân viên xét duyệt** quyết.
- **Ngoại lệ** (duyệt vượt chuẩn) → cấp **quản lý rủi ro** phê duyệt, **ghi nhật ký** đầy
  đủ lý do. *[Vapp chốt] ngưỡng hạn mức theo cấp phê duyệt.*

## Điều 11. Xử lý nợ quá hạn và thu hồi
Phân loại nợ theo [tt11-2021.md]. Đôn đốc, thu hồi nợ theo [tt43-2016.md] (sửa bởi TT
18/2019): **không đe dọa**, **không nhắc nợ với người không có nghĩa vụ trả** (người
thân, đồng nghiệp), số lần nhắc/ngày trong giới hạn quy định, bảo mật thông tin khách.
*[Vapp chốt] quy trình cơ cấu nợ / miễn giảm lãi.*

## Điều 12. Khẩu vị rủi ro
Mục tiêu kiểm soát chất lượng danh mục; rà soát ngưỡng chấm điểm và bộ số định kỳ theo
dữ liệu vay-trả thật. *[Vapp chốt] mục tiêu tỷ lệ nợ xấu (POC tham chiếu nháp: < 4%) và
chu kỳ hiệu chỉnh scorecard.*

## Điều 13. Minh bạch, đồng ý và quyền của khách hàng
Quyết định được **xử lý tự động** — Vapp thông báo việc xử lý tự động, giải thích nguyên
tắc, và bảo đảm quyền khách hàng theo NĐ 356/2025 ([nd356-2025.md]):
- **Đồng ý trước khi xử lý** dữ liệu (kiểm chứng được, không mặc định — Điều 6).
- **Rút lại đồng ý** bất cứ lúc nào (không hồi tố phần đã xử lý).
- **Yêu cầu nhân viên xét duyệt lại** quyết định tự động.

Dữ liệu cá nhân thu thập trên cơ sở đồng ý, lưu trữ và bảo vệ theo Luật 91/2025 + NĐ
356/2025; chuyển dữ liệu ra nước ngoài (nếu có) tuân thủ Điều 25.
