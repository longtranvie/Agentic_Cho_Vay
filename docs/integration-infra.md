# Tích hợp Vapp & Hạ tầng

Tổng hợp cách Vapp gọi hệ thống và cách hệ thống chạy production. Lý do từng lựa
chọn nằm ở ADR-0017 → ADR-0020.

## 1. API — Vapp gọi hệ thống ([ADR-0017](adr/0017-api-contract.md))

Hội thoại nhiều lượt → **REST theo phiên**:

```
POST /applications                 → tạo phiên (user_id từ Vapp) → application_id
POST /applications/{id}/messages   → gửi tin nhắn user → phản hồi agent + trạng thái
GET  /applications/{id}            → trạng thái/kết quả hiện tại
POST /applications/{id}/resume     → (nội bộ) nối tiếp sau khi người duyệt ca Review
```

- **Streaming** (SSE/WebSocket): hiện chữ dần như chat (vai nhân viên — FR-11).
- **Webhook**: ca Review → trả "đang xử lý" → callback Vapp khi người quyết xong.
- **Auth**: dịch vụ↔dịch vụ bằng API key/JWT/mTLS; `user_id` do Vapp truyền.

## 2. Lưu trữ — Postgres xương sống ([ADR-0018](adr/0018-postgres-luu-tru.md))

| Mục đích | Lưu ở | Ghi chú |
|---|---|---|
| Checkpoint (state hội thoại) | Postgres | SQLite chỉ cho dev |
| Audit trail (quyết định + version) | Postgres | PR-6 |
| Case queue (Review) | SQS hoặc bảng Postgres | ADR-0012 |
| Vector store (kho chính sách) | pgvector trong Postgres | ADR-0005 |
| Config/decision table (scorecard, lãi) | versioned (DB/git) | ADR-0014 |

## 3. Bảo mật & PII — ẩn danh trước khi gửi ([ADR-0019](adr/0019-an-danh-pii.md))

- **Ẩn danh hóa MỌI dữ liệu rời hệ thống** (OpenAI, LangSmith, log): bóc định danh
  trực tiếp (tên/CCCD/SĐT/địa chỉ), chỉ gửi dữ liệu cần để suy luận.
- **Redact PII trong văn bản tự do** của user (outbound).
- Mapping pseudonym ↔ danh tính giữ nội bộ (Postgres).
- Secrets (OpenAI key, DB creds) trong **AWS Secrets Manager**, không nằm trong repo.
- **⚠️ Mở:** pháp chế Vapp xác nhận mức ẩn danh có đủ tuân thủ Nghị định 13 & NHNN.

## 4. Observability ([PR-3]) — *trace cũng phải sạch PII (ADR-0019)*

- **Tracing**: LangSmith (bản đầu) — theo dõi từng phiên/bước agent.
- **Metrics**: độ trễ, **chi phí token/phiên** (PR-4), tỉ lệ Duyệt/Từ chối/Review, lỗi.
- **Logging**: có **redaction PII**.
- **Alert**: vượt ngưỡng chi phí, lỗi tăng, sự kiện degrade.

## 5. Triển khai — Docker trên AWS ([ADR-0020](adr/0020-trien-khai-docker-aws.md))

- **Docker**, app **stateless** (state ở Postgres) → scale ngang.
- **AWS**: ECS/Fargate (chạy container, chưa cần k8s) · RDS Postgres+pgvector ·
  Secrets Manager · SQS (case queue) · S3 (tài liệu chính sách) · CloudWatch.
- Lên **EKS** (k8s) sau nếu đông user.
- **Region**: cân nhắc theo yêu cầu chủ quyền dữ liệu (phối hợp pháp chế).

## 6. Độ tin cậy & degrade an toàn ([PR-7])

- OpenAI lỗi/timeout → retry có backoff; quá hạn → thông báo lịch sự, **không bao
  giờ auto-duyệt**. Quyết định sơ bộ vẫn chạy bằng rule engine kể cả khi phần diễn
  giải LLM lỗi.
- Rate limit theo user/phiên (PR-5).

## 7. CI/CD ([PR-8])

- Môi trường dev / staging / prod.
- **Cổng eval (regression gate)**: trước khi deploy, chạy bộ hồ sơ mẫu; nếu tăng
  tỉ lệ **duyệt sai** → **chặn deploy**.

## 8. Còn mở

- Định nghĩa chi tiết request/response của API với Vapp.
- Region AWS + cấu hình VPC/IAM.
- Chọn reranker cho RAG (xem `rag-design.md`).
- Pháp chế xác nhận mức ẩn danh PII (ADR-0019).
