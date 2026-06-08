# ADR-0021: Mô hình hội đồng tranh luận (debate multi-agent)

- **Trạng thái:** Accepted
- **Ngày:** 2026-06-07
- **Thay thế:** [ADR-0002](0002-kien-truc-multi-agent.md) (supervisor pipeline tĩnh)

## Bối cảnh
ADR-0002 thiết kế multi-agent kiểu **pipeline tĩnh** (các node phối hợp gián tiếp
qua state — blackboard). Chủ dự án muốn các agent **hội thoại/tranh luận trực tiếp
với nhau** (hướng "2" trong brainstorm) để có tính agentic cao hơn, chấp nhận đánh
đổi — nhưng vẫn giữ quyết định cuối an toàn (xem [ADR-0022](0022-quyet-dinh-tranh-luan-co-cong.md)).

## Quyết định
Phần phân tích hồ sơ dùng **mô hình hội đồng tranh luận**: nhiều agent LLM có vai
riêng **đọc & phản biện lập luận của nhau** qua N vòng, điều phối bởi một
**Moderator/Judge**:

- **Risk Analyst** — phân tích định tính rủi ro từ số liệu & hồ sơ.
- **Advocate** — lập luận điểm có lợi cho khách, đề nghị duyệt.
- **Skeptic/Underwriter** — phản biện, nêu rủi ro (devil's advocate).
- **Policy/Compliance (RAG)** — đưa dẫn chứng chính sách vào tranh luận.
- **Moderator/Judge** — điều phối, tổng hợp thành khuyến nghị + lý do + cờ rủi ro.

Danh sách vai có thể điều chỉnh. Tranh luận chỉ để **phân tích**; quyết định cuối
do Decision Gate xác định ([ADR-0022](0022-quyet-dinh-tranh-luan-co-cong.md)).

## Lý do
- Đáp ứng đúng kỳ vọng multi-agent của chủ dự án: agent giao tiếp thật, không chỉ
  chuyền state.
- Mô hình generator–critic/debate giúp surface rủi ro & điểm có lợi tốt hơn một
  agent đơn (Advocate vs Skeptic ép phân tích đa chiều).
- Vẫn an toàn vì quyết định cuối tách ra cổng xác định (ADR-0022).

## Phương án đã cân nhắc
- **Blackboard pipeline tĩnh (ADR-0002)** — dễ đoán/audit nhưng "khô", ít tính
  agentic; chủ dự án muốn hơn thế.
- **Agent tự quyết hoàn toàn (hướng 2a)** — linh hoạt nhất nhưng quyết định không
  tái lập, rủi ro pháp lý. Loại — xem ADR-0022.

## Hệ quả
- (+) Phân tích đa chiều, tính agentic cao, vẫn an toàn nhờ Decision Gate.
- (−) **Nhiều lần gọi LLM** → token & độ trễ tăng mạnh (PR-4); cần giới hạn số vòng.
- (−) Khó test/tái lập phần tranh luận hơn → bù bằng: lưu **toàn bộ transcript**,
  pin version prompt, nhiệt độ thấp, và cổng xác định backstop.
- (−) Cần thiết kế giao thức tranh luận (thứ tự phát biểu, điều kiện dừng).
