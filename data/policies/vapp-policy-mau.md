# Chính sách cho vay tiêu dùng Vapp (BẢN NHÁP DEV — MẪU GIẢ LẬP)

> ⚠️ **MẪU GIẢ LẬP do dev dựng** để hệ thống có chính sách sản phẩm tra cứu được, KHÔNG
> phải chính sách tín dụng chính thức của Vapp. Các con số khớp `decision_table.json`
> phiên bản `fintech-research-1` (xem [docs/decision-table-rationale.md]) và CHƯA được
> bộ phận **rủi ro + pháp chế Vapp** duyệt (open-questions D1/D2). Phải có chữ ký Vapp
> trước khi cho vay tiền thật. Bối cảnh: Vapp = **fintech vay tiêu dùng** (L2).

## Điều 1. Đối tượng và điều kiện vay
Khách hàng cá nhân đã định danh điện tử (eKYC) trên Vapp, có năng lực hành vi dân sự đầy
đủ, độ tuổi **từ 20 đến 60** tại thời điểm vay. Thu nhập hợp pháp ổn định, tối thiểu
**4.500.000đ/tháng** (neo theo lương tối thiểu vùng 2026 — NĐ 293/2025). Mục đích vay
hợp pháp (Điều 7 [tt39-hopnhat-2026.md]).

## Điều 2. Sản phẩm và hạn mức
Cho vay tiêu dùng không tài sản bảo đảm bằng đồng Việt Nam. **Tổng dư nợ một khách hàng
tại Vapp không vượt quá 100.000.000đ** — thuộc nhóm "khoản vay có giá trị nhỏ" (TT
12/2024 dẫn Điều 102.2 Luật Các TCTD 2024) và phù hợp trần cho vay tiêu dùng của công ty
tài chính (Điều 3 [tt43-2016.md]). Kỳ hạn theo khung sản phẩm, thường 3–36 tháng.

## Điều 3. Khả năng trả nợ (DTI)
Tổng nghĩa vụ trả nợ hằng tháng (dư nợ cũ + khoản vay đề nghị) trên thu nhập tháng — chỉ
số DTI — **không vượt quá 60%**. Vượt ngưỡng này bị loại (knock-out) vì rủi ro vỡ nợ tăng
mạnh. Khoản vay nhỏ được giảm nhẹ yêu cầu phương án sử dụng vốn (TT 12/2024), nhưng vẫn
phải chứng minh khả năng tài chính (Điều 7 [tt39-hopnhat-2026.md]).

## Điều 4. Lãi suất
Lãi suất cố định **18%/năm**, dưới trần **20%/năm** của Điều 468 [blds-2015.md] áp cho
quan hệ vay. Lãi tính trên dư nợ thực tế và thời gian vay thực tế (Điều 13
[tt39-hopnhat-2026.md]). Lãi nợ quá hạn không vượt 150% lãi trong hạn; lãi trên lãi chậm
trả không vượt 10%/năm.

## Điều 5. Mục đích vay bị từ chối
Không cho vay cho các nhu cầu bị cấm tại Điều 8 [tt39-hopnhat-2026.md]: ngành nghề bị
cấm, mua vàng miếng, đảo nợ tại chính tổ chức cho vay, gửi tiền, góp vốn/mua phần vốn
doanh nghiệp chưa niêm yết. Hồ sơ rơi vào nhóm này gắn cờ `regulatory_concern` → từ chối.

## Điều 6. Lịch sử tín dụng
Tham chiếu nhóm nợ tại CIC theo [tt11-2021.md]. Khách hàng đang có **nợ nhóm 3–5 (nợ
xấu)** bị từ chối. Từng trễ hạn (nhóm 2 hoặc lịch sử trễ) làm giảm điểm thiện chí trong
chấm điểm.

## Điều 7. Quy trình ra quyết định
Mỗi hồ sơ được **chấm điểm 0–100** (khả năng trả + thiện chí): **≥70 đề xuất duyệt ·
40–69 chuyển xét duyệt thủ công · <40 từ chối**. Hồ sơ điểm ≥75 và sạch chính sách chỉ
qua hội đồng rà soát rút gọn. Theo Điều 17 [tt39-hopnhat-2026.md]: **tách chức năng thẩm
định khỏi quyết định cho vay**, và **thông báo lý do khi khách hàng yêu cầu**. Quyết định
cuối do bộ quy tắc tất định đưa ra, không do mô hình ngôn ngữ.

## Điều 8. Minh bạch và dữ liệu cá nhân
Quyết định được **xử lý tự động** — Vapp thông báo cho khách hàng việc xử lý tự động,
giải thích nguyên tắc, và bảo đảm **quyền yêu cầu nhân viên xét duyệt lại** (NĐ
356/2025 — xem [nd356-2025.md]). Dữ liệu cá nhân được thu thập trên cơ sở đồng ý, lưu
trữ và bảo vệ theo Luật 91/2025 + NĐ 356/2025.
