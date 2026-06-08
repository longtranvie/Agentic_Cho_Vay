# ADR-0019: Ẩn danh hóa PII trước khi gửi ra dịch vụ ngoài

- **Trạng thái:** Accepted — ⚠️ cần pháp chế quyết đường (I)/(II), xem mục "Cập nhật"
- **Ngày:** 2026-06-07
- **Liên quan:** ràng buộc lựa chọn [ADR-0006](0006-llm-provider-openai.md); thỏa PR-1, PR-10, NFR-7

## Bối cảnh
Hệ thống dùng OpenAI (máy chủ nước ngoài). Hồ sơ vay chứa **PII nhạy cảm** (danh
tính, CCCD, SĐT, thu nhập, nợ). Chuyển PII ra nước ngoài đụng **Nghị định 13/2023
về bảo vệ DLCN** và quy định bảo mật khách hàng tài chính của NHNN.

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
- **OpenAI zero-retention, gửi nguyên PII** — dữ liệu vẫn rời VN, rủi ro Nghị định 13.
- **Model nội bộ/self-host cho phần PII (hybrid)** — an toàn nhất nhưng phức tạp,
  đi ngược lựa chọn OpenAI. Giữ làm phương án dự phòng.

## Hệ quả
- (+) Dùng được OpenAI với rủi ro PII thấp hơn nhiều; thiết kế áp cho mọi egress.
- (−) Ẩn danh **không tuyệt đối 100%** (redact văn bản tự do là bài toán khó); còn
  rủi ro tồn dư → **vẫn cần pháp chế Vapp xác nhận** mức ẩn danh có đủ tuân thủ không.
- (−) Thêm lớp xử lý (detection/redaction) + chi phí; cần test độ phủ redaction.

## ⚠️ Cập nhật theo khảo sát Nghị định 13/2023 (toàn văn)

Khảo sát văn bản thật cho thấy **ẩn danh là cần nhưng có thể CHƯA ĐỦ**:
- **Điều 2.4.h**: thông tin khách hàng của TCTD (định danh, tài khoản, tiền gửi…)
  là **dữ liệu cá nhân NHẠY CẢM** → bảo vệ tăng cường (Điều 28).
- **Điều 25 (chuyển ra nước ngoài)**: nếu gửi sang OpenAI thì cần **Hồ sơ đánh giá
  tác động**, gửi **Bộ Công an trong 60 ngày**, **sự đồng ý** người dùng (Điều 11:
  rõ ràng; im lặng ≠ đồng ý), và **văn bản ràng buộc/DPA** với bên nhận.
- **Không có miễn trừ rõ ràng cho dữ liệu ẩn danh.** Trong một phiên thẩm định, dữ
  liệu luôn gắn với người định danh được (phải quyết định *về chính người đó*);
  pseudonym có mapping ⇒ vẫn là dữ liệu cá nhân.

→ Câu hỏi cho pháp chế **không còn là "ẩn danh đủ chưa"** mà là chọn 1 trong 2 đường:

- **(I) Tuân thủ cross-border đầy đủ:** xin **đồng ý người dùng** + lập **hồ sơ đánh
  giá tác động** + ký **DPA với OpenAI** (+ vẫn ẩn danh để giảm thiểu). Giữ được OpenAI.
- **(II) Giữ PII trong nước (hybrid):** phần chạm PII xử lý bằng model nội bộ/self-host;
  OpenAI chỉ lo phần không-PII. An toàn nhất, phức tạp hơn.

**Ẩn danh (quyết định ở trên) vẫn áp dụng trong cả hai đường** như biện pháp giảm
thiểu, nhưng không thay thế việc chọn (I)/(II). Quyết định cuối thuộc pháp chế Vapp.
