"""Parser fixture tests (no live Vietlott)."""

from __future__ import annotations

from pathlib import Path

import pytest

from vietlott_quant_lab.data.errors import SourceSchemaChangedError
from vietlott_quant_lab.data.parser import (
    discover_history_key,
    parse_detail_html,
    parse_history_html,
    parse_vietnamese_date,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_history_sample() -> None:
    html = (FIXTURES / "history_sample.html").read_text(encoding="utf-8")
    outcome = parse_history_html(html, trust_empty_page=False)
    assert outcome.state == "PARSE_SUCCESS"
    assert len(outcome.rows) == 8
    assert outcome.rows[0].draw_id == "01561"
    assert outcome.rows[0].numbers == (14, 18, 20, 21, 26, 27)
    assert discover_history_key(html) == "e3a051eb"


def test_empty_history_without_trust_raises_schema_changed() -> None:
    html = (FIXTURES / "history_empty.html").read_text(encoding="utf-8")
    with pytest.raises(SourceSchemaChangedError) as exc:
        parse_history_html(html, trust_empty_page=False)
    assert exc.value.code == "SOURCE_SCHEMA_CHANGED"


def test_empty_history_with_trust_is_valid_eof() -> None:
    html = (FIXTURES / "history_empty.html").read_text(encoding="utf-8")
    outcome = parse_history_html(html, trust_empty_page=True)
    assert outcome.state == "PARSE_EMPTY_VALID_PAGE"
    assert outcome.rows == ()


def test_missing_wrapper_raises() -> None:
    with pytest.raises(SourceSchemaChangedError):
        parse_history_html("<div>no table</div>", trust_empty_page=False)


def test_parse_detail_sample() -> None:
    html = (FIXTURES / "detail_sample.html").read_text(encoding="utf-8")
    row = parse_detail_html(html)
    assert row.draw_id == "00001"
    assert row.draw_date.isoformat() == "2016-07-20"
    assert row.numbers == (2, 17, 33, 37, 38, 45)


def test_parse_vietnamese_date() -> None:
    assert parse_vietnamese_date("20/07/2016").isoformat() == "2016-07-20"
