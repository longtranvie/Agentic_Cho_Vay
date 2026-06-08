# Kiến trúc tổng thể

## 1. Tổng quan

Hệ thống mô phỏng một **hội đồng thẩm định tín dụng**: nhiều **agent có vai riêng
tranh luận với nhau** (debate pattern) để phân tích hồ sơ, được một **Moderator/
Judge** điều phối. Tranh luận để **phân tích**; **quyết định cuối vẫn qua một cổng
xác định (rule engine backstop)** — agent có thể đẩy xuống Review/Từ chối nhưng
**không thể tự duyệt vượt một luật cứng** (ADR-0021, ADR-0022). Chạy trên
**LangGraph** (state machine có checkpoint).

```
   [Vapp] user đã đăng nhập, "Tôi muốn vay 10tr"
                         │
                         ▼
                  ┌──────────────┐  nạp dữ liệu Vapp (KYC, thu nhập…) — deterministic
                  │  Bootstrap   │
                  └──────┬───────┘
                         ▼
                  ┌──────────────┐◄─┐ còn thiếu → hỏi tiếp
                  │   Intake     │  │ (agent: nhân viên tín dụng ảo)
                  └──────┬───────┘──┘
                         ▼
                  ┌──────────────┐  hạn mức tối đa + counter-offer — deterministic
                  │ Affordability│
                  └──────┬───────┘
                         ▼
                  ┌──────────────┐  knock-out + scorecard (SỐ) — deterministic
                  │  Pre-checks  │  (ADR-0014); knock-out → tới Gate luôn
                  └──────┬───────┘
                         ▼
        ╔════════════════════════════════════════╗
        ║   DELIBERATION — hội đồng tranh luận    ║  (các agent LLM nói chuyện,
        ║                                          ║   phản biện nhau qua N vòng)
        ║   Risk Analyst ◄─► Advocate ◄─► Skeptic ║
        ║          ▲           ▲          ▲        ║
        ║          └─ Policy/Compliance (RAG) ─┘   ║
        ║                    │                     ║
        ║          Moderator/Judge → khuyến nghị + ║
        ║                            lý do + cờ    ║
        ╚════════════════════┬═════════════════════╝
                             ▼
                  ┌──────────────────┐  kết hợp: knock-out + điểm số + khuyến nghị
                  │  DECISION GATE   │  dưới luật cứng (deterministic backstop)
                  │ (rule backstop)  │  → Duyệt / Từ chối / Review
                  └──────┬───────────┘
              review │    └──► Duyệt / Từ chối ──► finalize ──► trả Vapp
                     ▼
                  ┌──────────────┐  hỏi thêm review fields → interrupt + tạo case
                  │ Review prep  │
                  └──────┬───────┘
                         ▼
                  ┌──────────────┐
                  │ Human review │  resume sau khi người quyết
                  └──────────────┘
```

## 2. Các agent

Phân loại: **agent LLM** (có suy luận) vs **node công cụ** (deterministic, không LLM).

### 2.1 Bootstrap (node công cụ — không LLM)
- Nạp dữ liệu Vapp đã có về user (KYC, thu nhập, lịch sử…) để **pre-fill** hồ sơ.
- Intake chỉ hỏi phần **còn thiếu** → đỡ phiền, chính xác hơn (xem ADR-0014 nếu chốt được nguồn dữ liệu).
- *Trạng thái: phụ thuộc câu hỏi mở "Vapp có sẵn dữ liệu nào" (requirements mục 9).*

### 2.2 Intake Agent (LLM — nhân viên tín dụng ảo, FR-11)
- Đóng vai nhân viên: hội thoại tự nhiên, dẫn dắt, giải thích; giọng thân thiện,
  chuyên nghiệp, **không cam kết pháp lý**.
- **Loop**: còn thiếu trường bắt buộc → hỏi tiếp; đủ + hợp lệ → chuyển bước.
- Trích nhiều trường từ một câu trả lời, hỏi gộp khi hợp lý.
- Validate ngay; xử lý lạc đề/từ chối/mâu thuẫn/gaming (requirements mục 7).
- **Giới hạn số lần hỏi**. Hỏi *core fields* trước; *review fields* chỉ khi cần (ADR-0011).

### 2.3 Affordability (node công cụ — không LLM, ADR-0010)
- Tính **hạn mức vay tối đa** theo khả năng chi trả (phép tính ngược, deterministic).
- Chạy **sớm** để báo cho user và làm **counter-offer** nếu số xin vượt khả năng.

