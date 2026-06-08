# ADR-0006: Dùng OpenAI làm LLM provider

- **Trạng thái:** Accepted
- **Ngày:** 2026-06-07

## Bối cảnh
Hệ thống cần một LLM cho hội thoại intake, diễn giải kết quả và ra quyết định,
cùng embeddings cho RAG.

## Quyết định
Dùng **OpenAI** làm LLM provider: chat models (function calling) cho agent và
`text-embedding-3` cho RAG. Tích hợp qua `langchain-openai`.

## Lý do
- Yêu cầu của chủ dự án.
- Function calling hỗ trợ tốt structured output ([ADR-0007](0007-structured-output-pydantic.md)).
- Hệ sinh thái LangChain/LangGraph tích hợp sẵn.

## Phương án đã cân nhắc
- Provider khác (Anthropic, model mở…) — không chọn theo yêu cầu dự án.

## Hệ quả
- (+) Tích hợp nhanh, tài liệu/cộng đồng nhiều.
- (−) Phụ thuộc API trả phí; cần quản lý API key và chi phí token (NFR-6).
- **Lưu ý:** Lớp gọi LLM nên trừu tượng hóa tối thiểu để có thể đổi provider sau
  nếu cần, nhưng không làm phức tạp hóa quá mức ở bản đầu.
