# Eval golden set — đo chất lượng QUYẾT ĐỊNH

Test đơn vị trả lời *"code có chạy đúng logic không"*. Eval golden set trả lời câu khác:
*"hệ thống ra **quyết định có hợp lý** không"*. Đây là cách chứng minh chất lượng + chặn
hồi quy (regression) khi đổi bộ số.

- **Dữ liệu:** [data/eval/golden_set.json](../data/eval/golden_set.json) — mỗi ca có hồ sơ + `expected_outcome` + `basis` (vì sao).
- **Chạy báo cáo:** `python eval/run_eval.py` (offline, tất định — MockLLM + KeywordStore).
- **Gate hồi quy:** `tests/test_eval.py` — mọi ca tầng `high` PHẢI đúng (chạy trong `tests/run.py`).

## Ba tầng tin cậy của nhãn

| Tầng | Nghĩa | Lệch nghĩa là gì |
|---|---|---|
| **high** | Nhãn suy chắc từ knock-out/luật (tuổi, thu nhập, trần vay, DTI, hồ sơ sạch rõ) | **BUG** — chặn ở test |
| **needs_expert** | Ca biên, nhãn là phán đoán chính sách của dev | **Mang hỏi rủi ro Vapp** (có thể nhãn sai, có thể số draft sai) |
| **known_gap** | Offline không bắt được (mock không raise cờ) | **Giới hạn đã biết** — cần hội đồng LLM hoặc rule bổ sung |

> ⚠️ Nhãn do **dev suy luận**, CHƯA có chuyên gia rủi ro Vapp gán nhãn (open-questions
> **D4**). Tầng `high` đủ chắc để làm regression gate; tầng `needs_expert` là **đầu vào
> thảo luận** với risk, không phải chân lý.

## Kết quả hiện tại: 9/9 high · 11/13 tổng

Hai ca lệch là **phát hiện có chủ đích**, không phải lỗi:

1. **`unstable-income` — máy `approve`, kỳ vọng `review`.** Thu nhập không ổn định một mình
   không kéo điểm xuống dưới 70 với trọng số hiện tại (clean + thâm niên lấn át). → Câu hỏi
   cho rủi ro: *thu nhập không ổn định có nên buộc xét tay không?* Liên quan hiệu chỉnh
   trọng số bằng dữ liệu thật (**D5**).
2. **`purpose-gold-bar` — máy `approve`, kỳ vọng `reject`.** Mua vàng miếng bị cấm (Điều 8
   TT hợp nhất) nhưng offline mock không raise cờ `regulatory_concern`. → Cần **hội đồng LLM
   thật** bắt, HOẶC thêm **chặn mục đích tất định** (danh sách mục đích cấm trong knock-out).

## Việc còn lại (khi có nguồn lực Vapp)
- Chuyên gia rủi ro gán/duyệt nhãn → nâng `needs_expert` thành chân lý (D4).
- Bổ sung ca từ hồ sơ thật đã review.
- Cân nhắc chặn mục đích tất định để bịt `known_gap` mà không phụ thuộc LLM.
