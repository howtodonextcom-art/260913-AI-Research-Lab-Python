"""Vietnamese UI copy; scientific tokens stay English."""

from __future__ import annotations

from typing import Final

# --- Brand / shell ---
APP_TITLE: Final[str] = "Vietlott Quant Research Lab"
APP_SUBTITLE: Final[str] = "Phòng thí nghiệm định lượng Mega 6/45 — không phải công cụ dự đoán."

DISCLAIMER_VI: Final[str] = (
    "Lab này **không** dự đoán kết quả Vietlott. "
    "Các mẫu lịch sử là **giả thuyết** dưới giao thức thống kê. "
    "`NO_RANKING_EDGE_FOUND` là kết quả khoa học hợp lệ. "
    "Score không phải xác suất trừ khi có bằng chứng calibration."
)

DISCLAIMER_EN: Final[str] = (
    "This lab does **not** predict Vietlott results. "
    "Historical patterns are **hypotheses** under statistical protocols. "
    "`NO_RANKING_EDGE_FOUND` is a valid scientific outcome. "
    "Scores are not probabilities unless calibration evidence exists."
)

# --- Page titles ---
PAGE_OVERVIEW: Final[str] = "Tổng quan"
PAGE_DATA_LIBRARY: Final[str] = "Thư viện dữ liệu"
PAGE_NUMBER_LAB: Final[str] = "Number Lab"
PAGE_CANDIDATE_POOL: Final[str] = "Candidate Pool"
PAGE_AB_TOURNAMENT: Final[str] = "A/B Tournament"
PAGE_COMPRESSION: Final[str] = "Compression Frontier"
PAGE_PROSPECTIVE: Final[str] = "Prospective"
PAGE_SYSTEM_HEALTH: Final[str] = "System Health"

# --- Common ---
MISSING_DATASET: Final[str] = (
    "Chưa có dataset canonical. Chạy `python -m scripts.sync_official` rồi mở lại trang."
)
MISSING_ARTIFACT: Final[str] = (
    "Artifact chưa có — chạy `python -m scripts.run_model_tournament` "
    "(hoặc `run_window_tournament` / script research tương ứng)."
)
MISSING_COMPRESSION_ARTIFACT: Final[str] = (
    "Artifact compression chưa có — chạy pipeline compression "
    "(`python -m scripts.run_model_tournament` rồi ghi frontier vào artifacts/experiments)."
)
MISSING_PROSPECTIVE: Final[str] = (
    "Chưa có prospective chain — chạy `python -m scripts.freeze_prospective` "
    "sau khi có ranking đã freeze."
)
READ_ONLY: Final[str] = "Chế độ chỉ đọc (read-only)."
SCORE_NOT_PROBABILITY: Final[str] = (
    "Cột **Score** là tín hiệu xếp hạng (ranking signal), **không** phải probability."
)
NO_NETWORK_RERUN: Final[str] = "UI không gọi mạng mỗi lần rerun — chỉ đọc snapshot/artifact local."

# --- Overview ---
SCIENTIFIC_VERDICT: Final[str] = "Scientific Verdict"
PRODUCTION_VERDICT: Final[str] = "Production Verdict"
DATASET_SECTION: Final[str] = "Dataset"
RESEARCH_SECTION: Final[str] = "Research"
CANDIDATE_POOL_SECTION: Final[str] = "Candidate Pool"
DRAW_COUNT: Final[str] = "Số kỳ"
FIRST_DRAW: Final[str] = "Kỳ đầu"
LATEST_DRAW: Final[str] = "Kỳ mới nhất"
LAST_SYNC: Final[str] = "Last sync"
SOURCE: Final[str] = "Source"
DATASET_HASH: Final[str] = "Dataset hash"
BEST_MODEL: Final[str] = "Best model"
BEST_WINDOW: Final[str] = "Best window"
EVIDENCE_LEVEL: Final[str] = "Evidence level"
BEST_CUTOFF: Final[str] = "Best validated cutoff"
PROTOCOL_HASH: Final[str] = "Protocol hash"

