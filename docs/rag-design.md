# Thiết kế RAG (kho chính sách cho vay)

RAG dùng để **tra cứu tài liệu chính sách/quy định** ([ADR-0005](adr/0005-rag-cho-chinh-sach.md)),
đóng vai **phụ trợ** — trích dẫn/giải thích, hỗ trợ người xét duyệt, trả lời câu
hỏi chính sách trong hội thoại — **không nằm trên đường quyết định cứng**
([ADR-0016](adr/0016-vai-tro-rag-phu-tro.md)). Điều kiện cứng nằm ở decision table
([ADR-0014](adr/0014-mo-hinh-rui-ro-scorecard.md)).

## 1. Nguồn & loại tài liệu
- Chính sách cho vay nội bộ Vapp, văn bản NHNN liên quan, quy tắc sản phẩm, quy
  trình xử lý ngoại lệ.
- **Ngôn ngữ: tiếng Việt** (đã chốt).
- *Còn mở:* định dạng nguồn (PDF / Word / web) và đã có sẵn chưa — cần Vapp cung cấp.

## 2. Chunking — theo cấu trúc văn bản
Văn bản pháp lý/chính sách có cấu trúc rõ (Điều / Khoản / Mục) → **chunk theo cấu
trúc** (mỗi điều/khoản một chunk), không cắt theo độ dài cứng, để giữ trọn ngữ
nghĩa và trích dẫn được.

**Metadata mỗi chunk** (theo cấu trúc thật khảo sát từ TT39: Chương → Mục → Điều →
Khoản → Điểm):

```json
{
  "van_ban": "Thông tư 39/2016/TT-NHNN",
  "chuong": "I", "muc": null,
  "dieu": 7, "dieu_tieu_de": "Điều kiện vay vốn",
  "ngay_hieu_luc": "2017-03-15",
  "sua_doi_boi": ["Thông tư 12/2024/TT-NHNN"],
  "phien_ban": "hop-nhat-2024-07-01",
  "tham_chieu": ["Điều 2", "Điều 8"]
}
```

- **Đơn vị chunk = Điều** (tự chứa & trích dẫn được "Điều X"); Điều dài nhiều Khoản
  thì tách phụ theo Khoản nhưng **giữ tham chiếu Điều**.
- **Bản hợp nhất (quan trọng):** văn bản bị sửa đổi (TT39 ← TT12/2024, TT43 ← TT18/2019)
  → phải ingest **bản đang hiệu lực**, không phải bản gốc. Trường `sua_doi_boi` +
  `phien_ban` phục vụ việc này.
- **Tham chiếu chéo:** các Điều dẫn nhau ("theo Điều 7") → lưu `tham_chieu` để khi
  truy hồi có thể kéo thêm điều được dẫn.

## 3. Embedding
- OpenAI `text-embedding-3-**large**` (đã chốt) — ưu tiên độ chính xác cho tiếng
  Việt & văn bản pháp lý (sai một điều khoản là tốn kém).

## 4. Truy hồi — hybrid + rerank + lọc metadata
- **Hybrid** (keyword/BM25 + vector): văn bản pháp lý nhiều thuật ngữ & con số
  chính xác ("Điều 7", "20%/năm") mà vector thuần dễ trượt.
- **Rerank** kết quả để tăng độ chính xác top-k.
- **Lọc metadata**: đúng loại sản phẩm; **chỉ lấy bản còn hiệu lực** (theo ngày).

## 5. Versioning chính sách (bắt buộc — PR-6)
- Metadata **ngày hiệu lực**; truy hồi chỉ lấy bản đang hiệu lực.
- Pipeline **re-ingest** khi tài liệu cập nhật.
- Ghi lại **phiên bản tài liệu** đã dùng cho mỗi quyết định (audit).

## 6. Chống ảo & kiểm soát chất lượng
- **Grounding bắt buộc**: mọi phát biểu về chính sách phải kèm trích dẫn nguồn;
  không có nguồn → không khẳng định.
- Truy hồi yếu/không chắc → **đẩy sang Review**, không đoán (degrade an toàn — PR-7).
- **Eval RAG**: bộ câu hỏi–điều khoản mẫu đo (a) truy đúng điều khoản, (b) trả lời
  trung thực với nguồn (faithfulness).

## 7. Stack (bản đầu)
- Vector store: Chroma (bản đầu — [ADR-0005](adr/0005-rag-cho-chinh-sach.md)).
- Embedding: `text-embedding-3-large`.
- *Còn mở:* chọn reranker (vd cohere rerank / bge-reranker) — chốt khi triển khai.
