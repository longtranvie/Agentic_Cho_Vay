# Yêu cầu dữ liệu (Data Requirements)

Liệt kê mọi loại dữ liệu hệ thống cần, nguồn, chủ sở hữu và trạng thái. Dùng để
team Vapp biết phải chuẩn bị gì.

## 1. Bức tranh tổng — 7 nhóm dữ liệu

| Nhóm | Dùng để | Nguồn / Chủ sở hữu | Trạng thái |
|---|---|---|---|
| **A. Hồ sơ user** (core + review fields) | Đầu vào thẩm định | User khai / Vapp pre-fill / CIC | 🟡 Tùy "Vapp cho đọc gì" |
| **B. Config quyết định** | Cỗ máy ra quyết định | Rủi ro + Pháp chế Vapp | 🔴 **Blocker** |
| **C. Tài liệu chính sách** (RAG) | Tra cứu/trích dẫn | Pháp chế/sản phẩm Vapp + văn bản NHNN công khai | 🔴 **Blocker cho RAG** (lớp NHNN đã có) |
| **D. Vay-trả lịch sử** (có nhãn) | Hiệu chỉnh scorecard + ML sau | Vận hành Vapp / CIC | 🟢 Dev dùng proxy được |
| **E. Bộ eval** (golden set) | Đo đúng/sai + regression gate | Chuyên gia rủi ro Vapp | 🟡 Tạo giả lập được |
| **F. Vận hành/audit** | Giải trình, giám sát | Hệ thống tự sinh (Postgres) | 🟢 Chỉ cần thiết kế lưu |
| **G. Mapping ẩn danh PII** | Bóc/khôi phục danh tính | Hệ thống (Postgres, nhạy cảm) | 🟡 Cần thiết kế |

## 2. Chi tiết nhóm B — Config quyết định (đã phình to)

Không chỉ bảng điểm scorecard, mà gồm (tất cả **versioned**, do rủi ro+pháp chế sở hữu):
- Bảng điểm scorecard + knock-out + dải điểm ([ADR-0014](adr/0014-mo-hinh-rui-ro-scorecard.md))
- Lãi cố định + trần NHNN ([ADR-0015](adr/0015-lai-suat-co-dinh.md))
- Ngưỡng convene check tranh luận ([ADR-0023](adr/0023-giao-thuc-tranh-luan.md))
- Ánh xạ cờ rủi ro → hành động ([ADR-0022](adr/0022-quyet-dinh-tranh-luan-co-cong.md))
- **Persona/system prompt** từng agent hội đồng + Intake (artifact có version)

## 3. Chi tiết nhóm F — Audit (đã phình to)

- Toàn bộ **transcript tranh luận** ([ADR-0022](adr/0022-quyet-dinh-tranh-luan-co-cong.md))
- **Snapshot case** khi Review ([ADR-0012](adr/0012-co-che-review.md))
- Chi phí token/phiên (PR-4); version model/prompt/config mỗi quyết định (PR-6)

## 4. Nguồn dữ liệu THẬT đã khảo sát

