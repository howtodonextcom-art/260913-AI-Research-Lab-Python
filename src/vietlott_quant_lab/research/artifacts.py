"""Write JSON experiment artifacts under artifacts/experiments/."""

from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from vietlott_quant_lab.config.settings import Settings, get_settings
from vietlott_quant_lab.provenance.hashing import sha256_canonical, short_hash


def best_effort_git_commit(*, cwd: Path | None = None) -> str | None:
    """Return current HEAD SHA, or None if git is unavailable."""
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0:
        return None
    sha = completed.stdout.strip()
    return sha or None


def build_experiment_id(
    *,
    dataset_hash: str,
    protocol_hash: str,
    model_hash: str,
) -> str:
    """Identity from dataset + protocol + model hashes (not timestamp-only)."""
    return (
        f"{short_hash(dataset_hash)}_"
        f"{short_hash(protocol_hash)}_"
        f"{short_hash(model_hash)}"
    )


def write_experiment_artifact(
    *,
    dataset_hash: str,
    protocol_hash: str,
    model: str,
    model_hash: str,
    features: dict[str, Any] | list[Any] | str | None = None,
    windows: Any = None,
    hyperparameters: dict[str, Any] | None = None,
    development_results: dict[str, Any] | None = None,
    validation_results: dict[str, Any] | None = None,
    test_results: dict[str, Any] | None = None,
    scientific_verdict: str | None = None,
    extra: dict[str, Any] | None = None,
    settings: Settings | None = None,
    experiments_dir: Path | None = None,
    git_commit: str | None = None,
) -> Path:
    """Write a JSON experiment artifact; return the file path."""
    cfg = settings or get_settings()
    out_dir = experiments_dir or cfg.experiments_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    experiment_id = build_experiment_id(
        dataset_hash=dataset_hash,
        protocol_hash=protocol_hash,
        model_hash=model_hash,
    )
    payload: dict[str, Any] = {
        "experiment_id": experiment_id,
        "protocol_hash": protocol_hash,
        "dataset_hash": dataset_hash,
        "model": model,
        "model_hash": model_hash,
        "features": features,
        "windows": windows,
        "hyperparameters": hyperparameters or {},
        "development_results": development_results or {},
        "validation_results": validation_results or {},
        "test_results": test_results or {},
        "scientific_verdict": scientific_verdict,
        "generated_at": datetime.now(UTC).isoformat(),
        "git_commit": git_commit if git_commit is not None else best_effort_git_commit(
            cwd=cfg.project_root
        ),
        "artifact_sha256": "",  # filled after body without this field
    }
    if extra:
        payload.update(extra)

    body_for_hash = {k: v for k, v in payload.items() if k != "artifact_sha256"}
    payload["artifact_sha256"] = sha256_canonical(body_for_hash)

    path = out_dir / f"{experiment_id}.json"
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path
