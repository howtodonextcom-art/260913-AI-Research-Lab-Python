"""Prospective freeze and score event types (append-only ledger)."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from vietlott_quant_lab.config.constants import (
    DRAW_SIZE,
    NUMBER_MAX,
    NUMBER_MIN,
    POOL_SIZES,
)

_DRAW_ID_RE = re.compile(r"^\d{5}$")
GENESIS_HASH: str = "0" * 64
FREEZES_FILENAME: str = "freezes.jsonl"
SCORES_FILENAME: str = "scores.jsonl"


def _validate_draw_id(value: str) -> str:
    if not _DRAW_ID_RE.fullmatch(value):
        raise ValueError(f"draw_id must be exactly 5 digits, got {value!r}")
    return value


def _validate_pool(value: tuple[int, ...], *, size: int) -> tuple[int, ...]:
    if len(value) != size:
        raise ValueError(f"expected {size} numbers, got {len(value)}")
    if len(set(value)) != size:
        raise ValueError("pool numbers must be unique")
    for n in value:
        if n < NUMBER_MIN or n > NUMBER_MAX:
            raise ValueError(f"number out of range: {n}")
    return value


class ProspectiveRecord(BaseModel):
    """Immutable freeze commitment for a future draw.

    Scored fields stay null on freeze; filled only via join with ScoreEvent
    (never by rewriting the freeze JSONL line).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    target_draw_id: str
    ranking_01_45: tuple[int, ...]
    top18: tuple[int, ...]
    top17: tuple[int, ...]
    top16: tuple[int, ...]
    top15: tuple[int, ...]
    top14: tuple[int, ...]
    top13: tuple[int, ...]
    top12: tuple[int, ...]
    top11: tuple[int, ...]
    top10: tuple[int, ...]
    top9: tuple[int, ...]
    top8: tuple[int, ...]
    top7: tuple[int, ...]
    model_id: str
    model_hash: str
    feature_hash: str
    dataset_hash: str
    protocol_hash: str
    frozen_at: datetime
    record_hash: str
    previous_hash: str
    # Nullable scored fields (populated only when joining ScoreEvent views).
    actual_numbers: tuple[int, ...] | None = None
    k18: int | None = None
    k17: int | None = None
    k16: int | None = None
    k15: int | None = None
    k14: int | None = None
    k13: int | None = None
    k12: int | None = None
    k11: int | None = None
    k10: int | None = None
    k9: int | None = None
    k8: int | None = None
    k7: int | None = None
    mcp: int | None = None
    winner_ranks: tuple[int, ...] | None = None
    scored_at: datetime | None = None
    score_record_hash: str | None = None

    @field_validator("target_draw_id")
    @classmethod
    def _v_draw_id(cls, value: str) -> str:
        return _validate_draw_id(value)

    @field_validator("ranking_01_45")
    @classmethod
    def _v_ranking(cls, value: tuple[int, ...]) -> tuple[int, ...]:
        if len(value) != NUMBER_MAX:
            raise ValueError(f"ranking must have {NUMBER_MAX} entries")
        if sorted(value) != list(range(NUMBER_MIN, NUMBER_MAX + 1)):
            raise ValueError("ranking_01_45 must be a permutation of 1..45")
        return value

    @field_validator(
        "top18",
        "top17",
        "top16",
        "top15",
        "top14",
        "top13",
        "top12",
        "top11",
        "top10",
        "top9",
        "top8",
        "top7",
    )
    @classmethod
    def _v_top_pool(cls, value: tuple[int, ...], info: Any) -> tuple[int, ...]:
        size = int(str(info.field_name).removeprefix("top"))
        return _validate_pool(value, size=size)

    @model_validator(mode="after")
    def _nested_pools(self) -> ProspectiveRecord:
        pools = {
            m: frozenset(getattr(self, f"top{m}")) for m in POOL_SIZES
        }
        ranking_prefix = {
            m: frozenset(self.ranking_01_45[:m]) for m in POOL_SIZES
        }
        for m in POOL_SIZES:
            if pools[m] != ranking_prefix[m]:
                raise ValueError(f"top{m} must equal first {m} of ranking_01_45")
        ordered = sorted(POOL_SIZES)
        for i in range(1, len(ordered)):
            if not pools[ordered[i - 1]] <= pools[ordered[i]]:
                raise ValueError(
                    f"nested invariant broken: top{ordered[i - 1]} ⊄ top{ordered[i]}"
                )
        return self

    def freeze_payload_for_hash(self) -> dict[str, Any]:
        """Canonical freeze fields used for record_hash (excludes scored + record_hash)."""
        data = self.model_dump(mode="json")
        for key in (
            "record_hash",
            "actual_numbers",
            "k18",
            "k17",
            "k16",
            "k15",
            "k14",
            "k13",
            "k12",
            "k11",
            "k10",
            "k9",
            "k8",
            "k7",
            "mcp",
            "winner_ranks",
            "scored_at",
            "score_record_hash",
        ):
            data.pop(key, None)
        return data

    def pool(self, m: int) -> tuple[int, ...]:
        if m not in POOL_SIZES:
            raise ValueError(f"unsupported pool size: {m}")
        return tuple(getattr(self, f"top{m}"))


