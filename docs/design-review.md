# Bản review thiết kế — Hệ thống Agentic thẩm định cho vay (Vapp)

> Tóm tắt toàn bộ thiết kế để trình bày/duyệt. Chi tiết từng phần ở các tài liệu
> liên kết. Trạng thái: **thiết kế xong, chưa code.**

## 1. Hệ thống là gì
Một hệ thống **multi-agent** đóng vai **nhân viên tín dụng ảo**: user nói nhu cầu
("tôi muốn vay 10tr"), hệ thống **hội thoại khai thác thông tin**, **báo hạn mức tối
đa**, rồi một **hội đồng agent tranh luận** phân tích hồ sơ; quyết định cuối (Duyệt
/ Từ chối / Cần xét duyệt) do một **cổng luật xác định** đưa ra, kèm lý do. Production
cho **Vapp**.

## 2. Luồng hệ thống

```
Bootstrap → Intake (hội thoại) → Affordability (hạn mức) → Pre-checks (knock-out+điểm số)
   → HỘI ĐỒNG TRANH LUẬN (Risk/Advocate/Skeptic/Policy, Judge điều phối)
   → DECISION GATE (xác định) → Duyệt / Từ chối / Review → (Review) Human-in-the-loop
```
Chi tiết: [architecture.md](architecture.md).

## 3. Nguyên tắc cốt lõi (vì sao thiết kế thế này)

| Nguyên tắc | Nghĩa là | ADR |
|---|---|---|
| **Quyết định xác định** | Agent tranh luận để *phân tích*; luật chốt cuối → tái lập & audit được | [0009](adr/0009-ranh-gioi-trach-nhiem-quyet-dinh.md), [0022](adr/0022-quyet-dinh-tranh-luan-co-cong.md) |
| **Tranh luận chỉ làm chặt hơn** | Agent có thể đẩy xuống Review/Từ chối, **không tự duyệt** vượt luật cứng | [0022](adr/0022-quyet-dinh-tranh-luan-co-cong.md) |
| **Số do code, không do LLM** | DTI/điểm tính bằng Python, kiểm thử được | [0004](adr/0004-tach-tinh-toan-khoi-llm.md), [0014](adr/0014-mo-hinh-rui-ro-scorecard.md) |
| **Degrade an toàn** | LLM/RAG lỗi → không bao giờ auto-duyệt | PR-7 |
| **RAG là phụ trợ** | Điều kiện cứng ở config; RAG để trích dẫn/hỗ trợ người | [0016](adr/0016-vai-tro-rag-phu-tro.md) |
| **Tham số hóa & version** | Ngưỡng/bảng điểm/lãi ở config do rủi ro+pháp chế sở hữu | [0014](adr/0014-mo-hinh-rui-ro-scorecard.md) |

## 4. Mô hình ra quyết định
**Knock-out (loại thẳng) + Scorecard (chấm điểm) + Hội đồng tranh luận**, kết hợp ở
**Decision Gate** theo luật bất đối xứng (duyệt cần hội đủ điểm số *và* tranh luận
đồng thuận; bất kỳ rủi ro nào cũng đủ để hạ xuống Review/Từ chối). KHÔNG dùng ML giai
đoạn đầu (Vapp chưa có dữ liệu lịch sử) — có lộ trình tiến tới ML.
Chi tiết: [risk-model.md](risk-model.md), [debate-protocol.md](debate-protocol.md).

## 5. Stack công nghệ

| Lớp | Chọn |
|---|---|
| Điều phối | LangGraph (state machine + checkpoint) |
| LLM | OpenAI (function calling); model rẻ cho analyst, mạnh cho Judge |
| RAG | embedding `text-embedding-3-large`, hybrid + rerank, pgvector |
| Schema | Pydantic (structured output) |
| Lưu trữ | Postgres (checkpoint + audit + case + vector); SQLite cho dev |
| API | REST theo phiên + streaming + webhook |
| Triển khai | Docker trên AWS (ECS/Fargate, RDS, SQS, S3, CloudWatch) |
| Bảo mật | Ẩn danh PII trước khi gửi ra ngoài; Secrets Manager |
Chi tiết: [integration-infra.md](integration-infra.md).

## 6. Dữ liệu & pháp lý (điểm cần chú ý)

- **Chính sách (RAG):** văn bản NHNN công khai có sẵn (TT39/12-2024/43/18-2019, NĐ13);
  chính sách nội bộ Vapp cần cấp thêm.
- **Dữ liệu vay-trả thật tiếng Việt:** không công khai (CIC đóng) → dev dùng proxy
  (Home Credit) + dữ liệu giả lập.
- **⚠️ Pháp lý (quan trọng nhất):** Nghị định 13 — dữ liệu tài chính = **nhạy cảm**;
  gửi OpenAI = **chuyển ra nước ngoài** (cần đánh giá tác động + báo Bộ Công an +
  đồng ý người dùng + DPA). **Ẩn danh là cần nhưng có thể chưa đủ.**
Chi tiết: [data-requirements.md](data-requirements.md), [ADR-0019](adr/0019-an-danh-pii.md).

## 7. Blocker — cần Vapp/pháp chế quyết trước khi production

| # | Việc | Mức |
|---|---|---|
| L1 | PII→OpenAI: đường (I) tuân thủ cross-border đầy đủ hay (II) giữ PII trong nước? | 🔴 |
| L2 | Loại hình pháp lý của Vapp (quyết chế độ TT39/TT43, trần 100tr) | 🔴 |
| D1 | Ai cấp bộ config quyết định (bảng điểm/ngưỡng/lãi) | 🔴 |
| D2 | Tài liệu chính sách nội bộ Vapp (cho RAG) | 🔴 |
Danh sách đầy đủ: [open-questions.md](open-questions.md).

## 8. Trạng thái & bước tiếp
- **Đã xong:** 10 tài liệu thiết kế + 23 ADR, neo vào văn bản pháp luật thật.
- **Chưa làm:** code (chờ chốt thiết kế); gỡ blocker với Vapp.
- **Có thể bắt đầu:** dựng **skeleton** với expert-set + dữ liệu giả lập, song song
  đưa L1/L2/D1/D2 cho Vapp.
