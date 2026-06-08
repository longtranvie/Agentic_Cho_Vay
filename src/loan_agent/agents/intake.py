"""Intake Agent — nhân viên tín dụng ảo, slot-filling — ADR-0003/0011.

Trích field từ tin nhắn (qua LLM), validate, hỏi tiếp nếu thiếu core fields.
Mock LLM không trích được NL → hồ sơ đã đủ sẽ đi tiếp; demo nạp hồ sơ đủ sẵn.
"""

from __future__ import annotations

from ..schemas import LoanApplication


def _merge(app: LoanApplication, extracted: LoanApplication) -> LoanApplication:
    data = app.model_dump()
    for section, fields in extracted.model_dump().items():
        if isinstance(fields, dict):
            for field, value in fields.items():
                if value is not None:
                    data[section][field] = value
    return LoanApplication.model_validate(data)


def extract_and_ask(
    application: dict | None,
    messages: list,
    meta: dict | None,
    llm,
    max_turns: int,
) -> dict:
    """Trả patch state: application (đã merge) + meta(intake_ready/turns) + (câu hỏi)."""
    app = LoanApplication.model_validate(application or {})
    meta = dict(meta or {})

    if not app.is_complete():
        user_msgs = [m for m in messages if m.get("role") == "user"]
        if user_msgs and meta.get("intake_turns", 0) < max_turns:
            extracted = llm.structured(
                f"Trích thông tin hồ sơ vay từ câu: {user_msgs[-1]['content']}",
                LoanApplication,
            )
            app = _merge(app, extracted)

    if app.is_complete():
        meta["intake_ready"] = True
        return {"application": app.model_dump(mode="json"), "meta": meta}

    meta["intake_ready"] = False
    meta["intake_turns"] = meta.get("intake_turns", 0) + 1
    missing = app.missing_required_fields()
    question = f"Bạn cho mình biết thêm: {missing[0].replace('.', ' → ')}?"
    return {
        "application": app.model_dump(mode="json"),
        "meta": meta,
        "messages": [{"role": "assistant", "content": question}],
    }
