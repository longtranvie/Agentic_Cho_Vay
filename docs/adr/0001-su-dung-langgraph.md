# ADR-0001: Dùng LangGraph làm lớp điều phối

- **Trạng thái:** Accepted
- **Ngày:** 2026-06-07

## Bối cảnh
Hệ thống gồm nhiều agent chạy theo một quy trình có vòng lặp (hội thoại intake),
phân nhánh (ca biên → human review) và cần lưu/khôi phục trạng thái giữa các lượt.

## Quyết định
Dùng **LangGraph** làm lớp điều phối (state machine) cho toàn bộ luồng agent.

## Lý do
- Mô hình hóa quy trình dạng graph với node/edge có điều kiện — hợp với luồng
  intake loop + phân nhánh quyết định.
- Có sẵn **checkpointer** để lưu state, resume phiên và tạo audit trail (NFR-4, NFR-5).
- Hỗ trợ **interrupt** phục vụ human-in-the-loop ([ADR-0008](0008-human-in-the-loop.md)).
- State tường minh, dễ kiểm thử hơn so với chuỗi agent ẩn.

## Phương án đã cân nhắc
- **Tự viết orchestrator** — kiểm soát cao nhưng phải tự làm checkpoint/branching.
- **Chuỗi prompt đơn giản (1 agent lớn)** — khó kiểm soát, khó audit, khó loop.

## Hệ quả
- (+) Luồng tường minh, có checkpoint, dễ mở rộng thêm agent.
- (−) Thêm phụ thuộc và đường cong học LangGraph.
