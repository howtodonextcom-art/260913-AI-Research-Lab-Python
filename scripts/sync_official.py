"""CLI: sync official Vietlott Mega 6/45 history into canonical storage.

Usage (from repo root, after ``pip install -e ".[dev]"``)::

    python -m scripts.sync_official
    python -m scripts.sync_official --force
    python -m scripts.sync_official --delay 500
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
    from vietlott_quant_lab.data.errors import DataLayerError
    from vietlott_quant_lab.data.sync import sync_official
    from vietlott_quant_lab.observability.logging import get_logger, log_event

    parser = argparse.ArgumentParser(
        description="Sync official Mega 6/45 draws from vietlott.vn into Parquet/DuckDB."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force a full crawl back to draw #00001 (ignore incremental cursor).",
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=None,
        metavar="MS",
        help="Inter-page delay in milliseconds (default: settings.http_request_delay_ms).",
    )
    args = parser.parse_args(argv)

    settings = get_settings()
    logger = get_logger(__name__, level=settings.log_level)
    log_event(logger, "sync_cli_start", force=args.force, delay=args.delay)

    try:
        result = sync_official(
            settings=settings,
            force_full=args.force,
            delay_ms=args.delay,
        )
    except DataLayerError as exc:
        logger.error("sync failed: %s", exc)
        return 1

    print(
        f"sync ok mode={result.mode} fetched={result.records_fetched} "
        f"total={result.record_count} sha256={result.dataset_sha256} "
        f"canonical={result.canonical_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
