# Câu hỏi mở (Open Questions)

Các điểm cần Vapp/pháp chế/nghiệp vụ quyết — chặn hoặc ảnh hưởng lớn tới triển khai.
Mang đi họp. Cập nhật trạng thái khi có câu trả lời.

> 🔴 Blocker · 🟡 Ảnh hưởng lớn · 🟢 Cần nhưng không chặn

---

## 0. Bốn blocker cần gỡ trước — giải thích cho cuộc họp

Bốn việc dưới đây chặn việc lên production. Chia 2 nhóm: **pháp lý** (có thể đổi
kiến trúc → quyết sớm) và **dữ liệu** (để hệ thống quyết được bằng số thật).

### Nhóm pháp lý (ưu tiên cao nhất — có thể đổi kiến trúc)

**L1 — Đường xử lý PII khi dùng OpenAI**
- *Vấn đề:* Hồ sơ vay là **dữ liệu cá nhân nhạy cảm** (Nghị định 13, Điều 2.4.h);
  gửi sang OpenAI = **chuyển ra nước ngoài** (Điều 25). Ẩn danh là *cần nhưng có
  thể chưa đủ*.
- *Hai đường:*
  - **(I) Vẫn dùng OpenAI, tuân thủ đầy đủ:** xin **đồng ý user** + lập **hồ sơ
    đánh giá tác động** (gửi Bộ Công an 60 ngày) + ký **DPA** với OpenAI. Kiến trúc
    gần như giữ nguyên.
  - **(II) Giữ PII trong nước (hybrid):** phần chạm PII chạy bằng model nội bộ/tự
    host; OpenAI chỉ lo phần không nhạy cảm. **Đổi kiến trúc đáng kể.**
- *Vì sao quyết trước khi code:* (I) và (II) là **2 kiến trúc khác nhau** — chọn
  sai rồi đổi là đập lõi gọi LLM làm lại.

**L2 — Loại hình pháp lý của Vapp**
- *Vấn đề:* luật áp khác nhau tùy Vapp là **ngân hàng/TCTD** (Thông tư 39),
  **công ty tài chính** (Thông tư 43 → **trần 100tr/khách**), hay **fintech trung
  gian** (luật theo đối tác cho vay).
- *Ảnh hưởng:* quyết **knock-out rules** (có trần 100tr không), tài liệu RAG, và
  **ai chịu trách nhiệm thủ tục cross-border ở L1**.

> 🔗 L1 và L2 dính nhau — hỏi pháp chế **cùng lúc**.

### Nhóm dữ liệu (không đổi kiến trúc, nhưng thiếu thì không quyết được bằng số thật)

**D1 — Bộ config quyết định (ai cấp?)**
- *Là gì:* bảng điểm scorecard, ngưỡng knock-out, dải điểm, lãi, ngưỡng họp hội
  đồng, ánh xạ cờ rủi ro — **dữ liệu, không phải code**, là **chính sách tín dụng**.
- *Vì sao chặn:* rule engine cần số này mới quyết; kỹ thuật **không được tự đặt**
  (rủi ro pháp lý + tiền thật).
- *Nếu chưa có:* dev dùng **expert-set** (giá trị mẫu) để dựng skeleton; **không
  lên production** tới khi rủi ro Vapp duyệt số thật.

**D2 — Tài liệu chính sách nội bộ Vapp (cho RAG)**
- *Là gì:* quy tắc/sản phẩm **riêng của Vapp** dạng văn bản — khác văn bản luật
  NHNN công khai (đã có).
- *Vì sao chặn RAG:* thiếu nó hệ thống chỉ "biết luật chung", không biết **chính
  sách riêng Vapp** để trích dẫn/trả lời.
- *Cần ở dạng:* văn bản (PDF/Word), có ngày hiệu lực.

### Tóm tắt: hỏi ai, hỏi gì

| Blocker | Hỏi ai ở Vapp | Câu hỏi một dòng |
|---|---|---|
| **L1** | Pháp chế | Được gửi PII (ẩn danh) sang OpenAI không — đường (I) hay (II)? |
| **L2** | Pháp chế | Vapp là ngân hàng / công ty tài chính / fintech trung gian? |
| **D1** | Bộ phận rủi ro | Ai làm chủ bảng điểm + ngưỡng, cấp số được không? |
| **D2** | Sản phẩm/Pháp chế | Tài liệu chính sách nội bộ có ở dạng văn bản chưa? |

**Thứ tự:** L1 + L2 hỏi **cùng lúc, sớm nhất**; D1 + D2 thu thập **song song**.

---

## 1. Pháp lý & tuân thủ (gấp nhất)

