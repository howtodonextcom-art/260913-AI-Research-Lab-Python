"""Tournaments, gates, and experiment orchestration (P6–P9)."""

from vietlott_quant_lab.research.artifacts import (
    build_experiment_id,
    write_experiment_artifact,
)
from vietlott_quant_lab.research.compression import (
    CompressionFrontier,
    compression_frontier,
)
from vietlott_quant_lab.research.model_tournament import (
    ModelTournamentResult,
    run_model_tournament,
)
from vietlott_quant_lab.research.pool_gate import PoolGateResult, evaluate_pool18_gate
from vietlott_quant_lab.research.protocol import (
    HOLDOUT_SIGNAL_NOT_CONFIRMED,
    NO_VERIFIED_18_POOL_EDGE,
    SCIENTIFIC_VERDICTS,
    ResearchProtocol,
    default_protocol,
)
from vietlott_quant_lab.research.split import ChronologicalSplit, chronological_split
from vietlott_quant_lab.research.verdict import compute_scientific_verdict
from vietlott_quant_lab.research.walkforward import WalkForwardResult, walkforward_score
from vietlott_quant_lab.research.window_tournament import (
    WindowTournamentResult,
    run_window_tournament,
)

__all__ = [
    "HOLDOUT_SIGNAL_NOT_CONFIRMED",
    "NO_VERIFIED_18_POOL_EDGE",
    "SCIENTIFIC_VERDICTS",
    "ChronologicalSplit",
    "CompressionFrontier",
    "ModelTournamentResult",
    "PoolGateResult",
    "ResearchProtocol",
    "WalkForwardResult",
    "WindowTournamentResult",
    "build_experiment_id",
    "chronological_split",
    "compression_frontier",
    "compute_scientific_verdict",
    "default_protocol",
    "evaluate_pool18_gate",
    "run_model_tournament",
    "run_window_tournament",
    "walkforward_score",
    "write_experiment_artifact",
]
