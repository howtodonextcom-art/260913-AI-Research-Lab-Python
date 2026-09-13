"""Score pending freezes once actual draws appear (append-only ScoreEvent)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path

from vietlott_quant_lab.config.constants import POOL_SIZES
from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.prospective.chain import (
    append_score,
    compute_record_hash,
    load_freezes,
    load_scores,
    tip_hash,
)
from vietlott_quant_lab.prospective.types import (
    ProspectiveRecord,
    ScoreEvent,
    with_score,
)
from vietlott_quant_lab.statistics.metrics import (
    intersection_k,
    mcp_from_ranking,
    winner_ranks,
)


class ProspectiveScoreError(ValueError):
    """Raised when scoring cannot proceed safely."""


def _ranking_map(freeze: ProspectiveRecord) -> dict[int, int]:
    """number → rank (1 = best) from frozen ranking_01_45 order."""
    return {number: rank for rank, number in enumerate(freeze.ranking_01_45, start=1)}


def build_score_event(
    freeze: ProspectiveRecord,
    actual: DrawRecord,
    *,
    previous_hash: str,
    scored_at: datetime | None = None,
) -> ScoreEvent:
    if actual.draw_id != freeze.target_draw_id:
        raise ProspectiveScoreError(
            f"draw_id mismatch: freeze={freeze.target_draw_id} actual={actual.draw_id}"
        )
    ranking = _ranking_map(freeze)
    ranks = winner_ranks(ranking, actual.numbers)
    mcp = mcp_from_ranking(ranking, actual.numbers)
    k_by_m = {m: intersection_k(freeze.pool(m), actual.numbers) for m in POOL_SIZES}

    draft = ScoreEvent(
        freeze_record_hash=freeze.record_hash,
        target_draw_id=freeze.target_draw_id,
        actual_numbers=actual.numbers,
        k18=k_by_m[18],
        k17=k_by_m[17],
        k16=k_by_m[16],
        k15=k_by_m[15],
        k14=k_by_m[14],
        k13=k_by_m[13],
        k12=k_by_m[12],
        k11=k_by_m[11],
        k10=k_by_m[10],
        k9=k_by_m[9],
        k8=k_by_m[8],
        k7=k_by_m[7],
        mcp=mcp,
        winner_ranks=ranks,
        scored_at=scored_at or datetime.now(UTC),
        record_hash="pending",
        previous_hash=previous_hash,
    )
    digest = compute_record_hash(draft.score_payload_for_hash())
    return draft.model_copy(update={"record_hash": digest})


def pending_freezes(
    prospective_dir: Path,
    *,
    available_draw_ids: set[str] | None = None,
) -> list[ProspectiveRecord]:
    """Freezes not yet scored; optionally only those whose draw is available."""
    scored = {s.freeze_record_hash for s in load_scores(prospective_dir)}
    out: list[ProspectiveRecord] = []
    for freeze in load_freezes(prospective_dir):
        if freeze.record_hash in scored:
            continue
        if available_draw_ids is not None and freeze.target_draw_id not in available_draw_ids:
            continue
        out.append(freeze)
    return out


def score_pending(
    draws: Sequence[DrawRecord],
    *,
    prospective_dir: Path,
    scored_at: datetime | None = None,
) -> list[ScoreEvent]:
    """Append ScoreEvent rows for pending freezes whose target draw is now known.

    Freeze JSONL lines are never rewritten. Each freeze is scored at most once.
    """
    by_id: Mapping[str, DrawRecord] = {d.draw_id: d for d in draws}
    events: list[ScoreEvent] = []
    for freeze in pending_freezes(
        prospective_dir,
        available_draw_ids=set(by_id),
    ):
        actual = by_id[freeze.target_draw_id]
        event = build_score_event(
            freeze,
            actual,
            previous_hash=tip_hash(load_scores(prospective_dir)),
            scored_at=scored_at,
        )
        append_score(prospective_dir, event)
        events.append(event)
    return events


def scored_views(prospective_dir: Path) -> list[ProspectiveRecord]:
    """Freeze rows joined with their ScoreEvent (in-memory view only)."""
    scores = {s.freeze_record_hash: s for s in load_scores(prospective_dir)}
    views: list[ProspectiveRecord] = []
    for freeze in load_freezes(prospective_dir):
        score = scores.get(freeze.record_hash)
        views.append(with_score(freeze, score) if score else freeze)
    return views
