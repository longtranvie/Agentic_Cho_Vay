# ADR-0020: Triển khai bằng Docker trên AWS

- **Trạng thái:** Accepted
- **Ngày:** 2026-06-07

## Bối cảnh
Cần chọn cách đóng gói & nơi chạy production. Chủ dự án chọn **Docker + AWS**.
Giai đoạn đầu chưa cần Kubernetes (đã thống nhất: k8s chỉ khi đã đông user).

## Quyết định
- **Đóng gói Docker**; ứng dụng **stateless** (mọi state đẩy ra Postgres — ADR-0018).
- Chạy trên **AWS**. Ánh xạ dịch vụ (đề xuất, chốt khi triển khai):
  - **ECS/Fargate** chạy container (không cần quản k8s); lên **EKS** sau nếu cần.
  - **RDS for PostgreSQL** (+ pgvector) cho checkpoint/audit/case/vector.
  - **Secrets Manager** giữ OpenAI key, DB creds (không để trong code/repo).
  - **SQS** cho case queue Review (hoặc bảng Postgres ở bản tối giản).
  - **S3** lưu tài liệu chính sách nguồn (trước khi ingest vào RAG).
  - **CloudWatch** cho log/metrics/alert (kèm observability — xem integration-infra).

## Lý do
- Docker stateless → scale ngang dễ, môi trường nhất quán dev→prod.
- AWS có dịch vụ quản lý sẵn (RDS, Fargate) → ít việc vận hành, hợp đội nhỏ.
- Bắt đầu Fargate thay vì EKS → tránh độ phức tạp k8s khi chưa cần.

## Phương án đã cân nhắc
- **Kubernetes (EKS) ngay** — mạnh nhưng phức tạp, chưa cần ở giai đoạn đầu.
- **Cloud khác / on-prem** — không chọn theo yêu cầu (AWS).

## Hệ quả
- (+) Triển khai gọn, mở rộng được, tận dụng dịch vụ quản lý AWS.
- (−) Phụ thuộc hệ sinh thái AWS; cần cấu hình mạng/bảo mật (VPC, IAM) đúng chuẩn.
- (−) Lưu ý chủ quyền dữ liệu: cân nhắc **region** AWS phù hợp yêu cầu dữ liệu (phối hợp pháp chế).
