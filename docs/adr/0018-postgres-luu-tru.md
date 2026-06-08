# ADR-0018: Postgres làm xương sống lưu trữ (refine ADR-0001)

- **Trạng thái:** Accepted
- **Ngày:** 2026-06-07
- **Liên quan:** chi tiết hóa phần lưu trạng thái của [ADR-0001](0001-su-dung-langgraph.md)

## Bối cảnh
Hệ thống cần lưu 4 thứ: **checkpoint** (state hội thoại — ADR-0013), **audit trail**
(quyết định + version — PR-6), **case queue** (ca Review — ADR-0012), và **vector
store** (kho chính sách RAG — ADR-0005). ADR-0001 mới ghi "SQLite cho bản đầu" —
không đủ cho production nhiều instance.

## Quyết định
Dùng **PostgreSQL làm xương sống** cho cả 4 mục đích:
- Checkpoint + audit + case: bảng trong Postgres.
- Vector store: **pgvector** (extension của Postgres) → không phải nuôi hệ riêng.
- **SQLite** chỉ dùng cho **dev/thử nghiệm cục bộ**.

## Lý do
- Production cần đa instance, bền, giao dịch đồng thời → SQLite không kham.
- Một database lo hết → ít thành phần vận hành, ít điểm hỏng, dễ backup/audit.
- pgvector đủ tốt cho quy mô kho chính sách (không lớn); có thể tách Qdrant sau nếu cần.

## Phương án đã cân nhắc
- **SQLite ở prod** — không chịu được tải/đa instance.
- **Vector store riêng (Chroma/Qdrant) ngay** — thêm hệ thống phải vận hành; chưa cần.

## Hệ quả
- (+) Hạ tầng gọn, bền, dễ audit/backup; app stateless đẩy state ra Postgres.
- (−) Phải quản trị Postgres (trên AWS: dùng RDS quản lý — xem ADR-0020).
- (−) Nếu kho RAG phình rất to sau này, có thể phải tách vector store chuyên dụng.
