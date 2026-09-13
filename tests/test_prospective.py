"""P10 prospective freeze / score hash-chain tests."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from tests.conftest_research import make_draw, synthetic_history

from vietlott_quant_lab.prospective.chain import (
    ChainIntegrityError,
    freezes_path,
    load_freezes,
    load_scores,
    verify_chain,
)
from vietlott_quant_lab.prospective.freeze import (
    ProspectiveFreezeError,
    freeze_ranking,
    next_draw_id,
)
from vietlott_quant_lab.prospective.score import pending_freezes, score_pending, scored_views
from vietlott_quant_lab.ranking.engine import MODEL_HOT, MODEL_RANDOM


def test_freeze_writes_immutable_record(tmp_path: Path) -> None:
    history = synthetic_history(40)
    target = next_draw_id(history)
    record = freeze_ranking(
        history,
        prospective_dir=tmp_path,
        model_id=MODEL_HOT,
        seed=1,
        frozen_at=datetime(2026, 9, 13, 12, 0, tzinfo=UTC),
    )
    assert record.target_draw_id == target
    assert len(record.ranking_01_45) == 45
    assert set(record.top7) <= set(record.top18)
    assert record.actual_numbers is None
    assert record.mcp is None
    loaded = load_freezes(tmp_path)
    assert len(loaded) == 1
    assert loaded[0].record_hash == record.record_hash
    verify_chain(tmp_path)


def test_hash_chain_verify_and_tamper_fails(tmp_path: Path) -> None:
    history = synthetic_history(30)
    freeze_ranking(history, prospective_dir=tmp_path, model_id=MODEL_RANDOM, seed=2)
    freeze_ranking(
        history,
        prospective_dir=tmp_path,
        model_id=MODEL_HOT,
        seed=3,
        target_draw_id=f"{int(next_draw_id(history)) + 1:05d}",
    )
    verify_chain(tmp_path)

    path = freezes_path(tmp_path)
    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    row = json.loads(lines[0])
    row["ranking_01_45"] = row["ranking_01_45"][::-1]
    # Keep nested pools consistent with tampered ranking so Pydantic accepts the row,
    # but record_hash no longer matches the payload.
    for m in range(7, 19):
        row[f"top{m}"] = row["ranking_01_45"][:m]
    lines[0] = json.dumps(row, ensure_ascii=False, sort_keys=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with pytest.raises(ChainIntegrityError):
        verify_chain(tmp_path)


def test_refuse_freeze_for_known_draw(tmp_path: Path) -> None:
    history = synthetic_history(25)
    known = history[-1].draw_id
    with pytest.raises(ProspectiveFreezeError, match="refuse freeze for known draw"):
        freeze_ranking(
            history,
            prospective_dir=tmp_path,
            model_id=MODEL_HOT,
            target_draw_id=known,
        )


def test_score_once_append_only(tmp_path: Path) -> None:
    history = synthetic_history(50, seed=7)
    # Freeze for next draw using history[:-1]; actual is history[-1].
    past = history[:-1]
    actual = history[-1]
    record = freeze_ranking(
        past,
        prospective_dir=tmp_path,
        model_id=MODEL_HOT,
        target_draw_id=actual.draw_id,
        seed=0,
    )
    assert pending_freezes(tmp_path)
    events = score_pending([*past, actual], prospective_dir=tmp_path)
    assert len(events) == 1
    assert events[0].freeze_record_hash == record.record_hash
    assert events[0].actual_numbers == actual.numbers
    assert events[0].mcp is not None
    assert 6 <= events[0].mcp <= 45
    assert 0 <= events[0].k18 <= 6

    # Freeze ledger unchanged (still null scored fields on disk).
    freeze_on_disk = load_freezes(tmp_path)[0]
    assert freeze_on_disk.actual_numbers is None
    assert freeze_on_disk.mcp is None

    views = scored_views(tmp_path)
    assert views[0].mcp == events[0].mcp
    assert views[0].actual_numbers == actual.numbers

    # Second score attempt: no new events (already scored).
    again = score_pending([*past, actual], prospective_dir=tmp_path)
    assert again == []
    assert len(load_scores(tmp_path)) == 1
    verify_chain(tmp_path)


def test_score_waits_until_draw_exists(tmp_path: Path) -> None:
    history = synthetic_history(20)
    freeze_ranking(history, prospective_dir=tmp_path, model_id=MODEL_HOT, seed=1)
    # Only history present — target is future → nothing scored.
    events = score_pending(history, prospective_dir=tmp_path)
    assert events == []
    assert len(pending_freezes(tmp_path)) == 1

    future_id = next_draw_id(history)
    future = make_draw(
        future_id,
        history[-1].draw_date,
        (1, 2, 3, 4, 5, 6),
    )
    events = score_pending([*history, future], prospective_dir=tmp_path)
    assert len(events) == 1
    assert events[0].target_draw_id == future_id
