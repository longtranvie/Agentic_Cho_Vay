# ADR-0012: Cơ chế Review — interrupt, case queue, resume

- **Trạng thái:** Accepted
- **Ngày:** 2026-06-07

## Bối cảnh
Quyết định "Cần xét duyệt thủ công" ([ADR-0008](0008-human-in-the-loop.md)) cần
một cơ chế vận hành cụ thể trong Vapp: chuyển cho nhân viên, user chờ, rồi nối
tiếp khi có phán quyết.

## Quyết định
Khi Decision = Review:
1. Thu thập thêm *review fields* ([ADR-0011](0011-schema-2-tang.md)).
2. Graph **interrupt + checkpoint** tại đúng điểm chờ người.
3. Tạo một **case** kèm *snapshot toàn bộ ngữ cảnh* (hồ sơ, risk, trích dẫn chính
   sách, log hội thoại) đẩy vào **hàng đợi nhân viên** của Vapp.
4. User nhận trạng thái "**đang xử lý**" + SLA.
5. Nhân viên quyết (duyệt/từ chối/yêu cầu thêm) → **resume** graph từ checkpoint
   → trả kết quả về user.

## Lý do
- Tách rõ ranh giới máy/người; con người chịu trách nhiệm cuối ở ca khó.
- Snapshot đầy đủ → người xét duyệt có ngữ cảnh, đúng audit trail (NFR-5).
- Dùng đúng năng lực interrupt/checkpoint của LangGraph ([ADR-0001](0001-su-dung-langgraph.md)).

## Phương án đã cân nhắc
- **Chặn đồng bộ chờ người** — không khả thi (người có thể mất hàng giờ/ngày).
- **Bỏ phiên, làm lại sau** — mất ngữ cảnh, trải nghiệm kém, tốn lại token.

## Hệ quả
- (+) Vận hành Review rõ ràng, có SLA, resume được, audit đầy đủ.
- (−) Cần hạ tầng hàng đợi + giao diện cho nhân viên Vapp; chốt SLA & nơi lưu case.
- (−) Phải bảo đảm an toàn snapshot (chứa PII — PR-1).
