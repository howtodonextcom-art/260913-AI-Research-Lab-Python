"""Append-only prospective JSONL ledgers with hash-chain integrity."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from vietlott_quant_lab.prospective.types import (
    FREEZES_FILENAME,
    GENESIS_HASH,
    SCORES_FILENAME,
    ProspectiveRecord,
    ScoreEvent,
)


class ChainIntegrityError(ValueError):
    """Raised when a prospective hash chain fails verification."""


def canonical_json(payload: dict[str, Any]) -> str:
    """Deterministic JSON encoding for hashing."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(payload: str | bytes) -> str:
    raw = payload if isinstance(payload, bytes) else payload.encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def compute_record_hash(payload: dict[str, Any]) -> str:
    return sha256_hex(canonical_json(payload))


def freezes_path(prospective_dir: Path) -> Path:
    return prospective_dir / FREEZES_FILENAME


def scores_path(prospective_dir: Path) -> Path:
    return prospective_dir / SCORES_FILENAME


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line)


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        text = line.strip()
        if not text:
            continue
        try:
            rows.append(json.loads(text))
        except json.JSONDecodeError as exc:
            raise ChainIntegrityError(f"invalid JSON at {path}:{line_no}: {exc}") from exc
    return rows


def load_freezes(prospective_dir: Path) -> list[ProspectiveRecord]:
    return [
        ProspectiveRecord.model_validate(row) for row in _load_jsonl(freezes_path(prospective_dir))
    ]


def load_scores(prospective_dir: Path) -> list[ScoreEvent]:
    return [ScoreEvent.model_validate(row) for row in _load_jsonl(scores_path(prospective_dir))]


def tip_hash(records: list[Any], *, hash_attr: str = "record_hash") -> str:
    if not records:
        return GENESIS_HASH
    return str(getattr(records[-1], hash_attr))


def append_freeze(prospective_dir: Path, record: ProspectiveRecord) -> ProspectiveRecord:
    """Append an immutable freeze row. Does not rewrite prior lines."""
    existing = load_freezes(prospective_dir)
    expected_prev = tip_hash(existing)
    if record.previous_hash != expected_prev:
        raise ChainIntegrityError(
            f"freeze previous_hash mismatch: got {record.previous_hash}, "
            f"expected tip {expected_prev}"
        )
    recomputed = compute_record_hash(record.freeze_payload_for_hash())
    if record.record_hash != recomputed:
        raise ChainIntegrityError(
            f"freeze record_hash mismatch: got {record.record_hash}, expected {recomputed}"
        )
    for prior in existing:
        if prior.target_draw_id == record.target_draw_id and prior.model_id == record.model_id:
            raise ChainIntegrityError(
                f"freeze already exists for draw {record.target_draw_id} model {record.model_id}"
            )
        if prior.record_hash == record.record_hash:
            raise ChainIntegrityError("duplicate freeze record_hash")
    _append_jsonl(freezes_path(prospective_dir), record.model_dump(mode="json"))
    return record


def append_score(prospective_dir: Path, event: ScoreEvent) -> ScoreEvent:
    """Append a score event referencing a freeze. Never mutates freeze rows."""
    freezes = {f.record_hash: f for f in load_freezes(prospective_dir)}
    if event.freeze_record_hash not in freezes:
        raise ChainIntegrityError(
            f"score references unknown freeze_record_hash={event.freeze_record_hash}"
        )
    freeze = freezes[event.freeze_record_hash]
    if freeze.target_draw_id != event.target_draw_id:
        raise ChainIntegrityError("score target_draw_id does not match referenced freeze")

    existing = load_scores(prospective_dir)
    expected_prev = tip_hash(existing)
    if event.previous_hash != expected_prev:
        raise ChainIntegrityError(
            f"score previous_hash mismatch: got {event.previous_hash}, "
            f"expected tip {expected_prev}"
        )
    recomputed = compute_record_hash(event.score_payload_for_hash())
    if event.record_hash != recomputed:
        raise ChainIntegrityError(
            f"score record_hash mismatch: got {event.record_hash}, expected {recomputed}"
        )
    for prior in existing:
        if prior.freeze_record_hash == event.freeze_record_hash:
            raise ChainIntegrityError(
                f"freeze {event.freeze_record_hash} already scored "
                f"(score_hash={prior.record_hash})"
            )
    _append_jsonl(scores_path(prospective_dir), event.model_dump(mode="json"))
    return event


def verify_freeze_chain(prospective_dir: Path) -> None:
    """Fail if freeze history was tampered (hash / linkage / payload)."""
    path = freezes_path(prospective_dir)
    rows = _load_jsonl(path)
    prev = GENESIS_HASH
    seen_hashes: set[str] = set()
    for idx, row in enumerate(rows):
        record = ProspectiveRecord.model_validate(row)
        if record.previous_hash != prev:
            raise ChainIntegrityError(
                f"freeze chain broken at index {idx}: previous_hash={record.previous_hash} "
                f"expected={prev}"
            )
        expected = compute_record_hash(record.freeze_payload_for_hash())
        if record.record_hash != expected:
            raise ChainIntegrityError(
                f"freeze chain broken at index {idx}: record_hash mismatch "
                f"(stored={record.record_hash}, recomputed={expected})"
            )
        if record.record_hash in seen_hashes:
            raise ChainIntegrityError(f"duplicate freeze record_hash at index {idx}")
        seen_hashes.add(record.record_hash)
        prev = record.record_hash


def verify_score_chain(prospective_dir: Path) -> None:
    """Fail if score history was tampered."""
    freezes = {f.record_hash for f in load_freezes(prospective_dir)}
    rows = _load_jsonl(scores_path(prospective_dir))
    prev = GENESIS_HASH
    seen_freezes: set[str] = set()
    for idx, row in enumerate(rows):
        event = ScoreEvent.model_validate(row)
        if event.previous_hash != prev:
            raise ChainIntegrityError(
                f"score chain broken at index {idx}: previous_hash={event.previous_hash} "
                f"expected={prev}"
            )
        expected = compute_record_hash(event.score_payload_for_hash())
        if event.record_hash != expected:
            raise ChainIntegrityError(
                f"score chain broken at index {idx}: record_hash mismatch "
                f"(stored={event.record_hash}, recomputed={expected})"
            )
        if event.freeze_record_hash not in freezes:
            raise ChainIntegrityError(
                f"score chain broken at index {idx}: unknown freeze_record_hash"
            )
        if event.freeze_record_hash in seen_freezes:
            raise ChainIntegrityError(
                f"score chain broken at index {idx}: duplicate score for freeze"
            )
        seen_freezes.add(event.freeze_record_hash)
        prev = event.record_hash


def verify_chain(prospective_dir: Path) -> None:
    """Verify freeze and score ledgers (tamper → fail)."""
    verify_freeze_chain(prospective_dir)
    verify_score_chain(prospective_dir)
