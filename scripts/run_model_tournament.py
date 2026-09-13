"""CLI: Round-1 model tournament (HOT vs Multi-Scale Shrinkage vs Random).

Usage (from repo root)::

    python -m scripts.run_model_tournament
    python -m scripts.run_model_tournament --hot-lookback 90 --no-window-selection
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


def _parse_lookback(raw: str) -> int | str:
    if raw.upper() == "ALL":
        return "ALL"
    return int(raw)


def main(argv: list[str] | None = None) -> int:
    _ensure_src_on_path()
    from vietlott_quant_lab.config.settings import get_settings
    from vietlott_quant_lab.data.manifest import compute_dataset_sha256
    from vietlott_quant_lab.data.storage import default_canonical_path, load_canonical_parquet
    from vietlott_quant_lab.research.artifacts import write_experiment_artifact
    from vietlott_quant_lab.research.compression import compression_frontier
    from vietlott_quant_lab.research.model_tournament import run_model_tournament
    from vietlott_quant_lab.research.pool_gate import evaluate_pool18_gate
    from vietlott_quant_lab.research.protocol import default_protocol
    from vietlott_quant_lab.research.verdict import compute_scientific_verdict, verdict_report

    parser = argparse.ArgumentParser(
        description="Run Round-1 model tournament; freeze champion; confirm on Test."
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
        "--hot-lookback",
        type=_parse_lookback,
        default=None,
        help="HOT lookback (int or ALL). Default: run window tournament first.",
    )
    parser.add_argument(
        "--no-window-selection",
        action="store_true",
        help="Skip window tournament; use protocol default HOT lookback (90).",
    )
    parser.add_argument(
        "--skip-compression",
        action="store_true",
        help="Do not compute compression frontier after the tournament.",
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

    protocol = default_protocol(seed=args.seed, min_history=args.min_history)
    tournament = run_model_tournament(
        draws,
        protocol=protocol,
        hot_lookback=args.hot_lookback,
        run_window_selection=not args.no_window_selection and args.hot_lookback is None,
    )
    gate = evaluate_pool18_gate(draws, tournament=tournament, protocol=protocol)
    scientific = compute_scientific_verdict(model_tournament=tournament, pool_gate=gate)

    summary = {
        "tournament": tournament.summary(),
        "pool_gate": gate.summary(),
        "verdict": verdict_report(
            scientific=scientific,
            pool_gate=gate,
            model_tournament=tournament,
        ),
    }

    compression_summary = None
    if not args.skip_compression and tournament.champion is not None:
        frontier = compression_frontier(
            draws,
            model_id=tournament.champion.model_id,
            lookback=tournament.champion.lookback,
            seed=args.seed,
            min_history=args.min_history,
            practical_delta_mean_k=protocol.practical_delta_mean_k,
        )
        compression_summary = frontier.summary()
        summary["compression"] = compression_summary

    print(json.dumps(summary, ensure_ascii=False, indent=2))

    dataset_hash = compute_dataset_sha256(draws)
    model_hash = (
        tournament.champion.model_config_hash
        if tournament.champion is not None
        else "no_champion"
    )
    artifact_path = write_experiment_artifact(
        dataset_hash=dataset_hash,
        protocol_hash=tournament.protocol_hash,
        model=tournament.champion.model_id if tournament.champion else "none",
        model_hash=model_hash,
        windows={"hot_lookback": tournament.hot_lookback},
        hyperparameters={"seed": args.seed, "min_history": args.min_history},
        development_results={
            "scores": [
                {
                    "model_id": s.model_id,
                    "mean_k": s.development.mean_k,
                }
                for s in tournament.scores
            ]
        },
        validation_results={
            "scores": [
                {
                    "model_id": s.model_id,
                    "mean_k": s.validation.mean_k,
                }
                for s in tournament.scores
            ]
        },
        test_results=None if tournament.test is None else tournament.test.summary(),
        scientific_verdict=scientific,
        settings=settings,
        extra={
            "holdout_status": tournament.holdout_status,
            "pool_gate": gate.summary(),
            "compression": compression_summary,
        },
    )
    print(f"artifact written: {artifact_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
