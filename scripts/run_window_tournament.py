"""CLI: lookback-window tournament (Development → Validation; never Test).

Usage (from repo root)::

    python -m scripts.run_window_tournament
    python -m scripts.run_window_tournament --min-history 40
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _ensure_src_on_path() -> None:
    root = Path(__file__).resolve().parents[1]
    src = root / "src"
    if src.is_dir() and str(src) not in sys.path:
        sys.path.insert(0, str(src))


def main(argv: list[str] | None = None) -> int:
    _ensure_src_on_path()
    from vietlott_quant_lab.config.settings import get_settings
    from vietlott_quant_lab.data.manifest import compute_dataset_sha256
    from vietlott_quant_lab.data.storage import default_canonical_path, load_canonical_parquet
    from vietlott_quant_lab.provenance.hashing import sha256_canonical
    from vietlott_quant_lab.research.artifacts import write_experiment_artifact
    from vietlott_quant_lab.research.protocol import default_protocol
    from vietlott_quant_lab.research.window_tournament import run_window_tournament

    parser = argparse.ArgumentParser(
        description="Run lookback-window tournament (HOT) on chronological Dev/Val."
    )
    parser.add_argument(
        "--parquet",
        type=Path,
        default=None,
        help="Canonical draws parquet (default: data/processed/draws_mega645.parquet).",
    )
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--min-history", type=int, default=30)
    parser.add_argument(
        "--top-candidates",
        type=int,
        default=3,
        help="How many Development windows promote to Validation.",
    )
    args = parser.parse_args(argv)

    settings = get_settings()
    path = args.parquet or default_canonical_path(settings.processed_dir)
    draws = load_canonical_parquet(path)
    if not draws:
        print(
            f"ERROR: empty dataset at {path}. "
            "Run `python -m scripts.sync_official` first, or pass --parquet.",
            file=sys.stderr,
        )
        return 1

    protocol = default_protocol(
        seed=args.seed,
        min_history=args.min_history,
        top_window_candidates=args.top_candidates,
    )
    result = run_window_tournament(draws, protocol=protocol)
    summary = result.summary()
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    dataset_hash = compute_dataset_sha256(draws)
    model_hash = sha256_canonical(
        {
            "kind": "window_tournament",
            "selected_lookback": result.selected_lookback,
            "seed": args.seed,
        }
    )
    artifact_path = write_experiment_artifact(
        dataset_hash=dataset_hash,
        protocol_hash=result.protocol_hash,
        model="hot_window_tournament",
        model_hash=model_hash,
        windows=list(protocol.lookback_windows),
        hyperparameters={
            "seed": args.seed,
            "min_history": args.min_history,
            "top_window_candidates": args.top_candidates,
        },
        development_results={"ranked": summary["development"]},
        validation_results={"scores": summary["validation"]},
        test_results={"note": "Test never used for window selection"},
        scientific_verdict=None,
        settings=settings,
        extra={"selected_lookback": result.selected_lookback, "frozen": result.frozen},
    )
    print(f"artifact written: {artifact_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
