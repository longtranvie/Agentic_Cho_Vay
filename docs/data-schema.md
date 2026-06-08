# Schema hồ sơ vay & Slot-filling

Tài liệu này định nghĩa **các trường thông tin** Intake Agent cần khai thác và
**điều kiện hợp lệ** của từng trường. Đây là "checklist" để hội thoại không trôi
mất kiểm soát (xem [ADR-0003](adr/0003-intake-hoi-thoai-slot-filling.md)).

Schema chia **2 tầng** ([ADR-0011](adr/0011-schema-2-tang.md)):
- **Core fields** — bắt buộc để ra quyết định sơ bộ; hỏi cho mọi user.
- **Review fields** — thông tin sâu, **chỉ hỏi khi** hồ sơ rơi vào vùng xám (Review).

Một số core field có thể được **pre-fill** từ dữ liệu Vapp (Bootstrap) → Intake bỏ qua câu hỏi đó.

## 1. Core fields (tầng 1 — bắt buộc)

| Nhóm | Trường | Kiểu | Điều kiện hợp lệ |
|------|--------|------|------------------|
| **Khoản vay** | số tiền vay | số | > 0 |
| | mục đích vay | chuỗi | không rỗng |
| | kỳ hạn mong muốn (tháng) | số | > 0 |
| **Thu nhập** | thu nhập / tháng | số | ≥ 0 |
| | nguồn thu nhập | enum | lương / kinh doanh / khác |
| | tính ổn định | enum | ổn định / không ổn định |
| **Nghĩa vụ nợ** | tổng nợ hiện tại | số | ≥ 0 |
| | trả góp hàng tháng | số | ≥ 0 |
| **Nhân thân** | tuổi | số | ≥ 18 |
| | nghề nghiệp | chuỗi | không rỗng |
| | thâm niên (năm) | số | ≥ 0 |
| **Lịch sử tín dụng** | từng trả nợ trễ | boolean | — |

> **Affordability** ([ADR-0010](adr/0010-affordability-counter-offer.md)) cần tối thiểu:
> thu nhập/tháng, trả góp hiện tại, kỳ hạn → có thể tính & báo hạn mức tối đa ngay
> khi nhóm Thu nhập + Nghĩa vụ nợ đủ, không cần chờ toàn bộ core fields.

## 2. Review fields (tầng 2 — chỉ hỏi khi vào Review)

- Tài sản đảm bảo (có/không, loại, giá trị).
- Người bảo lãnh / đồng vay.
- Sao kê / bằng chứng thu nhập.
- Lý do/khoản mục của nợ hiện tại.
- Số người phụ thuộc.
- Ghi chú thêm của người vay.

## 3. Quy tắc slot-filling

1. Mỗi lượt, Intake Agent **trích tối đa các trường** có thể từ câu trả lời.
2. Trường nào còn thiếu → hỏi tiếp; **hỏi gộp** các trường liên quan khi hợp lý.
3. Trường sai điều kiện → **hỏi lại ngay**, không cho lọt xuống bước sau.
4. Có **giới hạn số lượt hỏi** (ví dụ tối đa N lượt) để tránh loop vô tận.
5. Đủ **tất cả trường bắt buộc + hợp lệ** → mới chuyển sang thẩm định.

## 4. Trường nhạy cảm — KHÔNG dùng để quyết định

Theo [NFR-2 (fairness)](requirements.md), **không** thu thập/sử dụng để ra quyết
định: giới tính, tôn giáo, sắc tộc, tình trạng hôn nhân, quan điểm chính trị.

## 5. Định dạng đầu ra (ví dụ)

```json
{
  "loan": { "amount": 10000000, "purpose": "mua xe", "term_months": 12 },
  "income": { "monthly": 20000000, "source": "luong", "stability": "on_dinh" },
  "debt": { "total": 0, "monthly_payment": 0 },
  "profile": { "age": 30, "occupation": "ke_toan", "tenure_years": 3 },
  "credit_history": { "had_late_payment": false }
}
```

> Đầu ra được mô tả bằng **Pydantic** (xem [ADR-0007](adr/0007-structured-output-pydantic.md)).
