"""CLI: score pending prospective freezes against newly synced draws.

Usage (from repo root, after ``pip install -e ".[dev]"``)::

    python -m scripts.score_prospective
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
    from vietlott_quant_lab.data.storage import default_canonical_path, load_canonical_parquet
    from vietlott_quant_lab.observability.logging import get_logger, log_event
    from vietlott_quant_lab.prospective.chain import ChainIntegrityError, verify_chain
    from vietlott_quant_lab.prospective.score import pending_freezes, score_pending

    parser = argparse.ArgumentParser(
        description="Score pending prospective freezes once actual draws are in canonical data."
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
    draws = load_canonical_parquet(canonical)
    if not draws:
        logger.error("no canonical draws at %s — run sync_official first", canonical)
        return 1

    try:
        verify_chain(prospective_dir)
    except ChainIntegrityError as exc:
        logger.error("prospective chain integrity failed: %s", exc)
        return 1

    awaiting = pending_freezes(prospective_dir)
    log_event(
        logger,
        "score_cli_start",
        pending=len(awaiting),
        draws=len(draws),
        prospective_dir=str(prospective_dir),
    )

    events = score_pending(draws, prospective_dir=prospective_dir)
    verify_chain(prospective_dir)

    if not events:
        print(f"score ok scored=0 pending={len(awaiting)} (no newly available targets)")
        return 0

    for ev in events:
        print(
            f"scored target={ev.target_draw_id} mcp={ev.mcp} k18={ev.k18} "
            f"freeze={ev.freeze_record_hash} score_hash={ev.record_hash}"
        )
    print(f"score ok scored={len(events)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