class ScoreEvent(BaseModel):
    """Append-only score against a frozen ProspectiveRecord (never mutates freeze)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    freeze_record_hash: str
    target_draw_id: str
    actual_numbers: tuple[int, ...]
    k18: int
    k17: int
    k16: int
    k15: int
    k14: int
    k13: int
    k12: int
    k11: int
    k10: int
    k9: int
    k8: int
    k7: int
    mcp: int
    winner_ranks: tuple[int, ...]
    scored_at: datetime
    record_hash: str
    previous_hash: str

    @field_validator("target_draw_id")
    @classmethod
    def _v_draw_id(cls, value: str) -> str:
        return _validate_draw_id(value)

    @field_validator("actual_numbers")
    @classmethod
    def _v_numbers(cls, value: tuple[int, ...]) -> tuple[int, ...]:
        if len(value) != DRAW_SIZE:
            raise ValueError(f"expected {DRAW_SIZE} numbers")
        if len(set(value)) != DRAW_SIZE:
            raise ValueError("actual_numbers must be unique")
        for n in value:
            if n < NUMBER_MIN or n > NUMBER_MAX:
                raise ValueError(f"number out of range: {n}")
        return tuple(sorted(value))

    @field_validator("winner_ranks")
    @classmethod
    def _v_ranks(cls, value: tuple[int, ...]) -> tuple[int, ...]:
        if len(value) != DRAW_SIZE:
            raise ValueError(f"expected {DRAW_SIZE} winner ranks")
        for r in value:
            if r < 1 or r > NUMBER_MAX:
                raise ValueError(f"rank out of range: {r}")
        return value

    @field_validator(
        "k18",
        "k17",
        "k16",
        "k15",
        "k14",
        "k13",
        "k12",
        "k11",
        "k10",
        "k9",
        "k8",
        "k7",
        "mcp",
    )
    @classmethod
    def _v_nonneg(cls, value: int) -> int:
        if value < 0:
            raise ValueError("metric must be non-negative")
        return value

    def score_payload_for_hash(self) -> dict[str, Any]:
        data = self.model_dump(mode="json")
        data.pop("record_hash", None)
        return data

    def k_for(self, m: int) -> int:
        if m not in POOL_SIZES:
            raise ValueError(f"unsupported pool size: {m}")
        return int(getattr(self, f"k{m}"))


def with_score(freeze: ProspectiveRecord, score: ScoreEvent) -> ProspectiveRecord:
    """Return a view of freeze with scored fields filled (does not rewrite ledger)."""
    if score.freeze_record_hash != freeze.record_hash:
        raise ValueError("score.freeze_record_hash does not match freeze.record_hash")
    if score.target_draw_id != freeze.target_draw_id:
        raise ValueError("score.target_draw_id does not match freeze.target_draw_id")
    return freeze.model_copy(
        update={
            "actual_numbers": score.actual_numbers,
            "k18": score.k18,
            "k17": score.k17,
            "k16": score.k16,
            "k15": score.k15,
            "k14": score.k14,
            "k13": score.k13,
            "k12": score.k12,
            "k11": score.k11,
            "k10": score.k10,
            "k9": score.k9,
            "k8": score.k8,
            "k7": score.k7,
            "mcp": score.mcp,
            "winner_ranks": score.winner_ranks,
            "scored_at": score.scored_at,
            "score_record_hash": score.record_hash,
        }
    )
