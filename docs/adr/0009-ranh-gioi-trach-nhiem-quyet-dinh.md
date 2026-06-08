# ADR-0009: Ranh giới trách nhiệm quyết định (rule engine quyết, LLM hỗ trợ)

- **Trạng thái:** Accepted — tinh chỉnh bởi [ADR-0022](0022-quyet-dinh-tranh-luan-co-cong.md)
- **Ngày:** 2026-06-07

> Nguyên tắc cốt lõi (quyết định cuối **xác định, audit được**) vẫn giữ. ADR-0022
> mở rộng vai LLM: ngoài intake/diễn giải, LLM còn **tranh luận phân tích** — nhưng
> kết quả tranh luận chỉ là *đầu vào* cho **Decision Gate xác định**, không thay
> thế nó. Bảng "vai LLM" bên dưới đọc cùng ADR-0022.

## Bối cảnh
Đây là sản phẩm tài chính chạy thật trong Vapp (production). Quyết định cho vay
có hệ quả pháp lý và tiền bạc. LLM không xác định (non-deterministic), có thể
"ảo", và khó audit nếu để nó tự ra phán quyết cuối.

## Quyết định
**Quyết định cuối cùng do một rule engine xác định (deterministic) đưa ra**, dựa
trên: chỉ số rủi ro tính bằng code ([ADR-0004](0004-tach-tinh-toan-khoi-llm.md))
và điều kiện chính sách. **LLM chỉ**: (1) dẫn dắt hội thoại intake, (2) trích
xuất thông tin có cấu trúc, (3) diễn giải lý do quyết định cho người đọc. LLM
**không** trực tiếp chọn Duyệt/Từ chối.

## Lý do
- Quyết định tái lập được, audit được, giải thích được (NFR-1, PR-2, PR-6).
- Ngưỡng/điều kiện do bộ phận pháp chế & rủi ro của Vapp kiểm soát, không phụ
  thuộc "tâm trạng" của model.
- Phù hợp **degrade an toàn** (PR-7): rule engine luôn cho kết quả xác định, kể
  cả khi phần diễn giải của LLM lỗi.

## Phương án đã cân nhắc
- **LLM ra quyết định cuối** — linh hoạt nhưng không tái lập, khó audit, rủi ro
  pháp lý cao. Loại.
- **Hybrid: LLM đề xuất, rule engine veto** — phức tạp hơn mà không thêm giá trị
  rõ ràng ở bản đầu. Có thể xem lại sau.

## Hệ quả
- (+) Quyết định xác định, audit & giải thích rõ; tách bạch trách nhiệm.
- (+) Khi LLM/RAG lỗi vẫn quyết định an toàn được.
- (−) Phải định nghĩa & bảo trì bộ luật/ngưỡng tường minh (phối hợp pháp chế Vapp).
