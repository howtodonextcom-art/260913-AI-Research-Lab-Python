"""Integrity and merge fail-closed tests."""

from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from vietlott_quant_lab.data.errors import MergeConflictError
from vietlott_quant_lab.data.integrity import check_integrity
from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.data.sync import merge_draws


def _draw(
    draw_id: str,
    day: date,
    numbers: tuple[int, ...],
) -> DrawRecord:
    return DrawRecord(
        draw_id=draw_id,
        draw_date=day,
        numbers=numbers,
        source_url=f"https://vietlott.vn/x?id={draw_id}&nocatche=1",
        fetched_at=datetime(2026, 9, 13, tzinfo=UTC),
    )


def test_integrity_detects_missing_ids() -> None:
    records = [
        _draw("00001", date(2016, 7, 20), (2, 17, 33, 37, 38, 45)),
        _draw("00003", date(2016, 7, 22), (1, 2, 3, 4, 5, 6)),
    ]
    report = check_integrity(records)
    assert not report.ok
    assert any("missing" in i for i in report.issues)


def test_integrity_pass_continuous() -> None:
    records = [
        _draw("00001", date(2016, 7, 20), (2, 17, 33, 37, 38, 45)),
        _draw("00002", date(2016, 7, 22), (1, 2, 3, 4, 5, 6)),
    ]
    report = check_integrity(records)
    assert report.ok


def test_merge_conflict_fail_closed(tmp_path: Path) -> None:
    existing = [_draw("00001", date(2016, 7, 20), (2, 17, 33, 37, 38, 45))]
    incoming = [_draw("00001", date(2016, 7, 20), (1, 2, 3, 4, 5, 6))]
    with pytest.raises(MergeConflictError) as exc:
        merge_draws(existing, incoming, conflict_dir=tmp_path)
    assert exc.value.code == "MERGE_CONFLICT"
    artifacts = list(tmp_path.glob("reconcile_*.json"))
    assert len(artifacts) == 1
    # Existing list unchanged by failed merge path (caller never wrote).
    assert existing[0].numbers == (2, 17, 33, 37, 38, 45)


def test_merge_adds_new() -> None:
    existing = [_draw("00001", date(2016, 7, 20), (2, 17, 33, 37, 38, 45))]
    incoming = [_draw("00002", date(2016, 7, 22), (1, 2, 3, 4, 5, 6))]
    result = merge_draws(existing, incoming, conflict_dir=None)
    assert result.added == 1
    assert len(result.merged) == 2
