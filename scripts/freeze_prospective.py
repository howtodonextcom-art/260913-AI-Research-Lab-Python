"""CLI: freeze next-draw ranking into the prospective hash chain.

Usage (from repo root, after ``pip install -e ".[dev]"``)::

    python -m scripts.freeze_prospective
    python -m scripts.freeze_prospective --model hot --lookback 90 --seed 0
    python -m scripts.freeze_prospective --target-draw 01234
"""

from __future__ import annotations

import argparse
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
    from vietlott_quant_lab.observability.logging import get_logger, log_event
    from vietlott_quant_lab.prospective.chain import verify_chain
    from vietlott_quant_lab.prospective.freeze import ProspectiveFreezeError, freeze_ranking
    from vietlott_quant_lab.ranking.engine import ROUND1_MODELS

    parser = argparse.ArgumentParser(
        description="Freeze ranking 01–45 for the next (future) Mega 6/45 draw."
    )
    parser.add_argument(
        "--model",
        default="hot",
        choices=list(ROUND1_MODELS),
        help="Ranking model id (default: hot).",
    )
    parser.add_argument(
        "--lookback",
        type=int,
        default=90,
        help="HOT lookback window in draws (default: 90).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="Model seed (default: 0).",
    )
    parser.add_argument(
        "--target-draw",
        default=None,
        metavar="ID",
        help="Future 5-digit draw id (default: last_known + 1).",
    )
    parser.add_argument(
        "--prospective-dir",
        type=Path,
        default=None,
        help="Override artifacts/prospective directory.",
    )
    args = parser.parse_args(argv)

    settings = get_settings()
    logger = get_logger(__name__, level=settings.log_level)
    prospective_dir = args.prospective_dir or settings.prospective_dir
    canonical = default_canonical_path(settings.processed_dir)
    history = load_canonical_parquet(canonical)
    if not history:
        logger.error("no canonical draws at %s — run sync_official first", canonical)
        return 1

    dataset_hash = compute_dataset_sha256(history)
    log_event(
        logger,
        "freeze_cli_start",
        model=args.model,
        lookback=args.lookback,
        seed=args.seed,
        target=args.target_draw,
        dataset_hash=dataset_hash,
    )

    try:
        record = freeze_ranking(
            history,
            prospective_dir=prospective_dir,
            model_id=args.model,
            target_draw_id=args.target_draw,
            lookback=args.lookback,
            seed=args.seed,
            dataset_hash=dataset_hash,
        )
        verify_chain(prospective_dir)
    except ProspectiveFreezeError as exc:
        logger.error("freeze refused: %s", exc)
        return 1
    except Exception as exc:  # noqa: BLE001 — CLI boundary
        logger.error("freeze failed: %s", exc)
        return 1

    print(
        f"freeze ok target={record.target_draw_id} model={record.model_id} "
        f"record_hash={record.record_hash} previous_hash={record.previous_hash} "
        f"dataset_hash={record.dataset_hash}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
