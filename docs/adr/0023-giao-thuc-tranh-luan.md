# ADR-0023: Giao thức tranh luận — convene check + round-robin có cap

- **Trạng thái:** Accepted
- **Ngày:** 2026-06-07
- **Liên quan:** chi tiết hóa [ADR-0021](0021-hoi-dong-tranh-luan.md), [ADR-0022](0022-quyet-dinh-tranh-luan-co-cong.md)

## Bối cảnh
Hội đồng tranh luận (ADR-0021) cần một giao thức cụ thể: ai nói khi nào, dừng lúc
nào, Judge tổng hợp ra gì, và cờ rủi ro định nghĩa thế nào — đồng thời **kiểm soát
chi phí/độ trễ** (PR-4) vì nhiều agent = nhiều lượt gọi LLM.

## Quyết định
- **Convene check (deterministic) trước khi họp:** ca rõ ràng (knock-out / điểm rất
  thấp; hoặc điểm cao + sạch chính sách + dữ liệu tin cậy) **bỏ qua tranh luận** (ca
  tốt chỉ "họp nhẹ" 1 lượt Skeptic); chỉ ca **mập mờ** mới họp đầy đủ.
- **Round-robin song song có cap:** Vòng 0 phát biểu mở (4 agent song song) → Vòng 1
  phản biện (song song); **cap cứng 2 vòng phản biện**, Judge **dừng sớm** khi hội tụ.
- **Output có cấu trúc** mỗi lượt (stance/arguments/flags/rebuttals) và Judge tổng
  hợp có cấu trúc (recommendation + confidence + blocking_flags + rationale).
- **Bộ cờ rủi ro tham số hóa** (data_inconsistency, unverifiable_critical_data,
  affordability_borderline, regulatory_concern, fraud_signal, + advisory); ánh xạ
  cờ → hành động là config xác định.

Chi tiết đầy đủ: `../debate-protocol.md`.

## Lý do
- Convene check là đòn bẩy chi phí lớn nhất: không triệu tập hội đồng cho ca hiển nhiên.
- Round-robin song song có cap → dễ đoán chi phí & độ trễ, dễ test hơn điều phối động.
- Output có cấu trúc → Judge tổng hợp & audit dễ, tránh agent lan man.
- Cờ tham số hóa → giữ tính xác định ở Gate (ADR-0022), nghiệp vụ chỉnh được.

## Phương án đã cân nhắc
- **Judge điều phối động (chọn người nói tiếp)** — "thông minh" hơn nhưng tốn thêm
  lượt LLM mỗi lần quyết, chi phí khó đoán. Loại ở bản đầu.
- **Luôn họp đầy đủ mọi hồ sơ** — nhất quán quy trình nhưng tốn nhiều; loại nhờ convene check.
- **Số vòng cố định, không dừng sớm** — đơn giản nhưng không tối ưu chi phí. Loại.

## Hệ quả
- (+) Tranh luận phong phú ở ca cần, rẻ ở ca dễ; chi phí có trần & kiểm soát được.
- (−) Convene check cần ngưỡng đúng (config) — đặt sai thì hoặc tốn hoặc bỏ sót ca cần họp.
- (−) Vẫn nhiều lượt LLM hơn pipeline cũ → cần theo dõi chi phí/độ trễ thực tế (PR-4).
