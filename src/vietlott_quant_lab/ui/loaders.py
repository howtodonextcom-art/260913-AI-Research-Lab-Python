"""Load local manifests, draws, experiment artifacts, and prospective chain.

UI never crawls Vietlott — only reads local services / artifacts.
Missing paths return empty/None with explicit health flags (never silent wrong claims).
"""

from __future__ import annotations

import contextlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from vietlott_quant_lab.config.constants import (
    DETAIL_PATH_TEMPLATE,
    MANIFEST_FILENAME,
    OFFICIAL_BASE_URL,
    PARSER_VERSION,
)
from vietlott_quant_lab.config.settings import Settings, get_settings
from vietlott_quant_lab.data.integrity import IntegrityReport, check_integrity
from vietlott_quant_lab.data.manifest import DatasetManifest, load_manifest
from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.data.storage import (
    SyncStateStore,
    default_canonical_path,
    default_sync_db_path,
    load_canonical_parquet,
)
from vietlott_quant_lab.prospective.chain import (
    ChainIntegrityError,
    load_freezes,
    load_scores,
    verify_chain,
)
from vietlott_quant_lab.prospective.score import pending_freezes, scored_views
from vietlott_quant_lab.prospective.types import ProspectiveRecord, ScoreEvent
from vietlott_quant_lab.ui.labels import (
    CHAIN_FAIL,
    CHAIN_OK,
    MISSING_PROSPECTIVE,
    STATUS_LOCAL_ONLY,
    STATUS_UNKNOWN,
)


@dataclass(frozen=True)
class DatasetBundle:
    draws: list[DrawRecord]
    manifest: DatasetManifest | None
    dataset_hash: str
    parquet_path: Path
    manifest_path: Path


@dataclass(frozen=True)
class ArtifactSummary:
    path: Path
    experiment_id: str
    model: str | None
    dataset_hash: str | None
    protocol_hash: str | None
    scientific_verdict: str | None
    generated_at: str | None
    kind: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProspectiveBundle:
    freezes: list[ProspectiveRecord]
    scores: list[ScoreEvent]
    chain_ok: bool
    chain_error: str | None


@dataclass(frozen=True)
class SystemHealth:
    source_status: str
    parser_status: str
    integrity_ok: bool | None
    integrity_issues: tuple[str, ...]
    freshness: str
    duckdb_ok: bool
    duckdb_path: str
    artifact_count: int
    prospective_chain_ok: bool | None
    prospective_message: str
    app_version: str
    dataset_hash: str | None
    record_count: int
    last_sync: str | None
    validation_status: str | None


def _settings(settings: Settings | None = None) -> Settings:
    return settings or get_settings()


def _manifest_path(settings: Settings) -> Path:
    return settings.manifests_dir / MANIFEST_FILENAME


def load_dataset_bundle(settings: Settings | None = None) -> DatasetBundle:
    cfg = _settings(settings)
    parquet_path = default_canonical_path(cfg.processed_dir)
    manifest_path = _manifest_path(cfg)
    draws = load_canonical_parquet(parquet_path) if parquet_path.exists() else []
    manifest = load_manifest(manifest_path)
    dataset_hash = manifest.dataset_sha256 if manifest else ""
    return DatasetBundle(
        draws=draws,
        manifest=manifest,
        dataset_hash=dataset_hash,
        parquet_path=parquet_path,
        manifest_path=manifest_path,
    )


def load_dataset_manifest(settings: Settings | None = None) -> DatasetManifest | None:
    return load_dataset_bundle(settings).manifest


def load_draws(settings: Settings | None = None) -> list[DrawRecord]:
    return load_dataset_bundle(settings).draws


def official_detail_url(draw_id: str) -> str:
    return OFFICIAL_BASE_URL + DETAIL_PATH_TEMPLATE.format(draw_id=draw_id)


def integrity_for_draws(draws: list[DrawRecord]) -> IntegrityReport:
    return check_integrity(draws, require_continuity_from_first=True)


