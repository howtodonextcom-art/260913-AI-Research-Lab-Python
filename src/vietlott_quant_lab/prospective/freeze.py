"""Freeze a ranking commitment for a FUTURE draw (no peeking)."""

from __future__ import annotations

import json
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from vietlott_quant_lab.config.constants import POOL_SIZES
from vietlott_quant_lab.data.manifest import compute_dataset_sha256
from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.features.windows import MULTI_SCALE_WINDOWS
from vietlott_quant_lab.prospective.chain import (
    append_freeze,
    compute_record_hash,
    load_freezes,
    sha256_hex,
    tip_hash,
)
from vietlott_quant_lab.prospective.types import ProspectiveRecord
from vietlott_quant_lab.ranking.engine import ROUND1_MODELS, rank_all
from vietlott_quant_lab.ranking.models.hot import DEFAULT_LOOKBACK
from vietlott_quant_lab.ranking.types import RankingResult

FEATURE_HASH_VERSION = "features.v1"
DEFAULT_PROTOCOL: dict[str, Any] = {
    "name": "round1_prospective",
    "split": "chronological_50_25_25",
    "primary_endpoint": "mean_k",
    "models": list(ROUND1_MODELS),
    "pool_sizes": list(POOL_SIZES),
}


class ProspectiveFreezeError(ValueError):
    """Raised when a freeze request is invalid (e.g. peeking at a known draw)."""


def next_draw_id(history: Sequence[DrawRecord]) -> str:
    if not history:
        raise ProspectiveFreezeError("cannot freeze without history to rank from")
    last = max(history, key=lambda d: d.draw_id)
    nxt = int(last.draw_id) + 1
    if nxt > 99999:
        raise ProspectiveFreezeError(f"draw id overflow after {last.draw_id}")
    return f"{nxt:05d}"


def _stable_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_model_hash(
    model_id: str,
    *,
    lookback: int,
    seed: int,
) -> str:
    return sha256_hex(
        _stable_json({"model_id": model_id, "lookback": lookback, "seed": seed})
    )


def compute_feature_hash(*, windows: Sequence[Any] = MULTI_SCALE_WINDOWS) -> str:
    payload = {
        "version": FEATURE_HASH_VERSION,
        "windows": ["ALL" if w == "ALL" else int(w) for w in windows],
    }
    return sha256_hex(_stable_json(payload))


def compute_protocol_hash(protocol: dict[str, Any] | None = None) -> str:
    body = protocol if protocol is not None else DEFAULT_PROTOCOL
    return sha256_hex(_stable_json(body))


def _pools_from_ranking(ranking: RankingResult) -> dict[str, tuple[int, ...]]:
    by_rank = ranking.by_rank()
    out: dict[str, tuple[int, ...]] = {
        "ranking_01_45": tuple(r.number for r in by_rank),
    }
    for m in POOL_SIZES:
        out[f"top{m}"] = tuple(r.number for r in by_rank[:m])
    return out


def freeze_ranking(
    history: Sequence[DrawRecord],
    *,
    prospective_dir: Path,
    model_id: str,
    target_draw_id: str | None = None,
    lookback: int = DEFAULT_LOOKBACK,
    seed: int = 0,
    dataset_hash: str | None = None,
    protocol_hash: str | None = None,
    feature_hash: str | None = None,
    model_hash: str | None = None,
    frozen_at: datetime | None = None,
    protocol: dict[str, Any] | None = None,
) -> ProspectiveRecord:
    """Freeze full ranking 01–45 + nested top18…top7 for a future draw.

    Refuses if ``target_draw_id`` already exists in ``history`` (peeking).
    Writes an immutable append-only freeze row under ``artifacts/prospective/``.
    """
    known_ids = {d.draw_id for d in history}
    target = target_draw_id or next_draw_id(history)
    if target in known_ids:
        raise ProspectiveFreezeError(
            f"refuse freeze for known draw {target} (peeking / draw already in dataset)"
        )

    ranking = rank_all(history, model_id, seed=seed, lookback=lookback)
    pools = _pools_from_ranking(ranking)
    existing = load_freezes(prospective_dir)
    prev = tip_hash(existing)
    ts = frozen_at or datetime.now(UTC)

    draft = ProspectiveRecord(
        target_draw_id=target,
        ranking_01_45=pools["ranking_01_45"],
        top18=pools["top18"],
        top17=pools["top17"],
        top16=pools["top16"],
        top15=pools["top15"],
        top14=pools["top14"],
        top13=pools["top13"],
        top12=pools["top12"],
        top11=pools["top11"],
        top10=pools["top10"],
        top9=pools["top9"],
        top8=pools["top8"],
        top7=pools["top7"],
        model_id=model_id,
        model_hash=model_hash or compute_model_hash(model_id, lookback=lookback, seed=seed),
        feature_hash=feature_hash or compute_feature_hash(),
        dataset_hash=dataset_hash or compute_dataset_sha256(list(history)),
        protocol_hash=protocol_hash or compute_protocol_hash(protocol),
        frozen_at=ts,
        record_hash="pending",
        previous_hash=prev,
    )
    record_hash = compute_record_hash(draft.freeze_payload_for_hash())
    record = draft.model_copy(update={"record_hash": record_hash})
    return append_freeze(prospective_dir, record)
