"""Immutable research and product constants."""

from __future__ import annotations

from pathlib import Path
from typing import Final, Literal

PRODUCT_MEGA645: Final[Literal["mega645"]] = "mega645"

# Mandatory multi-scale lookback windows (draw counts). "ALL" = full history.
LOOKBACK_WINDOWS: Final[tuple[int | Literal["ALL"], ...]] = (
    15,
    30,
    45,
    60,
    90,
    120,
    180,
    270,
    365,
    500,
    750,
    1000,
    "ALL",
)

# Nested candidate pool sizes (top-m of a frozen ranking).
POOL_SIZES: Final[tuple[int, ...]] = tuple(range(7, 19))  # 7 .. 18 inclusive

NUMBER_MIN: Final[int] = 1
NUMBER_MAX: Final[int] = 45
DRAW_SIZE: Final[int] = 6

# --- Official Vietlott Mega 6/45 source ---
OFFICIAL_BASE_URL: Final[str] = "https://vietlott.vn"
OFFICIAL_ALLOWED_HOST: Final[str] = "vietlott.vn"
HISTORY_PATH: Final[str] = "/vi/trung-thuong/ket-qua-trung-thuong/winning-number-645"
DETAIL_PATH_TEMPLATE: Final[str] = (
    "/vi/trung-thuong/ket-qua-trung-thuong/645?id={draw_id}&nocatche=1"
)
AJAX_COMPARE_PATH: Final[str] = (
    "/ajaxpro/Vietlott.PlugIn.WebParts.Game645CompareWebPart,Vietlott.PlugIn.WebParts.ashx"
)
FIRST_DRAW_ID: Final[str] = "00001"
HISTORY_PAGE_SIZE: Final[int] = 8
DEFAULT_MAX_HISTORY_PAGES: Final[int] = 800
HTTP_USER_AGENT: Final[str] = "vietlott-quant-lab/0.1 (+research)"
HTTP_MAX_RESPONSE_BYTES: Final[int] = 5 * 1024 * 1024
PARSER_VERSION: Final[str] = "1.0.0"
OFFICIAL_SOURCE_ID: Final[str] = "vietlott-official"
CANONICAL_DRAWS_FILENAME: Final[str] = "draws_mega645.parquet"
SYNC_STATE_DB_FILENAME: Final[str] = "sync_state.duckdb"
MANIFEST_FILENAME: Final[str] = "manifest_mega645.json"

# Repo-relative paths (resolved against Settings.project_root at runtime).
DATA_DIR_NAME: Final[str] = "data"
RAW_DIR_NAME: Final[str] = "raw"
PROCESSED_DIR_NAME: Final[str] = "processed"
SNAPSHOTS_DIR_NAME: Final[str] = "snapshots"
MANIFESTS_DIR_NAME: Final[str] = "manifests"
ARTIFACTS_DIR_NAME: Final[str] = "artifacts"
EXPERIMENTS_DIR_NAME: Final[str] = "experiments"
PROSPECTIVE_DIR_NAME: Final[str] = "prospective"
REPORTS_DIR_NAME: Final[str] = "reports"


def default_project_root() -> Path:
    """Resolve workspace root for editable/src trees and installed packages.

    Under ``src/vietlott_quant_lab/config/``, parents[3] is the repo root.
    After ``pip install`` (Docker), that walk lands under site-packages — fall
    back to the process CWD when it looks like the app workspace (``app.py``).
    """
    candidate = Path(__file__).resolve().parents[3]
    if (candidate / "app.py").is_file():
        return candidate
    cwd = Path.cwd()
    if (cwd / "app.py").is_file():
        return cwd
    return candidate