def list_experiment_artifact_paths(settings: Settings | None = None) -> list[Path]:
    cfg = _settings(settings)
    if not cfg.experiments_dir.exists():
        return []
    return sorted(
        cfg.experiments_dir.glob("*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )


def list_experiment_artifacts(settings: Settings | None = None) -> list[ArtifactSummary]:
    """Return parsed experiment artifacts (empty list if none)."""
    out: list[ArtifactSummary] = []
    for path in list_experiment_artifact_paths(settings):
        payload = load_json_artifact(path)
        if not payload:
            continue
        kind = str(
            payload.get("kind")
            or payload.get("artifact_kind")
            or (
                "model_tournament"
                if "champion" in payload or "scores" in payload
                else "experiment"
            )
        )
        out.append(
            ArtifactSummary(
                path=path,
                experiment_id=str(payload.get("experiment_id") or path.stem),
                model=payload.get("model") if isinstance(payload.get("model"), str) else None,
                dataset_hash=(
                    payload.get("dataset_hash")
                    if isinstance(payload.get("dataset_hash"), str)
                    else None
                ),
                protocol_hash=(
                    payload.get("protocol_hash")
                    if isinstance(payload.get("protocol_hash"), str)
                    else None
                ),
                scientific_verdict=(
                    payload.get("scientific_verdict")
                    if isinstance(payload.get("scientific_verdict"), str)
                    else None
                ),
                generated_at=(
                    payload.get("generated_at")
                    if isinstance(payload.get("generated_at"), str)
                    else None
                ),
                kind=kind,
                payload=payload,
            )
        )
    return out


def load_json_artifact(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def latest_tournament_artifact(settings: Settings | None = None) -> dict[str, Any] | None:
    for summary in list_experiment_artifacts(settings):
        payload = summary.payload
        if (
            payload.get("model")
            or payload.get("scientific_verdict")
            or "validation_results" in payload
            or "champion" in payload
            or "scores" in payload
        ):
            return payload
    return None


def find_compression_artifact(settings: Settings | None = None) -> dict[str, Any] | None:
    for summary in list_experiment_artifacts(settings):
        payload = summary.payload
        if "compression" in summary.kind.lower() or "frontier" in summary.kind.lower():
            return payload
        if "rows" in payload:
            return payload
        extra = payload.get("extra")
        if isinstance(extra, dict) and "rows" in extra:
            return payload
    return None


def load_prospective_bundle(settings: Settings | None = None) -> ProspectiveBundle:
    """Always fresh — do not wrap in long-lived Streamlit cache."""
    cfg = _settings(settings)
    freezes: list[ProspectiveRecord] = []
    scores: list[ScoreEvent] = []
    try:
        freezes = load_freezes(cfg.prospective_dir)
        scores = load_scores(cfg.prospective_dir)
        if not freezes and not scores:
            return ProspectiveBundle(freezes=[], scores=[], chain_ok=True, chain_error=None)
        verify_chain(cfg.prospective_dir)
        return ProspectiveBundle(freezes=freezes, scores=scores, chain_ok=True, chain_error=None)
    except ChainIntegrityError as exc:
        return ProspectiveBundle(
            freezes=freezes,
            scores=scores,
            chain_ok=False,
            chain_error=str(exc),
        )
    except Exception as exc:  # noqa: BLE001 — UI health surface
        return ProspectiveBundle(
            freezes=freezes,
            scores=scores,
            chain_ok=False,
            chain_error=str(exc),
        )


def prospective_pending_scored(
    bundle: ProspectiveBundle,
) -> tuple[list[ProspectiveRecord], list[ProspectiveRecord]]:
    scored_hashes = {s.freeze_record_hash for s in bundle.scores}
    pending = [f for f in bundle.freezes if f.record_hash not in scored_hashes]
    try:
        scored = [v for v in scored_views(_settings().prospective_dir) if v.scored_at is not None]
    except Exception:  # noqa: BLE001
        scored = [f for f in bundle.freezes if f.record_hash in scored_hashes]
    if bundle.chain_ok:
        with contextlib.suppress(Exception):
            pending = pending_freezes(_settings().prospective_dir)
    return pending, scored


def duckdb_health(settings: Settings | None = None) -> dict[str, Any]:
    cfg = _settings(settings)
    db_path = default_sync_db_path(cfg.manifests_dir)
    if not db_path.exists():
        return {"status": "MISSING", "path": str(db_path)}
    try:
        with SyncStateStore(db_path) as store:
            latest = store.get_latest_draw_id()
        return {"status": "OK", "path": str(db_path), "latest_draw_id": latest}
    except Exception as exc:  # noqa: BLE001
        return {"status": "FAIL", "path": str(db_path), "error": str(exc)}


def freshness_label(manifest: DatasetManifest | None) -> str:
    if manifest is None or not manifest.last_sync:
        return STATUS_UNKNOWN
    try:
        ts = datetime.fromisoformat(manifest.last_sync.replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=UTC)
        age_h = (datetime.now(UTC) - ts.astimezone(UTC)).total_seconds() / 3600.0
        if age_h < 24:
            return f"FRESH ({age_h:.1f}h)"
        if age_h < 24 * 7:
            return f"STALE ({age_h / 24:.1f}d)"
        return f"OLD ({age_h / 24:.1f}d)"
    except ValueError:
        return STATUS_UNKNOWN


def build_system_health(
    *,
    settings: Settings | None = None,
    app_version: str,
) -> SystemHealth:
    cfg = _settings(settings)
    bundle = load_dataset_bundle(cfg)
    manifest = bundle.manifest
    integrity: IntegrityReport | None = None
    if bundle.draws:
        integrity = integrity_for_draws(bundle.draws)
    artifacts = list_experiment_artifacts(cfg)
    prosp = load_prospective_bundle(cfg)
    duck = duckdb_health(cfg)

    if prosp.freezes or prosp.scores:
        chain_ok: bool | None = prosp.chain_ok
        chain_msg = CHAIN_OK if prosp.chain_ok else (prosp.chain_error or CHAIN_FAIL)
    else:
        chain_ok = None
        chain_msg = MISSING_PROSPECTIVE

    return SystemHealth(
        source_status=STATUS_LOCAL_ONLY,
        parser_status=manifest.parser_version if manifest else PARSER_VERSION,
        integrity_ok=None if integrity is None else integrity.ok,
        integrity_issues=tuple(integrity.issues) if integrity else (),
        freshness=freshness_label(manifest),
        duckdb_ok=duck.get("status") == "OK",
        duckdb_path=str(duck.get("path") or ""),
        artifact_count=len(artifacts),
        prospective_chain_ok=chain_ok,
        prospective_message=chain_msg,
        app_version=app_version,
        dataset_hash=bundle.dataset_hash or None,
        record_count=manifest.record_count if manifest else len(bundle.draws),
        last_sync=manifest.last_sync if manifest else None,
        validation_status=manifest.validation_status if manifest else None,
    )
