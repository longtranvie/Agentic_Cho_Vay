# ADR-0011: Schema hồ sơ 2 tầng (core fields + review fields)

- **Trạng thái:** Accepted
- **Ngày:** 2026-06-07

## Bối cảnh
Phần lớn hồ sơ chỉ cần thông tin cơ bản để ra quyết định Duyệt/Từ chối. Một số
ít rơi vào vùng xám cần xét duyệt → cần thông tin sâu hơn (tài sản đảm bảo, bảo
lãnh, sao kê…). Bắt mọi user khai hết thông tin nặng sẽ gây bỏ cuộc.

## Quyết định
Chia schema thành **2 tầng**:
- **Core fields**: bắt buộc để ra quyết định sơ bộ — hỏi cho mọi user.
- **Review fields**: chỉ hỏi **khi** quyết định sơ bộ = Review.

Luồng: đủ core → Decision sơ bộ; nếu Review → quay lại Intake hỏi review fields →
chuyển hồ sơ đầy đủ cho nhân viên.

## Lý do
- Giảm ma sát cho đa số user (FR-14), tăng tỉ lệ hoàn thành.
- Chỉ thu thập dữ liệu khi thực sự cần → phù hợp tối thiểu hóa PII (PR-1).
- Hồ sơ đưa cho người xét duyệt giàu thông tin hơn, đúng lúc.

## Phương án đã cân nhắc
- **Một tầng, hỏi tất cả từ đầu** — đơn giản nhưng nặng nề, bỏ cuộc cao, thu thừa PII.
- **Không hỏi thêm, để người tự đi xác minh** — chậm, trải nghiệm kém.

## Hệ quả
- (+) Hội thoại nhẹ cho đa số; hồ sơ Review đầy đủ.
- (−) Intake phải hỗ trợ 2 pha hỏi; logic "đủ trường" phụ thuộc tầng đang ở.
