"""CLI: Algorithm V2 classical tournament + ablation + compression + ML gate.

Usage (from repo root)::

    python -m scripts.run_algorithm_v2
    python -m scripts.run_algorithm_v2 --hot-lookback 90
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
    from vietlott_quant_lab.research.ablation import (
        fragility_label,
        run_ablation_v2,
        run_fragility_battery,
    )
    from vietlott_quant_lab.research.artifacts import write_experiment_artifact
    from vietlott_quant_lab.research.compression import compression_frontier
    from vietlott_quant_lab.research.model_tournament_v2 import run_model_tournament_v2
    from vietlott_quant_lab.research.protocol_v2 import default_protocol_v2

    parser = argparse.ArgumentParser(description="Run Algorithm V2 classical research.")
    parser.add_argument("--parquet", type=Path, default=None)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--min-history", type=int, default=30)
    parser.add_argument("--hot-lookback", type=_parse_lookback, default=90)
    parser.add_argument("--skip-ablation", action="store_true")
    parser.add_argument("--skip-compression", action="store_true")
    args = parser.parse_args(argv)

    settings = get_settings()
    path = args.parquet or default_canonical_path(settings.processed_dir)
    draws = load_canonical_parquet(path)
    if not draws:
        print(f"ERROR: empty dataset at {path}", file=sys.stderr)
        return 1

    hot_lb = args.hot_lookback
    if isinstance(hot_lb, str) and hot_lb != "ALL":
        hot_lb = int(hot_lb)

    protocol = default_protocol_v2(seed=args.seed, min_history=args.min_history)
    tournament = run_model_tournament_v2(
        draws,
        protocol=protocol,
        hot_lookback=hot_lb,  # type: ignore[arg-type]
    )

    ablation_rows = None
    fragility = None
    fragile_label = None
    if not args.skip_ablation:
        ablation_rows = [r.summary() for r in run_ablation_v2(draws, protocol=protocol)]
        champ = tournament.champion
        if champ is not None:
            lb = champ.lookback if isinstance(champ.lookback, int) else None
            frag = run_fragility_battery(
                draws,
                model_id=champ.model_id,
                lookback=lb if lb is not None else 90,
                protocol=protocol,
            )
            fragility = [f.summary() for f in frag]
            fragile_label = fragility_label(frag)

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

    summary = {
        "tournament": tournament.summary(),
        "ablation": ablation_rows,
        "fragility": fragility,
        "fragility_label": fragile_label,
        "compression": compression_summary,
        "ml_status": tournament.ml_status,
        "ml_prune_reason": protocol.ml_prune_reason
        if tournament.ml_status == "PRUNE_ML"
        else None,
    }
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
        windows={
            "hot_lookback": tournament.hot_lookback,
            "ewf_half_life": tournament.ewf_half_life,
        },
        hyperparameters={"seed": args.seed, "min_history": args.min_history, "family": "v2"},
        development_results={
            "scores": [
                {"model_id": s.model_id, "mean_k": s.development.mean_k}
                for s in tournament.scores
            ]
        },
        validation_results={
            "scores": [
                {
                    "model_id": s.model_id,
                    "mean_k": s.validation.mean_k,
                    "adjusted_p": s.adjusted_p_val,
                }
                for s in tournament.scores
            ]
        },
        test_results=None if tournament.test is None else tournament.test.summary(),
        scientific_verdict=tournament.scientific_verdict,
        settings=settings,
        extra={
            "holdout_status": tournament.holdout_status,
            "ml_status": tournament.ml_status,
            "ablation": ablation_rows,
            "fragility_label": fragile_label,
            "compression": compression_summary,
            "family_definition": tournament.family_definition,
        },
    )
    print(f"artifact written: {artifact_path}", file=sys.stderr)
    # Also write a stable path for reports to cite.
    out = Path("artifacts/experiments/algorithm_v2_latest.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"summary written: {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
