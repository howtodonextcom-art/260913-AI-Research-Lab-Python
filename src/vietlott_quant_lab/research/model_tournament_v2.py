"""Algorithm V2 model tournament — classical challengers only.

Selection on Validation only; Test confirms once. Simpler model wins ties.
Multiplicity: Holm–Bonferroni over the registered V2 model family (Validation
one-sided HAC p-values). Do not tune on Test. ML is gated separately.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal

from vietlott_quant_lab.data.schema import DrawRecord
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
from vietlott_quant_lab.research.protocol import HOLDOUT_SIGNAL_NOT_CONFIRMED
from vietlott_quant_lab.research.protocol_v2 import (
    MODEL_COMPLEXITY_V2,
    ResearchProtocolV2,
    default_protocol_v2,
)
from vietlott_quant_lab.research.split import ChronologicalSplit, chronological_split
from vietlott_quant_lab.research.walkforward import WalkForwardResult, walkforward_on_segment
from vietlott_quant_lab.statistics.multiplicity import holm_bonferroni

WindowSpec = int | Literal["ALL"]


@dataclass(frozen=True)
class ModelScoreV2:
    model_id: str
    lookback: WindowSpec | None
    half_life: int | None
    development: WalkForwardResult
    validation: WalkForwardResult
    complexity: int
    raw_p_val: float
    adjusted_p_val: float


@dataclass(frozen=True)
class FrozenChampionV2:
    model_id: str
    lookback: WindowSpec | None
    half_life: int | None
    model_config_hash: str
    protocol_hash: str


@dataclass(frozen=True)
class ModelTournamentV2Result:
    protocol_hash: str
    hot_lookback: WindowSpec
    ewf_half_life: int
    scores: tuple[ModelScoreV2, ...]
    champion: FrozenChampionV2 | None
    frozen: bool
    test: WalkForwardResult | None
    holdout_status: str
    scientific_verdict: str
    ml_status: str
    family_definition: str

    def summary(self) -> dict[str, Any]:
        return {
            "protocol_hash": self.protocol_hash,
            "hot_lookback": self.hot_lookback,
            "ewf_half_life": self.ewf_half_life,
            "family_definition": self.family_definition,
            "scores": [
                {
                    "model_id": s.model_id,
                    "lookback": s.lookback,
                    "half_life": s.half_life,
                    "complexity": s.complexity,
                    "raw_p_val": s.raw_p_val,
                    "adjusted_p_val": s.adjusted_p_val,
                    "development": s.development.summary(),
                    "validation": s.validation.summary(),
                }
                for s in self.scores
            ],
            "champion": None
            if self.champion is None
            else {
                "model_id": self.champion.model_id,
                "lookback": self.champion.lookback,
                "half_life": self.champion.half_life,
                "model_config_hash": self.champion.model_config_hash,
                "protocol_hash": self.champion.protocol_hash,
            },
            "frozen": self.frozen,
            "test": None if self.test is None else self.test.summary(),
            "holdout_status": self.holdout_status,
            "scientific_verdict": self.scientific_verdict,
            "ml_status": self.ml_status,
        }


def _model_config_hash(
    model_id: str,
    lookback: WindowSpec | None,
    half_life: int | None,
    seed: int,
) -> str:
    return sha256_canonical(
        {
            "model_id": model_id,
            "lookback": lookback,
            "half_life": half_life,
            "seed": seed,
        }
    )


def _select_ewf_half_life(
    draws: Sequence[DrawRecord],
    split: ChronologicalSplit,
    *,
    protocol: ResearchProtocolV2,
) -> int:
    """Pick EWF half-life on Development Mean K only (never Test)."""
    best_hl = protocol.default_ewf_half_life
    best_mean = float("-inf")
    for hl in protocol.ewf_half_lives or EWF_HALF_LIVES:
        wf = walkforward_on_segment(
            tuple(draws),
            split.development,
            model_id=MODEL_EWF,
            pool_size=protocol.pool_size,
            lookback=hl,
            seed=protocol.seed,
            min_history=protocol.min_history,
            extra_kwargs={"half_life": hl},
        )
        if wf.mean_k > best_mean or (
            abs(wf.mean_k - best_mean) < 1e-12 and hl < best_hl
        ):
            best_mean = wf.mean_k
            best_hl = hl
    return best_hl


def _lookback_for(
    model_id: str,
    *,
    hot_lookback: WindowSpec,
    ewf_half_life: int,
) -> WindowSpec | None:
    if model_id == MODEL_HOT:
        return hot_lookback
    if model_id == MODEL_EWF:
        return ewf_half_life
    if model_id in {
        MODEL_RANDOM,
        MODEL_ALL_HISTORY,
        MODEL_MULTI_SCALE_SHRINKAGE,
        MODEL_MULTI_SCALE_V2,
        MODEL_MOMENTUM,
        MODEL_MEAN_REVERSION,
        MODEL_HAZARD,
    }:
        return None
    return hot_lookback


def _extra_for(model_id: str, *, ewf_half_life: int) -> dict[str, Any] | None:
    if model_id == MODEL_EWF:
        return {"half_life": ewf_half_life}
    return None


def _positive(wf: WalkForwardResult, *, practical_delta: float, alpha: float) -> bool:
    p = wf.one_sided_p_hac if wf.one_sided_p_hac == wf.one_sided_p_hac else wf.one_sided_p_mean_k
    return wf.beats_null and wf.lift_mean_k >= practical_delta and p <= alpha


def _select_champion(scores: Sequence[ModelScoreV2]) -> ModelScoreV2 | None:
    if not scores:
        return None
    return max(
        scores,
        key=lambda s: (
            s.validation.mean_k,
            -s.validation.mean_mcp,
            s.validation.p_ge_4,
            -s.complexity,
            -s.adjusted_p_val,
        ),
    )


def run_model_tournament_v2(
    draws: Sequence[DrawRecord],
    *,
    protocol: ResearchProtocolV2 | None = None,
    split: ChronologicalSplit | None = None,
    hot_lookback: WindowSpec | None = None,
) -> ModelTournamentV2Result:
    """Run classical V2 tournament: Dev explore → Val select → Test confirm."""
    proto = protocol or default_protocol_v2()
    round1 = proto.as_round1_compatible()
    split = split or chronological_split(draws, protocol=round1)
    full = tuple(draws)
    hot_lb: WindowSpec = hot_lookback if hot_lookback is not None else proto.default_hot_lookback
    ewf_hl = _select_ewf_half_life(full, split, protocol=proto)

    family = (
        "V2 classical family: "
        + ", ".join(proto.models)
        + f"; EWF half-lives Dev-selected from {list(proto.ewf_half_lives)}; "
        "Holm–Bonferroni on Validation HAC p-values."
    )

    Raw = tuple[str, WindowSpec | None, int | None, WalkForwardResult, WalkForwardResult, int]
    raw_scores: list[Raw] = []
    for model_id in proto.models:
        lb = _lookback_for(model_id, hot_lookback=hot_lb, ewf_half_life=ewf_hl)
        extra = _extra_for(model_id, ewf_half_life=ewf_hl)
        hl = ewf_hl if model_id == MODEL_EWF else None
        dev = walkforward_on_segment(
            full,
            split.development,
            model_id=model_id,
            pool_size=proto.pool_size,
            lookback=lb,
            seed=proto.seed,
            min_history=proto.min_history,
            extra_kwargs=extra,
        )
        val = walkforward_on_segment(
            full,
            split.validation,
            model_id=model_id,
            pool_size=proto.pool_size,
            lookback=lb,
            seed=proto.seed,
            min_history=proto.min_history,
            extra_kwargs=extra,
        )
        raw_scores.append(
            (
                model_id,
                lb,
                hl,
                dev,
                val,
                MODEL_COMPLEXITY_V2.get(model_id, 99),
            )
        )

    # Multiplicity family = non-random challengers on Validation.
    family_indices = [i for i, s in enumerate(raw_scores) if s[0] != MODEL_RANDOM]
    p_values = [
        raw_scores[i][4].one_sided_p_hac
        if raw_scores[i][4].one_sided_p_hac == raw_scores[i][4].one_sided_p_hac
        else raw_scores[i][4].one_sided_p_mean_k
        for i in family_indices
    ]
    holm = holm_bonferroni(p_values, alpha=proto.alpha) if p_values else []
    adj_map = {family_indices[j]: holm[j].adjusted_p for j in range(len(holm))}

    scores: list[ModelScoreV2] = []
    for i, (model_id, lb, hl, dev, val, complexity) in enumerate(raw_scores):
        raw_p = val.one_sided_p_hac
        scores.append(
            ModelScoreV2(
                model_id=model_id,
                lookback=lb,
                half_life=hl,
                development=dev,
                validation=val,
                complexity=complexity,
                raw_p_val=raw_p,
                adjusted_p_val=adj_map.get(i, raw_p),
            )
        )

    winner = _select_champion(scores)
    protocol_hash = proto.protocol_hash()

    if winner is None:
        return ModelTournamentV2Result(
            protocol_hash=protocol_hash,
            hot_lookback=hot_lb,
            ewf_half_life=ewf_hl,
            scores=tuple(scores),
            champion=None,
            frozen=False,
            test=None,
            holdout_status=HOLDOUT_SIGNAL_NOT_CONFIRMED,
            scientific_verdict="NO_RANKING_EDGE_FOUND",
            ml_status="PRUNE_ML",
            family_definition=family,
        )

    champion = FrozenChampionV2(
        model_id=winner.model_id,
        lookback=winner.lookback,
        half_life=winner.half_life,
        model_config_hash=_model_config_hash(
            winner.model_id, winner.lookback, winner.half_life, proto.seed
        ),
        protocol_hash=protocol_hash,
    )

    extra = _extra_for(champion.model_id, ewf_half_life=ewf_hl)
    test_wf = walkforward_on_segment(
        full,
        split.test,
        model_id=champion.model_id,
        pool_size=proto.pool_size,
        lookback=champion.lookback,
        seed=proto.seed,
        min_history=proto.min_history,
        extra_kwargs=extra,
    )

    val_ok = (
        _positive(
            winner.validation,
            practical_delta=proto.practical_delta_mean_k,
            alpha=proto.alpha,
        )
        and winner.adjusted_p_val <= proto.alpha
    )
    test_ok = _positive(
        test_wf,
        practical_delta=proto.practical_delta_mean_k,
        alpha=proto.alpha,
    )
    random_val = next((s.validation for s in scores if s.model_id == MODEL_RANDOM), None)
    beats_random = (
        random_val is None or winner.validation.mean_k >= random_val.mean_k - 1e-12
    )

    if val_ok and test_ok and beats_random and champion.model_id != MODEL_RANDOM:
        holdout_status = "HOLDOUT_SIGNAL"
        scientific_verdict = "HOLDOUT_SIGNAL"
    elif val_ok and champion.model_id != MODEL_RANDOM:
        holdout_status = HOLDOUT_SIGNAL_NOT_CONFIRMED
        scientific_verdict = "VALIDATION_SIGNAL"
    elif any(
        _positive(s.development, practical_delta=proto.practical_delta_mean_k, alpha=proto.alpha)
        and s.model_id != MODEL_RANDOM
        for s in scores
    ):
        holdout_status = HOLDOUT_SIGNAL_NOT_CONFIRMED
        scientific_verdict = "EXPLORATORY_SIGNAL"
    else:
        holdout_status = "NO_RANKING_EDGE_FOUND"
        scientific_verdict = "NO_RANKING_EDGE_FOUND"

    ml_status = (
        "ML_ELIGIBLE"
        if val_ok and champion.model_id != MODEL_RANDOM
        else "PRUNE_ML"
    )

    return ModelTournamentV2Result(
        protocol_hash=protocol_hash,
        hot_lookback=hot_lb,
        ewf_half_life=ewf_hl,
        scores=tuple(scores),
        champion=champion,
        frozen=True,
        test=test_wf,
        holdout_status=holdout_status,
        scientific_verdict=scientific_verdict,
        ml_status=ml_status,
        family_definition=family,
    )