| # | Câu hỏi | Vì sao quan trọng | Chủ trì | Mức |
|---|---|---|---|---|
| L1 | **PII sang OpenAI: chọn đường (I) tuân thủ cross-border đầy đủ hay (II) giữ PII trong nước (hybrid)?** Nghị định 13 Điều 25: cần hồ sơ đánh giá tác động + gửi Bộ Công an 60 ngày + đồng ý người dùng + DPA. Ẩn danh là cần nhưng có thể chưa đủ. | Có thể đổi cả lựa chọn LLM/kiến trúc ([ADR-0019](adr/0019-an-danh-pii.md)) | Pháp chế | 🔴 |
| L2 | **Vapp thuộc loại hình nào** (ngân hàng / công ty tài chính / fintech hợp tác bên cho vay)? | Quyết định chế độ pháp lý: TT39 (chung) hay TT43 (**trần 100tr/khách**) → ảnh hưởng knock-out | Pháp chế | 🔴 |
| L3 | Có cần lấy **sự đồng ý người dùng** cho xử lý/chuyển dữ liệu ngay trong luồng onboarding không? | Điều 11 NĐ13: đồng ý phải rõ ràng | Pháp chế | 🟡 |
| L4 | Trần lãi suất áp dụng cho sản phẩm Vapp (theo Điều 13 TT39 & quy định hiện hành)? | Nạp vào config lãi ([ADR-0015](adr/0015-lai-suat-co-dinh.md)) | Pháp chế + Rủi ro | 🟡 |

## 2. Dữ liệu

| # | Câu hỏi | Vì sao quan trọng | Chủ trì | Mức |
|---|---|---|---|---|
| D1 | **Ai cấp bộ config quyết định** (bảng điểm, ngưỡng, knock-out, lãi)? Hay dev dùng expert-set tạm? | Nhóm B là **blocker** ([data-requirements §2](data-requirements.md)) | Rủi ro | 🔴 |
| D2 | **Tài liệu chính sách nội bộ Vapp** đã có dạng văn bản chưa? Định dạng (PDF/Word)? | Blocker cho RAG (lớp NHNN đã có sẵn) | Sản phẩm/Pháp chế | 🔴 |
| D3 | **Agent được đọc dữ liệu Vapp nào** (KYC, thu nhập, giao dịch)? | Quyết định Bootstrap + độ tin → ảnh hưởng tỉ lệ Review | Kỹ thuật Vapp | 🟡 |
| D4 | Ai tạo **bộ eval golden set**? Có chuyên gia rủi ro gán nhãn không? | Đo chất lượng + regression gate (PR-8) | Rủi ro | 🟡 |
| D5 | Có **dữ liệu vay-trả lịch sử** không (để hiệu chỉnh scorecard)? | Nếu không → expert-set + lộ trình ML sau | Vận hành | 🟢 |

## 3. Tích hợp & hạ tầng

| # | Câu hỏi | Vì sao quan trọng | Chủ trì | Mức |
|---|---|---|---|---|
| T1 | Chi tiết **hợp đồng API** request/response với Vapp | Để code đúng giao diện ([ADR-0017](adr/0017-api-contract.md)) | Kỹ thuật Vapp | 🟡 |
| T2 | **Region AWS** + cấu hình VPC/IAM (cân nhắc chủ quyền dữ liệu) | Tuân thủ + triển khai ([ADR-0020](adr/0020-trien-khai-docker-aws.md)) | Hạ tầng | 🟡 |
| T3 | Vận hành **hàng đợi Review**: ai xử, SLA bao lâu, giao diện nhân viên? | Quyết định cơ chế Review ([ADR-0012](adr/0012-co-che-review.md)) | Vận hành | 🟡 |
| T4 | Chọn **reranker** cho RAG | Hoàn thiện pipeline RAG ([rag-design.md](rag-design.md)) | Kỹ thuật | 🟢 |

## 4. Nghiệp vụ / tham số (cần con số cụ thể)

| # | Câu hỏi | Vì sao quan trọng | Chủ trì | Mức |
|---|---|---|---|---|
| B1 | Ngưỡng **convene check** (khi nào họp hội đồng tranh luận) | Cân bằng chi phí vs độ phủ ([ADR-0023](adr/0023-giao-thuc-tranh-luan.md)) | Rủi ro + Kỹ thuật | 🟡 |
| B2 | Định nghĩa cụ thể từng **cờ rủi ro chặn** + ánh xạ hành động | Decision Gate dùng ([ADR-0022](adr/0022-quyet-dinh-tranh-luan-co-cong.md)) | Rủi ro | 🟡 |
| B3 | **TTL hồ sơ dở** (7? 30 ngày?) | Nối phiên ([ADR-0013](adr/0013-noi-phien-va-ttl.md)) | Sản phẩm | 🟢 |
| B4 | **Ngân sách token/độ trễ** chấp nhận được mỗi hồ sơ | Mô hình tranh luận tốn nhiều LLM (PR-4) | Sản phẩm + Kỹ thuật | 🟡 |

## Tóm tắt blocker (phải gỡ trước khi production)
- **L1** (đường PII), **L2** (loại hình Vapp), **D1** (config), **D2** (tài liệu chính sách).
- Dev/skeleton có thể chạy trước với **expert-set + dữ liệu giả lập** trong khi chờ gỡ blocker.