### 2.4 Pre-checks (node công cụ — không LLM, ADR-0014)
- **Knock-out** (loại thẳng) + **scorecard** chấm điểm SỐ theo 2 chiều: capacity +
  willingness. Tham số ở **config có version**, không hard-code.
- Knock-out → đi thẳng tới Decision Gate (bỏ qua tranh luận). Chi tiết: `risk-model.md`.

### 2.5 Hội đồng tranh luận (Deliberation — các agent LLM, ADR-0021/0023)
**Convene check** (deterministic) trước: ca rõ ràng bỏ qua/họp nhẹ, chỉ ca mập mờ
mới họp đầy đủ (tiết kiệm chi phí — ADR-0023). Khi họp, các agent **phản biện nhau**
song song qua tối đa 2 vòng (Judge dừng sớm khi hội tụ):
- **Risk Analyst** — phân tích định tính rủi ro dựa trên số liệu & hồ sơ.
- **Advocate** ("luật sư của khách") — lập luận các điểm có lợi, đề nghị duyệt.
- **Skeptic / Underwriter** — phản biện, bới rủi ro (devil's advocate).
- **Policy/Compliance (RAG)** — kéo dẫn chứng chính sách vào tranh luận (ADR-0016).
- **Moderator/Judge** — điều phối, tổng hợp thành **khuyến nghị + lý do + cờ rủi ro**.
> Tranh luận chỉ để **phân tích**; không tự chốt cho vay (xem Decision Gate).
> Giao thức chi tiết (vòng, dừng, cờ rủi ro): `debate-protocol.md`.

### 2.6 Decision Gate (deterministic backstop — ADR-0022)
- Kết hợp: kết quả **knock-out** + **điểm số** + **khuyến nghị tranh luận**, dưới
  **luật cứng xác định**.
- Outcome: Duyệt / Từ chối / **Review**. Tranh luận có thể **hạ** xuống Review/Từ
  chối, nhưng **không thể tự duyệt** vượt một luật cứng/điểm số không đạt.
- Lý do cuối = tổng hợp của Judge + reason codes; lưu **toàn bộ transcript** để audit.

### 2.7 Review prep + Human-in-the-loop (ADR-0012)
- Khi outcome = Review: hỏi thêm *review fields*, rồi **interrupt + checkpoint**.
- Tạo **case** kèm snapshot ngữ cảnh (gồm transcript tranh luận) → hàng đợi nhân viên.
- Nhân viên quyết → **resume** graph → trả kết quả về user.

## 3. Luồng dữ liệu (state)

State của LangGraph mang theo toàn phiên:
- `messages`: lịch sử hội thoại với user.
- `application`: hồ sơ vay đang được lấp đầy (core + review fields).
- `provenance`: nguồn mỗi field ("từ Vapp" vs "user khai") → độ tin.
- `affordability`: hạn mức tối đa + counter-offer (nếu có).
- `risk`: kết quả knock-out + điểm scorecard + reason codes.
- `deliberation`: **transcript tranh luận** + khuyến nghị + cờ rủi ro của Judge.
- `policy`: trích dẫn chính sách liên quan.
- `decision`: outcome cuối (từ Decision Gate) + lý do tổng hợp.
- `case`: thông tin case khi chuyển Review (id, snapshot, trạng thái).
- `meta`: intake_turns, phase, versions (model/prompt/config), pii_map_ref.

> Phiên được checkpoint theo `user_id` + `application_id`, có **TTL** cho hồ sơ dở (ADR-0013).

## 4. Stack kỹ thuật

| Thành phần | Lựa chọn |
|------------|----------|
| Điều phối | LangGraph |
| LLM | OpenAI (function calling) |
| Embeddings | OpenAI `text-embedding-3` |
| Vector store | pgvector trong Postgres (ADR-0018); Chroma cho dev |
| Schema/validation | Pydantic |
| Lưu trạng thái | LangGraph checkpointer — **Postgres** (prod), SQLite (dev) — ADR-0018 |
| API | REST theo phiên + streaming + webhook (ADR-0017) |
| Triển khai | Docker trên AWS (ECS/Fargate, RDS, SQS, S3) — ADR-0020 |
| Bảo mật PII | Ẩn danh trước khi gửi ra ngoài (ADR-0019) |
| Observability | LangSmith (trace), CloudWatch (log/metrics) |

## 5. Tham chiếu quyết định

Lý do đằng sau các lựa chọn trên được ghi trong [adr/](adr/).