# --- Data library ---
FILTERS: Final[str] = "Bộ lọc"
DRAW_ID: Final[str] = "Draw ID"
DRAW_DATE: Final[str] = "Ngày quay"
NUMBERS: Final[str] = "Bộ số"
OFFICIAL_LINK: Final[str] = "Link chính thức"
INTEGRITY: Final[str] = "Integrity"
SYNC_STATUS: Final[str] = "Sync"
FRESHNESS: Final[str] = "Freshness"
VALIDATION: Final[str] = "Validation"

# --- Number lab ---
PICK_NUMBER: Final[str] = "Chọn số (01–45)"
FEATURES: Final[str] = "Features"
HISTORY: Final[str] = "Lịch sử xuất hiện"
RANKING_TABLE: Final[str] = "Bảng ranking 01–45"
COL_RANK: Final[str] = "Rank"
COL_NUMBER: Final[str] = "Number"
COL_SCORE: Final[str] = "Score"
MODEL_SELECTOR: Final[str] = "Model ranking"

# --- Candidate pool ---
POOL_SIZE: Final[str] = "Pool size (Top-m)"
MEAN_K: Final[str] = "Mean K"
RANDOM_MEAN_K: Final[str] = "Random Mean K (null)"
P4: Final[str] = "P(K≥4)"
P5: Final[str] = "P(K≥5)"
P6: Final[str] = "P6"
MCP: Final[str] = "MCP"
LIFT: Final[str] = "Lift"
EVIDENCE: Final[str] = "Evidence"
TOP_M_NUMBERS: Final[str] = "Top-m numbers"

# --- Tournament ---
TOURNAMENT_WINNER: Final[str] = "Winner (từ engine)"
DEVELOPMENT: Final[str] = "Development"
VALIDATION: Final[str] = "Validation"
TEST: Final[str] = "Test"
HOLDOUT_STATUS: Final[str] = "Holdout status"

# --- Compression ---
CONTAINMENT: Final[str] = "Containment / Mean K"
COST: Final[str] = "Cost (full bao)"
FRONTIER_CHART: Final[str] = "Compression frontier"

# --- Prospective ---
FROZEN: Final[str] = "Frozen"
PENDING: Final[str] = "Pending"
SCORED: Final[str] = "Scored"
HASH_CHAIN: Final[str] = "Hash chain"
CHAIN_OK: Final[str] = "Chain integrity: OK"
CHAIN_FAIL: Final[str] = "Chain integrity: FAIL"

# --- System health ---
SOURCE_REACHABLE: Final[str] = "Source reachable"
PARSER_STATUS: Final[str] = "Parser status"
DATASET_INTEGRITY: Final[str] = "Dataset integrity"
DATASET_FRESHNESS: Final[str] = "Dataset freshness"
DUCKDB_STATUS: Final[str] = "DuckDB"
EXPERIMENT_ARTIFACTS: Final[str] = "Experiment artifacts"
PROSPECTIVE_CHAIN: Final[str] = "Prospective chain"
APP_VERSION: Final[str] = "App version"
HEALTH_UNKNOWN_NETWORK: Final[str] = (
    "Không kiểm tra mạng trên mỗi rerun — trạng thái nguồn từ sync/manifest gần nhất."
)

# Status tokens (English — keep as-is in UI)
STATUS_PASS: Final[str] = "PASS"
STATUS_FAIL: Final[str] = "FAIL"
STATUS_UNKNOWN: Final[str] = "UNKNOWN"
STATUS_MISSING: Final[str] = "MISSING"
STATUS_OK: Final[str] = "OK"
STATUS_LOCAL_ONLY: Final[str] = "LOCAL_ONLY"

DEFAULT_PRODUCTION_VERDICT: Final[str] = "NOT_PRODUCTION_READY"
DEFAULT_SCIENTIFIC_VERDICT: Final[str] = "NO_RANKING_EDGE_FOUND"
