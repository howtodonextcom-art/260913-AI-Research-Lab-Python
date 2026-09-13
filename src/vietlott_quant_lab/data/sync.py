"""Incremental merge of official draws into canonical storage (fail-closed)."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from vietlott_quant_lab.config.settings import Settings, get_settings
from vietlott_quant_lab.data.client import VietlottOfficialClient
from vietlott_quant_lab.data.errors import MergeConflictError, ValidationError
from vietlott_quant_lab.data.integrity import check_integrity
from vietlott_quant_lab.data.manifest import (
    build_manifest,
    default_manifest_path,
    manifest_as_json,
    write_manifest,
)
from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.data.snapshots import write_raw_snapshot
from vietlott_quant_lab.data.storage import (
    SyncStateStore,
    default_canonical_path,
    default_sync_db_path,
    load_canonical_parquet,
    write_canonical_parquet,
)
from vietlott_quant_lab.observability.logging import get_logger, log_event

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class MergeResult:
    merged: list[DrawRecord]
    added: int
    conflicts: list[dict[str, object]]


@dataclass(frozen=True, slots=True)
class SyncResult:
    mode: str
    records_fetched: int
    record_count: int
    dataset_sha256: str
    validation_status: str
    canonical_path: Path
    manifest_path: Path


def _identity_tuple(record: DrawRecord) -> tuple[str, tuple[int, ...]]:
    return (record.draw_date.isoformat(), record.numbers)


def merge_draws(
    existing: list[DrawRecord],
    incoming: list[DrawRecord],
    *,
    conflict_dir: Path | None = None,
) -> MergeResult:
    """Merge by draw_id. Same id with different date/numbers → FAIL CLOSED."""
    by_id: dict[str, DrawRecord] = {r.draw_id: r for r in existing}
    conflicts: list[dict[str, object]] = []
    added = 0

    for rec in incoming:
        if rec.draw_id not in by_id:
            by_id[rec.draw_id] = rec
            added += 1
            continue
        old = by_id[rec.draw_id]
        if _identity_tuple(old) != _identity_tuple(rec):
            conflicts.append(
                {
                    "draw_id": rec.draw_id,
                    "old": {
                        "draw_date": old.draw_date.isoformat(),
                        "numbers": list(old.numbers),
                        "source_url": old.source_url,
                        "fetched_at": old.fetched_at.isoformat(),
                    },
                    "new": {
                        "draw_date": rec.draw_date.isoformat(),
                        "numbers": list(rec.numbers),
                        "source_url": rec.source_url,
                        "fetched_at": rec.fetched_at.isoformat(),
                    },
                }
            )

    if conflicts:
        artifact = _write_reconcile_artifact(conflicts, conflict_dir=conflict_dir)
        raise MergeConflictError(
            f"MERGE_CONFLICT: {len(conflicts)} draw_id(s) disagree; "
            f"reconcile artifact at {artifact} — canonical not overwritten"
        )

    merged = sorted(by_id.values(), key=lambda r: r.draw_id)
    return MergeResult(merged=merged, added=added, conflicts=[])


def _write_reconcile_artifact(
    conflicts: list[dict[str, object]],
    *,
    conflict_dir: Path | None,
) -> Path:
    base = conflict_dir or Path("data/snapshots")
    base.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    path = base / f"reconcile_{ts}_{uuid.uuid4().hex[:8]}.json"
    # Never overwrite: if somehow exists, pick another uuid path.
    while path.exists():
        path = base / f"reconcile_{ts}_{uuid.uuid4().hex[:8]}.json"
    payload = {
        "code": "MERGE_CONFLICT",
        "timestamp": datetime.now(UTC).isoformat(),
        "conflicts": conflicts,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    log_event(logger, "merge_conflict_artifact", path=str(path), count=len(conflicts))
    return path


def sync_official(
    *,
    settings: Settings | None = None,
    force_full: bool = False,
    delay_ms: int | None = None,
    client: VietlottOfficialClient | None = None,
    incoming: list[DrawRecord] | None = None,
) -> SyncResult:
    """Crawl (or accept prefetched ``incoming``), merge, validate, write canonical."""
    settings = settings or get_settings()
    delay = settings.http_request_delay_ms if delay_ms is None else delay_ms
    started = datetime.now(UTC)
    run_id = started.strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:8]

    canonical_path = default_canonical_path(settings.processed_dir)
    manifest_path = default_manifest_path(settings.manifests_dir)
    sync_db = default_sync_db_path(settings.manifests_dir)
    conflict_dir = settings.snapshots_dir

    existing = load_canonical_parquet(canonical_path)
    owns_client = client is None and incoming is None
    mode = "full" if force_full or not existing else "incremental"

    try:
        if incoming is None:
            if client is None:
                client = VietlottOfficialClient(page_delay_ms=delay)
            if mode == "full":
                incoming = client.crawl_full()
            else:
                latest_id = max(r.draw_id for r in existing)
                incoming = client.crawl_incremental(latest_id)
            # Snapshot landing marker for audit (lightweight).
            write_raw_snapshot(
                settings.raw_dir,
                source_url=client.history_url(),
                http_status=200,
                content=f"sync:{mode}:fetched={len(incoming)}".encode(),
                label=f"sync_{mode}",
            )
    finally:
        if owns_client and client is not None:
            client.close()

    assert incoming is not None
    merge = merge_draws(existing, incoming, conflict_dir=conflict_dir)

    # Full replace after force: still merge for conflict detection against existing.
    # Integrity: full history must be continuous from #00001 once we claim full.
    require_cont = mode == "full" or (
        bool(existing) and existing[0].draw_id == "00001"
    )
    # Prefer continuity whenever the merged set starts at 00001.
    if merge.merged and merge.merged[0].draw_id == "00001":
        require_cont = True

    report = check_integrity(merge.merged, require_continuity_from_first=require_cont)
    if not report.ok:
        raise ValidationError(
            "integrity FAIL CLOSED: " + "; ".join(report.issues)
        )

    write_canonical_parquet(canonical_path, merge.merged)
    manifest = build_manifest(merge.merged, validation_status="PASS")
    write_manifest(manifest_path, manifest)

    with SyncStateStore(sync_db) as store:
        if merge.merged:
            store.upsert_cursor(
                latest_draw_id=merge.merged[-1].draw_id,
                latest_draw_date=merge.merged[-1].draw_date.isoformat(),
                dataset_sha256=manifest.dataset_sha256,
                last_sync_at=manifest.last_sync,
            )
        store.save_manifest_json(manifest_as_json(manifest))
        store.record_run(
            run_id=run_id,
            started_at=started.isoformat(),
            finished_at=datetime.now(UTC).isoformat(),
            mode=mode,
            records_fetched=len(incoming),
            status="ok",
            message=f"added={merge.added}",
        )

    log_event(
        logger,
        "sync_complete",
        mode=mode,
        fetched=len(incoming),
        total=len(merge.merged),
        sha256=manifest.dataset_sha256,
    )
    return SyncResult(
        mode=mode,
        records_fetched=len(incoming),
        record_count=len(merge.merged),
        dataset_sha256=manifest.dataset_sha256,
        validation_status="PASS",
        canonical_path=canonical_path,
        manifest_path=manifest_path,
    )