### 4a. Tài liệu chính sách (nhóm C) — tiếng Việt, công khai ✅
| Văn bản | Vai trò | Nguồn |
|---|---|---|
| VBHN 06/VBHN-NHNN 2026 (TT39 + TT06/2023 + TT12/2024 + TT52/2025) | Hoạt động cho vay TCTD — **bản hợp nhất hiện hành** | [thuvienphapluat](https://thuvienphapluat.vn/van-ban/Tien-te-Ngan-hang/Van-ban-hop-nhat-06-VBHN-NHNN-2026-Thong-tu-hoat-dong-cho-vay-cua-to-chuc-tin-dung-doi-voi-khach-hang-692624.aspx) |
| Thông tư 12/2024/TT-NHNN | Sửa đổi TT39 (hiệu lực 1/7/2024) | [luatvietnam](https://luatvietnam.vn/tai-chinh/thong-tu-12-2024-tt-nhnn-sua-doi-tt-39-2016-tt-nhnn-quy-dinh-ve-hoat-dong-cho-vay-358296-d1.html) |
| Thông tư 43/2016/TT-NHNN | Cho vay tiêu dùng (công ty tài chính); **trần 100tr/khách** | [thuvienphapluat](https://thuvienphapluat.vn/van-ban/Tien-te-Ngan-hang/Thong-tu-43-2016-TT-NHNN-cho-vay-tieu-dung-cua-cong-ty-tai-chinh-326281.aspx) |
| Thông tư 18/2019/TT-NHNN | Sửa đổi TT43 | [luatvietnam](https://luatvietnam.vn/tai-chinh/thong-tu-18-2019-tt-nhnn-sua-doi-thong-tu-43-2016-cho-vay-tieu-dung-cua-cong-ty-tai-chinh-178364-d1.html) |
| Luật 91/2025/QH15 + NĐ 356/2025/NĐ-CP | Bảo vệ DLCN — **thay NĐ13/2023** (cho phần ẩn danh PII) | [NĐ356 chinhphu](https://vanban.chinhphu.vn/?pageid=27160&docid=216387) |

> Cấu trúc Điều/Khoản/Điểm đã khảo sát từ TT39 → schema chunk chi tiết: [rag-design.md §2](rag-design.md).
> Đây là **lớp pháp lý**; chính sách **sản phẩm nội bộ Vapp** vẫn phải do Vapp cấp.

### 4b. Dữ liệu cho mô hình/dev (nhóm D, E) — proxy quốc tế
| Dataset | Mô tả | Dùng để | Nguồn |
|---|---|---|---|
| Home Credit Default Risk | Hồ sơ vay + nhãn vỡ nợ (Home Credit có ở VN → schema sát) | Dev + phương pháp scorecard | [Kaggle](https://www.kaggle.com/c/home-credit-default-risk/data) |
| HMEQ | 5.960 khoản, kinh điển | Học/dựng scorecard | (trong tutorial dưới) |
| vnpdf-financial-reports | Báo cáo tài chính VN (PDF) | Test trích xuất/embeddings tiếng Việt | [HuggingFace](https://huggingface.co/datasets/kiethuynhanh/vnpdf-financial-reports-dataset) |

> ⚠️ Proxy quốc tế **không phải dân số VN/tiếng Việt** → chỉ dev + học phương pháp,
> KHÔNG calibrate production. **Kiểm tra license/ToS** trước khi dùng.
> Tài liệu học tiếng Việt: [Credit Scorecard — deepai-book](https://phamdinhkhanh.github.io/deepai-book/ch_ml/creditScorecard.html).

### 4c. CIC — nguồn thật nhưng KHÔNG mở
[cic.gov.vn](https://cic.gov.vn/): chỉ tổ chức được cấp quyền truy cập theo lô; cá
nhân chỉ xem hồ sơ mình. → CIC là **việc tích hợp**, không phải dataset tải về.

## 5. Kế hoạch dữ liệu theo giai đoạn

| Nhóm | Dev (giờ) | Production (sau) |
|---|---|---|
| C. Chính sách | Văn bản NHNN công khai + policy Vapp giả lập | + chính sách nội bộ Vapp thật |
| D. Vay-trả nhãn | Home Credit/HMEQ (proxy) | Nội bộ Vapp / CIC |
| E. Eval golden set | Hồ sơ VN giả lập (chuyên gia gán nhãn, VND, nghề VN) | + ca thật đã review |
| A. Schema input | Đối chiếu feature Home Credit | Dữ liệu Vapp |

**An toàn PII khi dev:** dùng văn bản công khai (RAG) + Home Credit (đã ẩn danh sẵn)
→ không đụng Luật 91/2025 / NĐ 356/2025 trong lúc phát triển.

## 6. Đề xuất bộ dữ liệu giả lập cho dev

Để dựng & test skeleton trước khi có dữ liệu thật:
- ~20–50 **hồ sơ vay VN giả lập** đa dạng (đậu/rớt/biên) — chuyên gia gán nhãn → nhóm A + E.
- 4–6 **tài liệu chính sách giả** + vài Điều thật từ TT39/43 → nhóm C (test RAG).
- 1 bộ **config expert-set** (bảng điểm + ngưỡng mẫu) → nhóm B.

> Liên quan: câu hỏi mở về nguồn dữ liệu → [open-questions.md](open-questions.md).
