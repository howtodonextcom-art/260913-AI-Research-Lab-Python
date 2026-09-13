"""Immutable raw HTTP snapshots under data/raw/ (never overwrite)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from vietlott_quant_lab.config.constants import PARSER_VERSION
from vietlott_quant_lab.observability.logging import get_logger, log_event

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class SnapshotMeta:
    source_url: str
    fetched_at: str
    http_status: int
    content_hash: str
    parser_version: str
    byte_length: int
    path: str


def content_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def write_raw_snapshot(
    raw_dir: Path,
    *,
    source_url: str,
    http_status: int,
    content: bytes,
    label: str = "page",
    parser_version: str = PARSER_VERSION,
) -> SnapshotMeta:
    """Write content-addressed + timestamped snapshot; never overwrite existing file."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    digest = content_sha256(content)
    fetched_at = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    safe_label = "".join(c if c.isalnum() or c in "-_" else "_" for c in label)[:64]
    stem = f"{fetched_at}_{safe_label}_{digest[:16]}"
    body_path = raw_dir / f"{stem}.bin"
    meta_path = raw_dir / f"{stem}.meta.json"

    if body_path.exists() or meta_path.exists():
        # Content-addressed collision with same timestamp is astronomically rare;
        # still refuse overwrite and pick a unique suffix.
        suffix = 1
        while body_path.exists() or meta_path.exists():
            stem = f"{fetched_at}_{safe_label}_{digest[:16]}_{suffix}"
            body_path = raw_dir / f"{stem}.bin"
            meta_path = raw_dir / f"{stem}.meta.json"
            suffix += 1

    body_path.write_bytes(content)
    meta = SnapshotMeta(
        source_url=source_url,
        fetched_at=datetime.now(UTC).isoformat(),
        http_status=http_status,
        content_hash=digest,
        parser_version=parser_version,
        byte_length=len(content),
        path=str(body_path.as_posix()),
    )
    meta_path.write_text(
        json.dumps(asdict(meta), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    log_event(logger, "raw_snapshot_written", path=str(body_path), hash=digest)
    return meta
