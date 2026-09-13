"""Algorithm V2 research protocol and complexity registry.

Changing any methodological field changes ``protocol_hash``. Round-1 models
remain baselines; V2 challengers are registered separately.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from vietlott_quant_lab.config.constants import LOOKBACK_WINDOWS
from vietlott_quant_lab.provenance.hashing import sha256_canonical
from vietlott_quant_lab.ranking.engine import (
    MODEL_ALL_HISTORY,
    MODEL_EWF,
    MODEL_HAZARD,
    MODEL_HOT,
    MODEL_MEAN_REVERSION,
    MODEL_MOMENTUM,
    MODEL_MULTI_SCALE_SHRINKAGE,
    MODEL_MULTI_SCALE_V2,
    MODEL_RANDOM,
)
from vietlott_quant_lab.ranking.models.ewf import EWF_HALF_LIVES
from vietlott_quant_lab.research.protocol import (
    DEFAULT_ALPHA,
    DEFAULT_MIN_HISTORY,
    DEFAULT_POOL_SIZE,
    DEFAULT_PRACTICAL_DELTA_MEAN_K,
    ResearchProtocol,
)

# Lower complexity wins ties (simpler model preferred).
MODEL_COMPLEXITY_V2: dict[str, int] = {
    MODEL_RANDOM: 0,
    MODEL_ALL_HISTORY: 1,
    MODEL_HOT: 2,
    MODEL_EWF: 3,
    MODEL_HAZARD: 3,
    MODEL_MOMENTUM: 4,
    MODEL_MEAN_REVERSION: 4,
    MODEL_MULTI_SCALE_SHRINKAGE: 5,
    MODEL_MULTI_SCALE_V2: 6,
}

V2_TOURNAMENT_MODELS: tuple[str, ...] = (
    MODEL_RANDOM,
    MODEL_ALL_HISTORY,
    MODEL_HOT,
    MODEL_EWF,
    MODEL_MULTI_SCALE_SHRINKAGE,
    MODEL_MULTI_SCALE_V2,
    MODEL_MOMENTUM,
    MODEL_MEAN_REVERSION,
    MODEL_HAZARD,
)


class ResearchProtocolV2(BaseModel):
    """Registered Algorithm V2 protocol (hash changes when methodology changes)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = "algorithm_v2_classical_v1"
    parent_round1_name: str = "round1_default_v1"
    split_rule: Literal["chronological_50_25_25"] = "chronological_50_25_25"
    development_fraction: float = Field(default=0.50, ge=0.0, le=1.0)
    validation_fraction: float = Field(default=0.25, ge=0.0, le=1.0)
    test_fraction: float = Field(default=0.25, ge=0.0, le=1.0)
    alpha: float = Field(default=DEFAULT_ALPHA, gt=0.0, lt=1.0)
    multiplicity_method: Literal["holm_bonferroni"] = "holm_bonferroni"
    primary_endpoint: Literal["mean_k"] = "mean_k"
    primary_inference: Literal["newey_west_hac"] = "newey_west_hac"
    secondary_endpoints: tuple[str, ...] = (
        "p_ge_4",
        "p_ge_5",
        "p_eq_6",
        "mean_winner_rank",
        "median_winner_rank",
        "mean_mcp",
        "p_mcp_le_pool",
    )
    pool_size: int = Field(default=DEFAULT_POOL_SIZE, ge=6, le=45)
    lookback_windows: tuple[int | Literal["ALL"], ...] = LOOKBACK_WINDOWS
    ewf_half_lives: tuple[int, ...] = EWF_HALF_LIVES
    models: tuple[str, ...] = V2_TOURNAMENT_MODELS
    seed: int = 0
    min_history: int = Field(default=DEFAULT_MIN_HISTORY, ge=1)
    practical_delta_mean_k: float = Field(default=DEFAULT_PRACTICAL_DELTA_MEAN_K, ge=0.0)
    default_hot_lookback: int | Literal["ALL"] = 90
    default_ewf_half_life: int = 90
    ml_enabled: bool = False
    ml_prune_reason: str = (
        "Classical V2 Validation must show practical edge before ML challengers; "
        "otherwise PRUNE ML."
    )

    def canonical_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")

    def protocol_hash(self) -> str:
        return sha256_canonical(self.canonical_dict())

    def as_round1_compatible(self) -> ResearchProtocol:
        """Project shared split/endpoint fields onto Round-1 ResearchProtocol."""
        return ResearchProtocol(
            name=self.name,
            split_rule=self.split_rule,
            development_fraction=self.development_fraction,
            validation_fraction=self.validation_fraction,
            test_fraction=self.test_fraction,
            alpha=self.alpha,
            multiplicity_method=self.multiplicity_method,
            primary_endpoint=self.primary_endpoint,
            pool_size=self.pool_size,
            lookback_windows=self.lookback_windows,
            models=(MODEL_HOT, MODEL_MULTI_SCALE_SHRINKAGE, MODEL_RANDOM),
            seed=self.seed,
            min_history=self.min_history,
            practical_delta_mean_k=self.practical_delta_mean_k,
            default_hot_lookback=self.default_hot_lookback,
        )


def default_protocol_v2(**overrides: Any) -> ResearchProtocolV2:
    return ResearchProtocolV2(**overrides)
