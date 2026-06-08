# ADR-0002: Kiến trúc multi-agent có Supervisor

- **Trạng thái:** ⚠️ Superseded by [ADR-0021](0021-hoi-dong-tranh-luan.md)
- **Ngày:** 2026-06-07

> Mô hình supervisor pipeline tĩnh dưới đây đã được thay bằng **hội đồng tranh luận**
> ([ADR-0021](0021-hoi-dong-tranh-luan.md)) + **Decision Gate xác định**
> ([ADR-0022](0022-quyet-dinh-tranh-luan-co-cong.md)). Ý tưởng "các agent chuyên
> trách + human review" vẫn được kế thừa.

## Bối cảnh
Quy trình thẩm định gồm nhiều phần việc khác nhau: thu thập thông tin, tính rủi
ro, đối chiếu chính sách, ra quyết định. Mỗi phần có yêu cầu và công cụ riêng.

## Quyết định
Chia thành các agent chuyên trách, điều phối bởi một **Supervisor**:
**Intake → Risk/Credit → Policy/RAG → Decision**, với nhánh **Human review**.

## Lý do
- Mỗi agent có một trách nhiệm rõ ràng → dễ hiểu, dễ kiểm thử, dễ thay thế.
- Mô phỏng đúng quy trình thẩm định tín dụng thật.
- Cho phép dùng model/công cụ khác nhau cho từng agent (tối ưu chi phí — NFR-6).

## Phương án đã cân nhắc
- **Một agent đơn (monolithic prompt)** — đơn giản lúc đầu nhưng khó kiểm soát,
  khó audit, khó tách phần tính số ra khỏi LLM.
- **Mạng agent ngang hàng tự gọi nhau** — linh hoạt nhưng khó đoán luồng, khó debug.

## Hệ quả
- (+) Tách bạch trách nhiệm, dễ audit theo từng bước (NFR-5).
- (−) Nhiều thành phần hơn, cần định nghĩa rõ state chia sẻ giữa các agent.
