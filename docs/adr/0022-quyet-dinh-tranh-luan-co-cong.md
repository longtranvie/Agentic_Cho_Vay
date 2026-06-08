# ADR-0022: Quyết định từ tranh luận + cổng xác định backstop (2b)

- **Trạng thái:** Accepted
- **Ngày:** 2026-06-07
- **Tinh chỉnh:** [ADR-0009](0009-ranh-gioi-trach-nhiem-quyet-dinh.md) (vẫn giữ nguyên
  tắc quyết định cuối xác định; mở rộng vai LLM sang tranh luận phân tích)

## Bối cảnh
Chuyển sang hội đồng tranh luận ([ADR-0021](0021-hoi-dong-tranh-luan.md)) đặt câu
hỏi: kết quả tranh luận **có phải quyết định cuối** không? (2a) Judge chốt luôn →
không tái lập, khó audit, rủi ro pháp lý cao. (2b) tranh luận để phân tích, một
cổng xác định chốt cuối. Chủ dự án chọn **2b**.

## Quyết định
**Quyết định cho vay cuối cùng do Decision Gate xác định (deterministic) đưa ra**,
nhận 3 đầu vào:
1. **Knock-out** (deterministic) — vi phạm luật cứng → Từ chối/bất hợp lệ ngay.
2. **Điểm scorecard** (deterministic, ADR-0014) — dải điểm số.
3. **Khuyến nghị tranh luận** (từ Judge, ADR-0021) — đánh giá định tính + cờ rủi ro.

**Luật của cổng (bất đối xứng — an toàn một chiều):**
- **Duyệt** chỉ khi: qua knock-out **VÀ** điểm số đạt ngưỡng **VÀ** không có vi
  phạm chính sách cứng **VÀ** tranh luận không nêu cờ rủi ro chặn.
  → Tức **muốn duyệt phải hội đủ cả số lẫn đồng thuận tranh luận**.
- **Hạ xuống Review/Từ chối**: knock-out, điểm thấp, vi phạm chính sách, **hoặc**
  tranh luận nêu rủi ro → bất kỳ cái nào cũng đủ.
  → Tức tranh luận **chỉ có thể làm chặt hơn**, không thể tự "duyệt" vượt luật cứng
  hay điểm số không đạt.

## Lý do
- Giữ nguyên tắc ADR-0009: quyết định cuối **xác định, audit được, giải trình được**
  với NHNN — kể cả khi phần tranh luận LLM biến thiên.
- Vẫn cho agent tranh luận hết mình (giá trị phân tích), nhưng rủi ro pháp lý được
  chặn vì agent không có "tiếng nói cuối" để tạo ra một khoản duyệt thiếu cơ sở.
- Degrade an toàn (PR-7): tranh luận lỗi/biến thiên → cùng lắm đẩy Review, không
  bao giờ tạo duyệt sai.

## Audit & tái lập
- Lưu **toàn bộ transcript tranh luận** + đầu vào/đầu ra của Gate + version
  prompt/model/config dùng (PR-6).
- Nhiệt độ thấp cho agent; chấp nhận LLM không tái lập tuyệt đối — **tính phòng vệ
  nằm ở cổng xác định + transcript đầy đủ**, không nằm ở việc ép LLM tái lập.

## Phương án đã cân nhắc
- **2a — tranh luận = quyết định** — linh hoạt nhất, rủi ro pháp lý cao nhất. Loại.

## Hệ quả
- (+) Có tranh luận agent phong phú **và** quyết định cuối vững về pháp lý.
- (−) Có thể có cảm giác "tranh luận sôi nổi nhưng vẫn bị luật cứng chặn" — đúng ý
  đồ; cần truyền đạt rõ cho user/nghiệp vụ.
- (−) Cần định nghĩa rõ "cờ rủi ro chặn" từ Judge để Gate dùng (tham số hóa).
