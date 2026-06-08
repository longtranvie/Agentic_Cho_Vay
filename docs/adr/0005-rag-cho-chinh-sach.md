# ADR-0005: RAG chỉ dùng cho chính sách cho vay

- **Trạng thái:** Accepted
- **Ngày:** 2026-06-07

## Bối cảnh
Hệ thống cần tra cứu quy định/chính sách cho vay (điều kiện, hạn mức, ngưỡng phê
duyệt) — đây là văn bản dài, thay đổi theo thời gian. Trong khi đó hồ sơ tài
chính cá nhân là dữ liệu **có cấu trúc**, đã thu thập trong bước Intake.

## Quyết định
Dùng **RAG** (vector store + embeddings) **chỉ cho kho tài liệu chính sách**.
Dữ liệu hồ sơ cá nhân đưa **trực tiếp** vào prompt/tool dưới dạng cấu trúc,
**không** qua RAG.

## Lý do
- RAG hợp với tài liệu lớn, ít cấu trúc, hay thay đổi (chính sách).
- Dữ liệu cá nhân đã có cấu trúc → đưa thẳng vừa chính xác vừa rẻ hơn, tránh
  rủi ro truy hồi nhầm/thiếu.
- Tách bạch giúp audit: biết rõ điều khoản chính sách nào được trích dẫn.

## Phương án đã cân nhắc
- **Nhét cả chính sách vào prompt** — vượt context, tốn token, khó cập nhật.
- **RAG cho cả dữ liệu cá nhân** — thừa, dễ sai, không cần thiết với dữ liệu có cấu trúc.

## Hệ quả
- (+) Trích dẫn chính sách rõ ràng, phục vụ explainability (NFR-1).
- (−) Cần dựng và bảo trì kho tài liệu + vector store; chốt công cụ (Chroma/FAISS…) sau.
