# Mô hình rủi ro & ra quyết định

Tài liệu này đặc tả cách hệ thống ra quyết định cho vay. Quyết định là **xác định
(deterministic), không do LLM** ([ADR-0009](adr/0009-ranh-gioi-trach-nhiem-quyet-dinh.md));
mô hình gồm **knock-out + scorecard** ([ADR-0014](adr/0014-mo-hinh-rui-ro-scorecard.md)).

> ⚠️ **Mọi con số dưới đây là GIÁ TRỊ MINH HỌA.** Trước production, bộ phận rủi ro
> & pháp chế Vapp phải xác nhận/điều chỉnh. Tất cả nằm ở **config có version**, đổi
> không cần sửa code (PR-6).

## 1. Pipeline ra quyết định

```
Hồ sơ đủ core fields
        │
        ▼
① Knock-out (loại thẳng)  ──► vi phạm → TỪ CHỐI / BẤT HỢP LỆ (tới Gate luôn)
        │ qua được
        ▼
② Scorecard (chấm điểm SỐ) — deterministic
   ├─ điểm Capacity (khả năng trả)
   └─ điểm Willingness (thiện chí trả)
        │
        ▼
③ Hội đồng tranh luận (ADR-0021/0023) — convene check bỏ qua ca rõ ràng;
   ca mập mờ → các agent LLM phản biện nhau (song song, cap 2 vòng)
   → khuyến nghị + cờ rủi ro (chỉ là PHÂN TÍCH, không tự quyết). Xem debate-protocol.md
        │
        ▼
④ DECISION GATE (deterministic backstop — ADR-0022)
   kết hợp knock-out + điểm số + khuyến nghị tranh luận dưới luật cứng
   → DUYỆT / REVIEW / TỪ CHỐI
```

> **Luật cổng bất đối xứng (ADR-0022):** **Duyệt** cần hội đủ *cả* điểm số đạt *và*
> tranh luận đồng thuận (không cờ rủi ro chặn) *và* không vi phạm chính sách cứng.
> Tranh luận **chỉ có thể làm chặt hơn** (đẩy Review/Từ chối), **không thể tự duyệt**
> vượt luật cứng hay điểm số không đạt.

## 2. Lớp Knock-out (điều kiện cứng)

Vi phạm bất kỳ điều nào → loại ngay, không chấm điểm:

| Điều kiện loại thẳng (minh họa) |
|---|
| Tuổi < 18 hoặc > giới hạn sản phẩm |
| Thu nhập = 0 / không chứng minh được |
| DTI vượt trần tuyệt đối (vd > 0.6) |
| Vi phạm chính sách cứng (từ Policy/RAG) |
| Nợ xấu trên CIC *(khi có tích hợp CIC)* |

## 3. Scorecard — 2 chiều rủi ro ([ADR-0014](adr/0014-mo-hinh-rui-ro-scorecard.md))

Tính **cả hai**, không để chiều này che chiều kia:

### 3a. Capacity — khả năng trả (có đủ tiền không)
| Yếu tố | Điều kiện (minh họa) | Điểm |
|---|---|---|
| DTI sau vay | <0.3 → +30 · 0.3–0.4 → +15 · 0.4–0.5 → +5 · >0.5 → −20 |
| Khoản vay / thu nhập năm | <2 → +15 · 2–3 → +5 · >3 → −10 |

### 3b. Willingness — thiện chí trả (có chịu trả không)
| Yếu tố | Điều kiện (minh họa) | Điểm |
|---|---|---|
| Lịch sử trả nợ | chưa từng trễ → +25 · từng trễ → −15 |
| Thâm niên việc làm | ≥3 năm → +15 · 1–3 → +8 · <1 → 0 |
| Ổn định thu nhập | ổn định → +15 · không → 0 |

> Khi dữ liệu là **tự khai** (độ tin thấp), điểm Willingness kém tin cậy → hồ sơ
> dễ rơi vào Review (xem [data-requirements.md](data-requirements.md), nhóm A).

## 4. Dải điểm → quyết định (minh họa)

| Tổng điểm | Kết quả |
|---|---|
| ≥ 70 | **Duyệt** |
| 40 – 69 | **Review** (xét duyệt thủ công) |
| < 40 | **Từ chối** |

## 5. Lãi suất

**Cố định theo sản phẩm** ([ADR-0015](adr/0015-lai-suat-co-dinh.md)), là tham số
config tuân trần NHNN. Dùng cho Affordability và ước tính trả góp.

## 6. Tham số hóa & version

Toàn bộ con số (knock-out, bảng điểm, dải điểm, lãi, giới hạn pháp lý) sống trong
một **decision table dạng config có version**, do rủi ro & pháp chế Vapp sở hữu:
- Đổi chính sách → đổi config, không sửa code.
- Mỗi quyết định ghi lại **phiên bản config** đã dùng (audit & rollback — PR-6).

## 7. Lộ trình tiến hóa

1. **Giai đoạn 1 (ra mắt):** knock-out + scorecard với trọng số **chuyên gia đặt**.
2. **Giai đoạn 2 (có dữ liệu):** hiệu chỉnh trọng số bằng dữ liệu vay-trả thật.
3. **Giai đoạn 3 (đủ dữ liệu):** thêm ML chạy **shadow mode** để so sánh; chỉ
   chuyển khi chứng minh được & xử lý xong giải thích/pháp lý. Phần "tính điểm rủi
   ro" tách sau một interface để thay cách tính mà output không đổi.
