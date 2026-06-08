# Yêu cầu hệ thống (Requirements)

## 1. Mục tiêu

Xây dựng một hệ thống **agentic** quyết định **có cho người dùng vay hay không**.
Người dùng bắt đầu bằng một yêu cầu tự nhiên (ví dụ *"Tôi muốn vay 10 triệu"*),
hệ thống **hội thoại để khai thác thông tin**, sau đó thẩm định và đưa ra quyết
định kèm **lý do**.

> **Mục tiêu triển khai:** **Production** — tính năng này phục vụ trong ứng dụng
> **Vapp**. Vì là production (không phải demo), các yêu cầu về bảo mật, bảo vệ dữ
> liệu cá nhân, tuân thủ pháp lý, và giám sát vận hành là **bắt buộc** (xem mục 4
> và mục 4b bên dưới), không phải tùy chọn.

## 2. Phạm vi (Scope)

**Trong phạm vi:**
- Thu thập thông tin hồ sơ vay qua hội thoại (slot-filling có schema).
- Tính các chỉ số rủi ro tài chính (DTI, khả năng trả nợ…) bằng code.
- Tra cứu chính sách/quy định cho vay qua RAG.
- Ra quyết định: **Duyệt / Từ chối / Cần xét duyệt thủ công**, kèm giải thích.

**Ngoài phạm vi (giai đoạn đầu):**
- Tích hợp hệ thống ngân hàng/CIC thật.
- Giải ngân, hợp đồng, chữ ký số.
- Đa ngôn ngữ (mặc định tiếng Việt).

## 3. Yêu cầu chức năng (Functional)

| ID | Yêu cầu |
|----|---------|
| FR-1 | Nhận yêu cầu vay dạng ngôn ngữ tự nhiên làm điểm bắt đầu. |
| FR-2 | Hội thoại hỏi để lấp đầy các **trường bắt buộc** (xem `data-schema.md`). |
| FR-3 | Trích nhiều trường từ một câu trả lời (ví dụ "lương 20tr, kế toán 3 năm"). |
| FR-4 | Validate dữ liệu ngay khi thu thập (số tiền > 0, tuổi ≥ 18…); hỏi lại nếu sai. |
| FR-5 | Chỉ chuyển sang bước thẩm định khi **đủ trường bắt buộc và hợp lệ**. |
| FR-6 | Tính chỉ số rủi ro bằng công thức/code, **không để LLM tự đoán số**. |
| FR-7 | Đối chiếu hồ sơ với chính sách cho vay qua RAG. |
| FR-8 | Ra quyết định Duyệt / Từ chối / Cần xét duyệt + **lý do theo từng yếu tố**. |
| FR-9 | Chuyển ca biên (gray zone) sang **người xét duyệt** (human-in-the-loop). |
| FR-10 | Trả kết quả ở **định dạng có cấu trúc** (JSON theo schema). |
| FR-11 | Agent đóng vai **nhân viên tín dụng ảo**: hội thoại tự nhiên, dẫn dắt, giải thích (giọng thân thiện, chuyên nghiệp, không cam kết pháp lý). |
| FR-12 | Tính & thông báo **hạn mức vay tối đa** theo khả năng chi trả của user (ước tính, kèm cảnh báo "tham khảo"). |
| FR-13 | **Counter-offer**: nếu số tiền xin vượt khả năng, đề xuất mức tối đa khả thi hoặc kéo dài kỳ hạn. |
| FR-14 | **Schema 2 tầng**: chỉ hỏi *review fields* (thông tin sâu) khi hồ sơ rơi vào vùng xám cần xét duyệt. |
| FR-15 | Xử lý hội thoại lệch hướng: lạc đề, từ chối cung cấp, khai mâu thuẫn, cố lách (xem mục 7). |
| FR-16 | **Nối lại phiên**: user quay lại có thể tiếp tục hồ sơ đang dở (trong thời hạn TTL) hoặc làm mới. |

## 4. Yêu cầu phi chức năng (Non-functional)

| ID | Yêu cầu |
|----|---------|
| NFR-1 | **Explainability**: mọi quyết định phải truy vết được lý do (phục vụ audit). |
| NFR-2 | **Fairness**: không dùng yếu tố nhạy cảm (giới tính, tôn giáo, sắc tộc…) khi quyết định. |
| NFR-3 | **Tính đúng tài chính**: phép tính số phải chính xác, kiểm thử được. |
| NFR-4 | **Khả năng phục hồi**: lưu trạng thái hội thoại để resume (checkpointing). |
| NFR-5 | **Audit trail**: lưu lại đầu vào, các bước, và quyết định. |
| NFR-6 | **Chi phí/độ trễ**: model nhỏ cho tác vụ đơn giản, model mạnh cho quyết định. |
| NFR-7 | **An toàn**: chống prompt injection từ nội dung người dùng nhập. |

## 4b. Yêu cầu production cho Vapp (bắt buộc)

Vì hệ thống chạy thật trong Vapp, bổ sung các yêu cầu sau:

