# ADR-0019: Ẩn danh hóa PII trước khi gửi ra dịch vụ ngoài

- **Trạng thái:** Accepted — **Vapp chọn đường (I): OpenAI + tuân thủ cross-border đầy đủ** (2026-06-08). Xem mục "Cập nhật".
- **Ngày:** 2026-06-07
- **Liên quan:** ràng buộc lựa chọn [ADR-0006](0006-llm-provider-openai.md); thỏa PR-1, PR-10, NFR-7

## Bối cảnh
Hệ thống dùng OpenAI (máy chủ nước ngoài). Hồ sơ vay chứa **PII nhạy cảm** (danh
tính, CCCD, SĐT, thu nhập, nợ). Chuyển PII ra nước ngoài đụng **Luật Bảo vệ dữ liệu
cá nhân 2025 (số 91/2025/QH15) và Nghị định 356/2025/NĐ-CP** (hiệu lực 01/01/2026,
thay Nghị định 13/2023) cùng quy định bảo mật khách hàng tài chính của NHNN.

## Quyết định
**Ẩn danh hóa (anonymize/pseudonymize) dữ liệu TRƯỚC khi gửi ra bất kỳ dịch vụ
ngoài nào** — không chỉ OpenAI mà cả **observability (LangSmith), log**:
- Bóc **định danh trực tiếp** (tên, CCCD/CMND, SĐT, địa chỉ) ra khỏi payload; thay
  bằng token/pseudonym. Mapping pseudonym ↔ danh tính **chỉ giữ nội bộ** (Postgres).
- Chỉ gửi **dữ liệu cần cho suy luận** (vd: "thu nhập 20tr, nợ 5tr, kỳ hạn 12 tháng").
- **Redact PII trong văn bản tự do**: user có thể tự gõ tên/SĐT trong chat → phải
  có lớp phát hiện & che PII trên message gửi ra (outbound).
- Lớp gọi LLM **tách riêng (adapter)** để đổi cách xử lý/đổi provider mà không sửa
  toàn hệ thống.

## Lý do
- Giảm mạnh rủi ro pháp lý khi vẫn dùng được OpenAI (theo lựa chọn của chủ dự án).
- Nguyên tắc nhất quán: **mọi dữ liệu rời hệ thống đều phải sạch PII** (kể cả trace/log).

## Phương án đã cân nhắc
- **OpenAI zero-retention, gửi nguyên PII** — dữ liệu vẫn rời VN, rủi ro theo Luật 91/2025 / NĐ 356/2025.
- **Model nội bộ/self-host cho phần PII (hybrid)** — an toàn nhất nhưng phức tạp,
  đi ngược lựa chọn OpenAI. Giữ làm phương án dự phòng.

## Hệ quả
- (+) Dùng được OpenAI với rủi ro PII thấp hơn nhiều; thiết kế áp cho mọi egress.
- (−) Ẩn danh **không tuyệt đối 100%** (redact văn bản tự do là bài toán khó); còn
  rủi ro tồn dư → **vẫn cần pháp chế Vapp xác nhận** mức ẩn danh có đủ tuân thủ không.
- (−) Thêm lớp xử lý (detection/redaction) + chi phí; cần test độ phủ redaction.

## ⚠️ Cập nhật theo Luật 91/2025 + Nghị định 356/2025 (hiệu lực 01/01/2026)

> Sửa 2026-06-08: Nghị định 13/2023 đã **hết hiệu lực**, thay bằng **Luật BVDLCN 2025
> (91/2025/QH15)** + **NĐ 356/2025/NĐ-CP**. Số Điều dưới đây theo NĐ356 — đối chiếu
> bản chính thức (chinhphu.vn) khi làm việc với pháp chế.

Văn bản hiện hành cho thấy **ẩn danh là cần nhưng có thể CHƯA ĐỦ**:
- **Dữ liệu nhạy cảm (NĐ356 Điều 4)**: **thông tin tài chính, tín dụng** được liệt kê
  rõ là **dữ liệu cá nhân nhạy cảm** → nghĩa vụ bảo vệ tăng cường.
- **Chuyển ra nước ngoài**: gửi sang OpenAI cần **Hồ sơ đánh giá tác động chuyển dữ
  liệu xuyên biên giới** (mục đích, loại dữ liệu, biện pháp bảo mật, đánh giá rủi ro),
  **nộp trong 60 ngày**, kèm **sự đồng ý** người dùng và **DPA** với bên nhận.
- **Sự đồng ý (NĐ356 Điều 6)**: phải **kiểm chứng được**; **cấm mặc định đồng ý**; với
  dữ liệu nhạy cảm phải thông báo rõ đó là dữ liệu nhạy cảm.
- **MỚI — Lĩnh vực tài chính-ngân hàng**: phải **ghi nhật ký toàn bộ hoạt động xử lý**
  + **thông báo sự cố lộ/mất dữ liệu nhạy cảm trong 72 giờ**.
- **MỚI — Xử lý tự động & AI**: hệ thống quyết định cho vay tự động phải **thông báo cho
  người dùng về việc xử lý tự động** và **giải thích nguyên tắc hoạt động của thuật
  toán** → ảnh hưởng thiết kế phần giải trình quyết định (gắn với trích dẫn chính sách).
- **Không có miễn trừ rõ ràng cho dữ liệu ẩn danh.** Trong một phiên thẩm định, dữ liệu
  luôn gắn với người định danh được; pseudonym có mapping ⇒ vẫn là dữ liệu cá nhân.

→ Câu hỏi cho pháp chế **không còn là "ẩn danh đủ chưa"** mà là chọn 1 trong 2 đường:

- **(I) Tuân thủ cross-border đầy đủ:** xin **đồng ý người dùng** + lập **hồ sơ đánh
  giá tác động** + ký **DPA với OpenAI** (+ vẫn ẩn danh để giảm thiểu). Giữ được OpenAI.
- **(II) Giữ PII trong nước (hybrid):** phần chạm PII xử lý bằng model nội bộ/self-host;
  OpenAI chỉ lo phần không-PII. An toàn nhất, phức tạp hơn.

**Ẩn danh (quyết định ở trên) vẫn áp dụng trong cả hai đường** như biện pháp giảm
thiểu, nhưng không thay thế việc chọn (I)/(II).

**→ Quyết định 2026-06-08: Vapp chọn đường (I)** — giữ OpenAI + tuân thủ cross-border
đầy đủ (đồng ý người dùng + hồ sơ đánh giá tác động + DPA với OpenAI). Kiến trúc LLM
giữ nguyên. Nghĩa vụ phát sinh phải code/thực hiện: luồng **đồng ý** onboarding,
**ghi nhật ký xử lý**, **thông báo xử lý tự động + giải thích thuật toán** (NĐ356), quy
trình **báo sự cố 72h**. Thủ tục nộp Bộ Công an + ký DPA là việc của **pháp chế Vapp**.
