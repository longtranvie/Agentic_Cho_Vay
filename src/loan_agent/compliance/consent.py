"""Thu thập đồng ý xử lý dữ liệu cá nhân — NĐ356/2025 Điều 6.

Đồng ý phải: (1) TRƯỚC khi xử lý, (2) cụ thể về mục đích, (3) kiểm chứng được (lưu
version + thời điểm), (4) không mặc định (khách chủ động xác nhận). Bản notice có
version để biết khách đã đồng ý với nội dung nào.
"""

from __future__ import annotations

CONSENT_VERSION = "2026-06-09"


def build_consent_notice() -> dict:
    """Nội dung khách cần đồng ý trước khi hệ thống thu thập/xử lý hồ sơ."""
    return {
        "version": CONSENT_VERSION,
        "tieu_de": "Đồng ý xử lý dữ liệu cá nhân để thẩm định khoản vay",
        "muc_dich": [
            "Thu thập & xử lý thông tin hồ sơ (tuổi, thu nhập, dư nợ, lịch sử tín "
            "dụng) để thẩm định khả năng vay.",
            "Xử lý TỰ ĐỘNG bằng bộ quy tắc tín dụng để ra quyết định sơ bộ.",
            "Có thể chuyển dữ liệu đã ẩn danh ra nước ngoài (OpenAI) cho bước hội "
            "đồng phân tích.",
        ],
        "quyen_cua_ban": [
            "Rút lại đồng ý bất cứ lúc nào (không hồi tố phần đã xử lý).",
            "Yêu cầu nhân viên xét duyệt lại quyết định tự động.",
            "Từ chối — khi đó hệ thống sẽ KHÔNG xử lý hồ sơ của bạn.",
        ],
        "co_so_phap_ly": (
            "NĐ 356/2025/NĐ-CP (Điều 6 đồng ý, Điều 25 chuyển dữ liệu xuyên biên "
            "giới); Luật 91/2025/QH15."
        ),
        "luu_y": "Đồng ý phải do bạn chủ động xác nhận; hệ thống không mặc định đồng ý.",
    }
