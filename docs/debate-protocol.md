# Giao thức tranh luận (Debate Protocol)

Đặc tả cách hội đồng tranh luận ([ADR-0021](adr/0021-hoi-dong-tranh-luan.md)) vận
hành. Tranh luận chỉ để **phân tích**; quyết định cuối do Decision Gate xác định
([ADR-0022](adr/0022-quyet-dinh-tranh-luan-co-cong.md)). Quyết định giao thức:
[ADR-0023](adr/0023-giao-thuc-tranh-luan.md).

## 1. Tổng quan luồng

```
① CONVENE CHECK (deterministic)
   ├─ knock-out / điểm rất thấp, rõ ràng  → bỏ tranh luận → Gate
   ├─ điểm cao + sạch chính sách + dữ liệu tin cậy → "họp nhẹ" (1 lượt Skeptic) → Gate
   └─ mập mờ / tín hiệu trái chiều        → HỌP ĐẦY ĐỦ ↓
② VÒNG 0 — Phát biểu mở (4 agent, song song)
③ VÒNG 1 — Phản biện (song song); Judge dừng sớm nếu hội tụ
   └─ tối đa thêm 1 vòng (cap cứng = 2 vòng phản biện)
④ JUDGE tổng hợp → khuyến nghị + cờ rủi ro
⑤ DECISION GATE (deterministic)
```

## 2. Convene check (điểm ①) — quyết định có họp không

Deterministic, dựa trên: dải điểm scorecard, kết quả đối chiếu chính sách cứng,
**độ tin dữ liệu** (từ `provenance` — dữ liệu Vapp vs user tự khai).

| Tình huống | Hành động |
|---|---|
| Knock-out / điểm rất thấp, không yếu tố giảm nhẹ | Bỏ tranh luận → Gate (Từ chối) |
| Điểm cao **và** không vi phạm chính sách **và** dữ liệu tin cậy | "Họp nhẹ": 1 lượt **Skeptic** soát nhanh → Gate |
| Còn lại (điểm vùng giữa / tín hiệu trái chiều / độ tin thấp) | **Họp đầy đủ** (vòng 0 + phản biện) |

> Ngưỡng & điều kiện convene là **config có version** (ADR-0014).

## 3. Cấu trúc vòng tranh luận

- **Vòng 0 — Phát biểu mở:** Risk Analyst, Advocate, Skeptic, Policy/Compliance
  cùng phát biểu **song song**, dựa trên cùng bộ dữ kiện + điểm số + trích dẫn.
- **Vòng 1 — Phản biện:** mỗi agent đọc phát biểu của nhau → phản bác, nêu/rút cờ.
- **Cap cứng = 2 vòng phản biện.** Judge **dừng sớm** khi không còn lập luận mới
  (hội tụ).

## 4. Cấu trúc đầu ra mỗi lượt agent (structured)

Mỗi agent trả **có cấu trúc** (không "tám" tự do):
- `stance`: lean_approve | neutral | lean_reject
- `arguments`: danh sách { luận điểm, dẫn chứng/grounding }
- `flags_raised`: danh sách { cờ, mức độ, lý do }
- `rebuttals` (vòng ≥1): phản hồi tới luận điểm của agent khác

## 5. Judge tổng hợp (structured)

- `summary_for` / `summary_against`: lập luận hai chiều
- `risk_flags`: cờ rủi ro hợp nhất (kèm mức độ)
- `blocking_flags`: tập con cờ **chặn** (đầu vào cho Gate)
- `recommendation`: lean_approve | lean_review | lean_reject
- `confidence`: low | medium | high
- `rationale_text`: diễn giải ngôn ngữ tự nhiên (dùng làm lý do cho user/audit)

> Judge **không** chốt outcome — chỉ đưa khuyến nghị + cờ cho Decision Gate.

## 6. Bộ cờ rủi ro & ánh xạ Gate (tham số hóa — ADR-0022)

| Cờ | Ý nghĩa | Gate xử (mặc định) |
|---|---|---|
| `data_inconsistency` | Khai mâu thuẫn / nghi gian | Review (nặng → Từ chối) |
| `unverifiable_critical_data` | Dữ liệu quan trọng không kiểm chứng | Review |
| `affordability_borderline` | Sát ngưỡng + thu nhập bấp bênh | Review |
| `regulatory_concern` | Nghi vấn tuân thủ | Review / Từ chối |
| `fraud_signal` | Dấu hiệu gian lận | Từ chối + cảnh báo |
| *(advisory)* | Lo ngại nhẹ | Không chặn (chỉ ghi chú) |

**Việc raise cờ** là phán đoán định tính của hội đồng; **ánh xạ cờ → hành động** là
config xác định. Bất kỳ cờ chặn nào → kéo xuống ít nhất Review (luật bất đối xứng).

## 7. Kiểm soát chi phí & độ trễ (PR-4)

- **Convene check** bỏ qua tranh luận cho ca rõ ràng (đòn bẩy lớn nhất).
- Gọi LLM **song song** trong mỗi vòng; **cap** số vòng; Judge **dừng sớm**.
- **Model rẻ** cho analyst (vd gpt-4o-mini), **model mạnh** cho Judge (vd gpt-4o).
- Worst case ca khó ≈ (4 agent × 2 vòng) + Judge ≈ 9 lượt; ca rõ ràng ≈ 0–1 lượt.

## 8. Audit & tái lập

- Lưu **toàn bộ transcript** (mọi lượt + Judge) vào `deliberation` (state) → audit.
- Nhiệt độ thấp; pin version prompt/model/config cho mỗi quyết định (PR-6).
- Phòng vệ pháp lý nằm ở **Decision Gate xác định + transcript đầy đủ**, không ở
  việc ép LLM tái lập tuyệt đối.
