"""DrawRecord schema tests."""

from __future__ import annotations

from datetime import UTC, date, datetime

import pytest
from pydantic import ValidationError

from vietlott_quant_lab.data.schema import DrawRecord


def _valid(**overrides: object) -> DrawRecord:
    base: dict[str, object] = {
        "draw_id": "00001",
        "draw_date": date(2016, 7, 20),
        "numbers": (45, 2, 17, 33, 37, 38),
        "source_url": "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/645?id=00001&nocatche=1",
        "fetched_at": datetime(2026, 9, 13, tzinfo=UTC),
    }
    base.update(overrides)
    return DrawRecord.model_validate(base)


def test_numbers_sorted_and_product_default() -> None:
    rec = _valid()
    assert rec.product == "mega645"
    assert rec.numbers == (2, 17, 33, 37, 38, 45)


def test_rejects_bad_draw_id() -> None:
    with pytest.raises(ValidationError):
        _valid(draw_id="1")


def test_rejects_duplicate_numbers() -> None:
    with pytest.raises(ValidationError):
        _valid(numbers=(1, 1, 2, 3, 4, 5))


def test_rejects_out_of_range() -> None:
    with pytest.raises(ValidationError):
        _valid(numbers=(1, 2, 3, 4, 5, 99))


def test_rejects_wrong_count() -> None:
    with pytest.raises(ValidationError):
        _valid(numbers=(1, 2, 3, 4, 5))
