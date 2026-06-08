# ADR-0008: Human-in-the-loop cho ca biên

- **Trạng thái:** Accepted
- **Ngày:** 2026-06-07

## Bối cảnh
Một số hồ sơ nằm ở **vùng xám** (gray zone): chỉ số rủi ro hoặc đối chiếu chính
sách không đủ rõ để tự động Duyệt hay Từ chối. Quyết định sai trong vùng này tốn
kém (duyệt nhầm rủi ro cao / từ chối nhầm khách tốt).

## Quyết định
Decision Agent phân loại 3 kết quả: **Duyệt / Từ chối / Cần xét duyệt thủ công**.
Ca "cần xét duyệt" được **chuyển cho người** thông qua cơ chế **interrupt** của
LangGraph, rồi tiếp tục luồng sau khi có phán quyết của người.

## Lý do
- Giảm rủi ro của quyết định tự động ở vùng không chắc chắn.
- Phù hợp bối cảnh tài chính nhạy cảm; giữ con người chịu trách nhiệm cuối.
- LangGraph hỗ trợ sẵn interrupt/resume ([ADR-0001](0001-su-dung-langgraph.md)).

## Phương án đã cân nhắc
- **Tự động hoàn toàn (chỉ Duyệt/Từ chối)** — đơn giản nhưng rủi ro cao ở vùng xám.

## Hệ quả
- (+) An toàn hơn, có người kiểm soát ca khó; vẫn giữ audit trail.
- (−) Cần định nghĩa ngưỡng "vùng xám" và giao diện/cơ chế cho người xét duyệt.
