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

## Kết quả hiện tại: 10/10 high · 12/14 tổng

Hai ca lệch là **phát hiện có chủ đích**, không phải lỗi:

1. **`unstable-income` — máy `approve`, kỳ vọng `review`.** Thu nhập không ổn định một mình
   không kéo điểm xuống dưới 70 với trọng số hiện tại (clean + thâm niên lấn át). → Câu hỏi
   cho rủi ro: *thu nhập không ổn định có nên buộc xét tay không?* Liên quan hiệu chỉnh
   trọng số bằng dữ liệu thật (**D5**).
2. **`data-inconsistency-tenure` — máy `approve`, kỳ vọng `review`.** Tuổi 22 nhưng thâm niên
   15 năm (bắt đầu làm lúc 7 tuổi — bất khả). Mâu thuẫn logic này cần **hội đồng LLM** nêu cờ
   `data_inconsistency`; offline tất định không suy luận được → giới hạn đã biết.

> ✅ Ca `purpose-gold-bar` (mua vàng miếng) trước là `known_gap`, nay **bịt được offline** bằng
> chặn mục đích cấm tất định (`knockout.forbidden_purposes`, Điều 8) → đã nâng lên tầng `high`.

## Việc còn lại (khi có nguồn lực Vapp)
- Chuyên gia rủi ro gán/duyệt nhãn → nâng `needs_expert` thành chân lý (D4).
- Bổ sung ca từ hồ sơ thật đã review.
- Mở rộng `forbidden_purposes` (khớp mờ theo từ khóa) — danh sách cần pháp chế Vapp rà & duyệt.
