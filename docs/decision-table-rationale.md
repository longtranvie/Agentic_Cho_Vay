# Căn cứ bộ tham số quyết định (decision_table.json)

> **⚠️ Trạng thái: BẢN NHÁP DEV — chưa được rủi ro Vapp duyệt (open-questions D1).**
> Số dưới đây do dev **research + neo theo quy định hiện hành (T6/2026)** để hệ thống
> quyết được bằng số *hợp lý*, thay cho placeholder. Đây **không** phải chính sách tín
> dụng chính thức. **Phải có chữ ký bộ phận rủi ro Vapp trước khi cho vay tiền thật.**
> Bối cảnh: Vapp = **fintech** vay tiêu dùng (L2) → áp khung vay nhỏ/tiêu dùng.

## 1. Knock-out (điều kiện cứng — loại thẳng)

| Tham số | Giá trị | Căn cứ |
|---|---|---|
| `min_age` | **20** | Trên tuổi có năng lực hành vi dân sự đầy đủ (18, BLDS) + thực tiễn vay tiêu dùng yêu cầu thu nhập ổn định. |
| `max_age` | **60** | Khoản vay nên kết thúc quanh tuổi nghỉ hưu (thu nhập từ lương). Fintech tiêu dùng thường giới hạn ~60 tại thời điểm vay. *Khẩu vị rủi ro — Vapp có thể nới tới 65/70 nếu có bảo đảm.* |
| `min_income` | **4.500.000đ/tháng** | ≈ **lương tối thiểu vùng 2026** (NĐ 293/2025: Vùng III 4,14tr · Vùng II 4,73tr). Sàn để có khả năng trả nợ tối thiểu. |
| `dti_abs_max` | **0.60** | Tổng nghĩa vụ trả nợ (cũ + mới) ≤ 60% thu nhập. Thông lệ an toàn quốc tế 50–60%; trên ngưỡng này rủi ro vỡ nợ tăng mạnh. |
| `max_loan_amount` | **100.000.000đ** | Trần **"khoản vay có giá trị nhỏ"** — TT 12/2024 dẫn chiếu Điều 102.2 Luật Các TCTD 2024. Phù hợp fintech vay tiêu dùng (L2). |
| `forbidden_purposes` | **vàng miếng · đảo nợ · gửi tiền** | Mục đích **bị cấm cho vay** — **Điều 8** TT hợp nhất. Khớp mờ (bỏ dấu) trên `loan.purpose`. Danh sách cần pháp chế Vapp rà & mở rộng (khớp từ khóa dễ sót/nhầm — kết hợp hội đồng LLM cho ca tinh vi). |

## 2. Scorecard (chấm điểm 0–100)

Thang điểm tổng = **capacity (khả năng trả, tối đa 45)** + **willingness (thiện chí, tối đa 55)**.

| Nhóm | Tham số | Logic | Ghi chú |
|---|---|---|---|
| Capacity | `dti` bands | DTI thấp → điểm cao (≤0.3: +30 … >0.5: −20) | Phán đoán chuyên gia |
| Capacity | `lti` bands | Khoản vay/thu nhập-năm thấp → điểm cao | Phán đoán chuyên gia |
| Willingness | `late_payment` | Từng trễ hạn: −15; sạch: +25 | Tín hiệu thiện chí mạnh nhất |
| Willingness | `tenure_years` | Thâm niên cao → ổn định hơn | |
| Willingness | `stability` | Thu nhập ổn định: +15 | |

> 🔴 **Trọng số scorecard là phần YẾU nhất về căn cứ.** Chúng là phán đoán chuyên gia,
> **phải hiệu chỉnh bằng dữ liệu vay-trả lịch sử thật (D5)** — lý tưởng là hồi quy/ML
> trên nhãn vỡ nợ. Trước khi có dữ liệu đó, coi đây là khởi tạo, không phải cuối cùng.

## 3. Dải điểm & lãi suất

| Tham số | Giá trị | Căn cứ |
|---|---|---|
| `approve_min` / `review_min` | **70 / 40** | Khẩu vị rủi ro: ≥70 duyệt · 40–69 xét duyệt tay · <40 từ chối. **Cần rủi ro Vapp chốt theo mục tiêu nợ xấu.** |
| `interest_rate.annual` | **0.18 (18%/năm)** | Dưới trần **20%/năm** của Điều 468 BLDS (nếu là quan hệ vay dân sự). Nếu cho vay qua TCTD đối tác thì theo thỏa thuận thị trường (TT39) — fintech cần xác định mô hình đối tác (L2). |
| `convene.clear_approve_min` | **75** | Điểm ≥75 + sạch chính sách → chỉ họp hội đồng "light" (tiết kiệm chi phí LLM). |

## 4. Cờ rủi ro chặn (`blocking_flags`)

Ánh xạ cờ → hành động: `regulatory_concern`/`fraud_signal` → **reject**; `data_inconsistency`/
`unverifiable_critical_data`/`affordability_borderline` → **review**. Hội đồng chỉ được nêu
cờ TRONG tập này (cờ ngoài danh sách bị lọc — xem agents/deliberation.py).

## 5. Việc cần Vapp làm trước production
- Bộ phận **rủi ro** rà & **ký duyệt** toàn bộ số mục 1–3 (D1).
- Cung cấp **dữ liệu vay-trả thật** để hiệu chỉnh trọng số scorecard (D5).
- Xác định **mô hình đối tác cho vay** (fintech hợp tác TCTD nào) → chốt trần lãi & loại hình áp dụng.
