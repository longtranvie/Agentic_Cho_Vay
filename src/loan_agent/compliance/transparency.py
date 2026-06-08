"""Thông báo minh bạch xử lý tự động — NĐ356/2025.

Báo cho chủ thể: quyết định do hệ thống TỰ ĐỘNG đưa ra + giải thích nguyên tắc + quyền
yêu cầu người xét duyệt. Giải thích dựng từ dữ kiện TẤT ĐỊNH (điểm, DTI, knock-out,
trích dẫn) — KHÔNG do LLM, để chính xác và tái lập được.
"""

from __future__ import annotations

_OUTCOME_VI = {
    "approve": "ĐỀ XUẤT DUYỆT",
    "reject": "TỪ CHỐI",
    "review": "CHUYỂN XÉT DUYỆT THỦ CÔNG",
}


def build_notice(result: dict) -> dict:
    """Dựng thông báo minh bạch từ state cuối của pipeline."""
    decision = result.get("decision", {})
    risk = result.get("risk", {})
    aff = result.get("affordability", {})
    policy = result.get("policy", {})
    outcome = decision.get("outcome", "")
    dti = risk.get("dti")
    dti_str = f"{dti:.2f}" if isinstance(dti, (int, float)) else "?"

    return {
        "xu_ly_tu_dong": True,
        "thong_bao": (
            "Quyết định này được hệ thống XỬ LÝ TỰ ĐỘNG đưa ra dựa trên bộ quy tắc tín "
            "dụng. Bạn có quyền yêu cầu nhân viên xét duyệt xem lại."
        ),
        "ket_qua": _OUTCOME_VI.get(outcome, outcome),
        "ly_do": decision.get("reasons", []),
        "nguyen_tac_thuat_toan": [
            f"Điểm tín dụng {risk.get('score', '?')}/100 so với ngưỡng duyệt trong cấu hình.",
            f"Tỷ lệ trả nợ trên thu nhập (DTI) {dti_str}.",
            "Kiểm tra điều kiện cứng: tuổi, thu nhập tối thiểu, trần khoản vay.",
            "Quyết định cuối do bộ quy tắc tất định, không do mô hình ngôn ngữ.",
        ],
        "han_muc_uoc_tinh": aff.get("max_principal"),
        "chinh_sach_dan_chieu": [
            {"nguon": c.get("source"), "dieu": c.get("dieu")}
            for c in policy.get("citations", [])
        ],
        "co_so_phap_ly": "NĐ 356/2025/NĐ-CP — minh bạch xử lý dữ liệu tự động.",
    }
