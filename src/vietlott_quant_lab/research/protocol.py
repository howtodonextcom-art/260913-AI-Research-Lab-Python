"""Hashable research protocol and scientific verdict tokens."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from vietlott_quant_lab.config.constants import LOOKBACK_WINDOWS
from vietlott_quant_lab.provenance.hashing import sha256_canonical
from vietlott_quant_lab.ranking.engine import (
    MODEL_HOT,
    MODEL_MULTI_SCALE_SHRINKAGE,
    MODEL_RANDOM,
)

ScientificVerdict = Literal[
    "NO_RANKING_EDGE_FOUND",
    "EXPLORATORY_SIGNAL",
    "VALIDATION_SIGNAL",
    "HOLDOUT_SIGNAL",
    "PROSPECTIVE_SIGNAL",
]

SCIENTIFIC_VERDICTS: tuple[ScientificVerdict, ...] = (
    "NO_RANKING_EDGE_FOUND",
    "EXPLORATORY_SIGNAL",
    "VALIDATION_SIGNAL",
    "HOLDOUT_SIGNAL",
    "PROSPECTIVE_SIGNAL",
)

# Extended outcome tokens (gate / holdout confirmation) — not scientific status ladder.
HOLDOUT_SIGNAL_NOT_CONFIRMED = "HOLDOUT_SIGNAL_NOT_CONFIRMED"
NO_VERIFIED_18_POOL_EDGE = "NO_VERIFIED_18_POOL_EDGE"

DEFAULT_ALPHA = 0.05
DEFAULT_POOL_SIZE = 18
DEFAULT_TOP_WINDOW_CANDIDATES = 3
DEFAULT_PRACTICAL_DELTA_MEAN_K = 0.05
DEFAULT_MIN_HISTORY = 30

# Lower complexity wins ties (simpler model preferred).
MODEL_COMPLEXITY: dict[str, int] = {
    MODEL_RANDOM: 0,
    MODEL_HOT: 1,
    MODEL_MULTI_SCALE_SHRINKAGE: 2,
}


class ResearchProtocol(BaseModel):
    """Registered, hashable research protocol.

    Changing any methodological field changes ``protocol_hash``.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = "round1_default_v1"
    split_rule: Literal["chronological_50_25_25"] = "chronological_50_25_25"
    development_fraction: float = Field(default=0.50, ge=0.0, le=1.0)
    validation_fraction: float = Field(default=0.25, ge=0.0, le=1.0)
    test_fraction: float = Field(default=0.25, ge=0.0, le=1.0)
    alpha: float = Field(default=DEFAULT_ALPHA, gt=0.0, lt=1.0)
    multiplicity_method: Literal["holm_bonferroni"] = "holm_bonferroni"
    primary_endpoint: Literal["mean_k"] = "mean_k"
    pool_size: int = Field(default=DEFAULT_POOL_SIZE, ge=6, le=45)
    lookback_windows: tuple[int | Literal["ALL"], ...] = LOOKBACK_WINDOWS
    models: tuple[str, ...] = (
        MODEL_HOT,
        MODEL_MULTI_SCALE_SHRINKAGE,
        MODEL_RANDOM,
    )
    seed: int = 0
    min_history: int = Field(default=DEFAULT_MIN_HISTORY, ge=1)
    top_window_candidates: int = Field(default=DEFAULT_TOP_WINDOW_CANDIDATES, ge=1)
    practical_delta_mean_k: float = Field(default=DEFAULT_PRACTICAL_DELTA_MEAN_K, ge=0.0)
    default_hot_lookback: int | Literal["ALL"] = 90

    def canonical_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")

    def protocol_hash(self) -> str:
        """SHA-256 of canonical JSON for this protocol."""
        return sha256_canonical(self.canonical_dict())


def default_protocol(**overrides: Any) -> ResearchProtocol:
    return ResearchProtocol(**overrides)
