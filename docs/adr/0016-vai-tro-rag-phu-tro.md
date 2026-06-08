# ADR-0016: RAG là thành phần phụ trợ, không nằm trên đường quyết định cứng

- **Trạng thái:** Accepted
- **Ngày:** 2026-06-07
- **Liên quan:** mở rộng [ADR-0005](0005-rag-cho-chinh-sach.md); ràng buộc bởi
  [ADR-0009](0009-ranh-gioi-trach-nhiem-quyet-dinh.md), [ADR-0014](0014-mo-hinh-rui-ro-scorecard.md)

## Bối cảnh
Quyết định cho vay phải **xác định, audit được, không do LLM phán** (ADR-0009,
0014). Nhưng RAG = LLM đọc văn bản → **không xác định** và có thể đọc sai/ảo. Nếu
để "LLM đọc chính sách rồi tự kết luận hồ sơ có tuân thủ không" thì mâu thuẫn với
nguyên tắc đã chốt và tạo rủi ro pháp lý.

## Quyết định
**RAG KHÔNG nằm trên đường ra quyết định cứng.** Tách như sau:

| Loại chính sách | Xử lý | RAG quyết định? |
|---|---|---|
| Định lượng/cứng (trần lãi, hạn mức, tuổi, DTI tối đa…) | Mã hóa thành **tham số decision table** (ADR-0014) | ❌ |
| Định tính/ngoại lệ | RAG truy hồi → **đưa human reviewer** | ❌ (hỗ trợ người) |
| Trích dẫn nguồn cho một điều kiện/quyết định | RAG tìm đúng điều khoản để **giải thích** | ❌ (explainability) |
| User hỏi về chính sách trong hội thoại | RAG trả lời | ❌ (không phải quyết định) |

→ RAG làm 3 việc: (1) **trích dẫn/giải thích** (NFR-1), (2) **hỗ trợ người xét
duyệt** ở ca Review, (3) **trả lời câu hỏi chính sách** trong hội thoại. Điều kiện
cứng luôn là **config xác định**.

## Lý do
- Giữ được tính xác định & audit của quyết định (ADR-0009).
- Vẫn tận dụng RAG đúng thế mạnh (truy hồi & diễn giải văn bản dài).
- Degrade an toàn (PR-7): RAG lỗi/không chắc → không ảnh hưởng quyết định cứng;
  ca định tính không chắc → đẩy Review thay vì để LLM tự quyết.

## Phương án đã cân nhắc
- **RAG tham gia trực tiếp phán compliance** — linh hoạt nhưng phá tính xác định,
  rủi ro pháp lý & ảo. Loại.

## Hệ quả
- (+) Quyết định xác định; RAG tăng minh bạch & hỗ trợ người mà không gây rủi ro.
- (−) Phải mã hóa điều kiện cứng vào config (công sức ban đầu), và duy trì đồng bộ
  giữa config và văn bản chính sách gốc.
