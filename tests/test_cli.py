from loan_agent.cli import _parse, _parse_bool, _parse_money, _parse_source


def test_parse_money_handles_trieu_and_separators():
    assert _parse_money("10tr") == 10_000_000
    assert _parse_money("50 triệu") == 50_000_000
    assert _parse_money("20.000.000") == 20_000_000
    assert _parse_money("0") == 0


def test_parse_source_by_number_and_word():
    assert _parse_source("1") == "luong"
    assert _parse_source("kinh doanh") == "kinh_doanh"


def test_parse_bool_late_payment():
    assert _parse_bool("1") is False  # chưa trễ hạn
    assert _parse_bool("2") is True  # đã từng


def test_parse_int_and_str():
    assert _parse("int", " 12 ") == 12
    assert _parse("str", " mua xe ") == "mua xe"