| ID | Yêu cầu |
|----|---------|
| PR-1 | **Bảo vệ dữ liệu cá nhân (PII)**: mã hóa khi lưu/truyền; tối thiểu hóa dữ liệu thu thập; có chính sách lưu trữ/xóa. |
| PR-2 | **Tuân thủ pháp lý**: bám quy định cho vay của Việt Nam (NHNN) và quy định bảo vệ dữ liệu người dùng. |
| PR-3 | **Observability**: logging, tracing (ví dụ LangSmith/OpenTelemetry), và metrics cho mỗi phiên & mỗi quyết định. |
| PR-4 | **Kiểm soát chi phí token**: hạn mức theo phiên, cảnh báo khi vượt ngưỡng. |
| PR-5 | **Rate limiting & chống lạm dụng**: giới hạn theo người dùng/phiên. |
| PR-6 | **Quản lý phiên bản model & prompt**: ghi lại model/prompt version dùng cho mỗi quyết định (phục vụ audit & rollback). |
| PR-7 | **Xử lý lỗi & degrade an toàn**: khi LLM/RAG lỗi → không tự ý Duyệt; mặc định an toàn (từ chối hoặc chuyển human). |
| PR-8 | **Kiểm thử & CI/CD**: unit test cho phần tính toán, regression test bộ hồ sơ mẫu, pipeline triển khai. |
| PR-9 | **Tích hợp Vapp**: định nghĩa API/giao diện để Vapp gọi hệ thống (cần chốt hợp đồng API). |
| PR-10 | **Bảo mật ứng dụng**: chống prompt injection, không lộ thông tin nhạy cảm/secret qua output của agent. |

## 5. Tiêu chí thành công (Success criteria)

- Có bộ hồ sơ mẫu **có nhãn** (duyệt/từ chối) để đo lường.
- Đo được: độ chính xác, tỉ lệ **duyệt sai** (false-approval), tỉ lệ chuyển human review.
- Mỗi quyết định đều kèm lý do người đọc hiểu được.

## 7. Xử lý hội thoại (guardrails) — FR-15

Agent đóng vai nhân viên nên phải xử lý được các tình huống hội thoại:

| Tình huống | Hướng xử lý |
|---|---|
| **Lạc đề** | Khóa phạm vi "chỉ về khoản vay" trong system prompt; lịch sự kéo về câu hỏi đang dở. |
| **Từ chối cung cấp** | Hỏi lại tối đa N lần → vẫn không có thì đánh dấu field "không cung cấp" → ép sang **Review** hoặc từ chối (không tự duyệt khi thiếu — PR-7). |
| **Khai mâu thuẫn** | Phát hiện chênh lệch với giá trị đã lưu → **xác nhận lại** trước khi ghi đè. |
| **Cố lách / gaming** | **Không lộ ngưỡng** quyết định; ưu tiên đối chiếu dữ liệu tin được; chống prompt injection (PR-10). |

## 8. Vận hành Review & nối phiên — FR-9, FR-14, FR-16

**Khi quyết định = Review (vùng xám):**
1. Thu thập thêm *review fields* (schema tầng 2).
2. Graph **interrupt + checkpoint**; tạo **case** kèm snapshot toàn bộ ngữ cảnh
   (hồ sơ, chỉ số rủi ro, trích dẫn chính sách, log hội thoại) đẩy vào **hàng đợi nhân viên**.
3. User nhận trạng thái "**đang xử lý**" + SLA.
4. Nhân viên quyết → **resume** graph từ checkpoint → trả kết quả về user.

**Nối lại phiên:**
- Checkpoint theo `user_id` + `application_id`; mở lại → "tiếp tục hồ sơ dở hay làm mới?".
- **TTL** cho hồ sơ dở (vd 7–30 ngày): dữ liệu tài chính quá hạn → bắt khai lại
  (tránh quyết định trên số liệu lỗi thời). Ca Review giữ lâu hơn (đang chờ người).

> Chi tiết kỹ thuật & lý do: xem ADR-0010 → ADR-0013.

## 9. Giả định & câu hỏi mở

**Đã chốt:**
- **Mục đích**: ✅ Production cho Vapp (mục 1 & 4b).
- **Mô hình rủi ro**: ✅ Knock-out + Scorecard, lãi cố định (ADR-0014, 0015).
- **Vai trò RAG**: ✅ Phụ trợ, nguồn tiếng Việt, embedding large (ADR-0016, rag-design).
- **API**: ✅ REST theo phiên + streaming + webhook (ADR-0017).
- **Lưu trữ**: ✅ Postgres xương sống (ADR-0018).
- **PII → OpenAI**: ✅ Ẩn danh trước khi gửi (ADR-0019) — *mức ẩn danh chờ pháp chế xác nhận*.
- **Triển khai**: ✅ Docker trên AWS (ADR-0020).

**Còn mở (cần Vapp/pháp chế):**
- **Dữ liệu Vapp có sẵn**: agent được đọc dữ liệu nào (KYC, thu nhập, giao dịch)? — ảnh hưởng Bootstrap + độ tin quyết định.
- **Dữ liệu mẫu/eval & tham số scorecard**: ai cung cấp, thật hay expert-set?
- **Kho chính sách RAG**: tài liệu thật chưa, định dạng (PDF/Word/web)?
- **Pháp chế**: mức ẩn danh PII có đủ tuân thủ Luật 91/2025 / NĐ 356/2025 & NHNN? Region AWS?
- **Chi tiết hợp đồng API** request/response với Vapp; chọn reranker RAG.
