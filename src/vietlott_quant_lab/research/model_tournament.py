"""Round-1 model tournament: HOT vs Multi-Scale Shrinkage vs Random."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal

from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.provenance.hashing import sha256_canonical
from vietlott_quant_lab.ranking.engine import (
    MODEL_HOT,
    MODEL_MULTI_SCALE_SHRINKAGE,
    MODEL_RANDOM,
)
from vietlott_quant_lab.research.protocol import (
    HOLDOUT_SIGNAL_NOT_CONFIRMED,
    MODEL_COMPLEXITY,
    ResearchProtocol,
    default_protocol,
)
from vietlott_quant_lab.research.split import ChronologicalSplit, chronological_split
from vietlott_quant_lab.research.walkforward import WalkForwardResult, walkforward_on_segment
from vietlott_quant_lab.research.window_tournament import run_window_tournament

WindowSpec = int | Literal["ALL"]


@dataclass(frozen=True)
class ModelScore:
    model_id: str
    lookback: WindowSpec | None
    development: WalkForwardResult
    validation: WalkForwardResult
    complexity: int


@dataclass(frozen=True)
class FrozenChampion:
    model_id: str
    lookback: WindowSpec | None
    model_config_hash: str
    protocol_hash: str


@dataclass(frozen=True)
class ModelTournamentResult:
    protocol_hash: str
    hot_lookback: WindowSpec
    scores: tuple[ModelScore, ...]
    champion: FrozenChampion | None
    frozen: bool
    test: WalkForwardResult | None
    holdout_status: str
    scientific_verdict: str

    def summary(self) -> dict[str, Any]:
        return {
            "protocol_hash": self.protocol_hash,
            "hot_lookback": self.hot_lookback,
            "scores": [
                {
                    "model_id": s.model_id,
                    "lookback": s.lookback,
                    "complexity": s.complexity,
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
                "model_config_hash": self.champion.model_config_hash,
                "protocol_hash": self.champion.protocol_hash,
            },
            "frozen": self.frozen,
            "test": None if self.test is None else self.test.summary(),
            "holdout_status": self.holdout_status,
            "scientific_verdict": self.scientific_verdict,
        }


def _lookback_for_model(
    model_id: str,
    *,
    hot_lookback: WindowSpec,
) -> WindowSpec | None:
    if model_id == MODEL_HOT:
        return hot_lookback
    if model_id == MODEL_RANDOM:
        return None
    if model_id == MODEL_MULTI_SCALE_SHRINKAGE:
        return None
    return hot_lookback


def _model_config_hash(model_id: str, lookback: WindowSpec | None, seed: int) -> str:
    return sha256_canonical(
        {"model_id": model_id, "lookback": lookback, "seed": seed}
    )


def _select_champion(scores: Sequence[ModelScore]) -> ModelScore | None:
    """Select on Validation mean_k; simpler model wins ties."""
    if not scores:
        return None
    return max(
        scores,
        key=lambda s: (s.validation.mean_k, -s.complexity, -s.validation.one_sided_p_mean_k),
    )


def _positive(wf: WalkForwardResult, *, practical_delta: float, alpha: float) -> bool:
    return (
        wf.beats_null
        and wf.lift_mean_k >= practical_delta
        and wf.one_sided_p_mean_k <= alpha
    )


def run_model_tournament(
    draws: Sequence[DrawRecord],
    *,
    protocol: ResearchProtocol | None = None,
    split: ChronologicalSplit | None = None,
    hot_lookback: WindowSpec | None = None,
    run_window_selection: bool = True,
) -> ModelTournamentResult:
    """Round 1 A/B: HOT vs Multi-Scale Shrinkage vs Random.

    Champion is selected on Validation only, then FREEZE. Test confirms once.
    """
    proto = protocol or default_protocol()
    split = split or chronological_split(draws, protocol=proto)
    full = tuple(draws)

    if hot_lookback is None:
        if run_window_selection and len(full) >= proto.min_history + 4:
            win = run_window_tournament(full, protocol=proto, split=split)
            hot_lookback = win.selected_lookback or proto.default_hot_lookback
        else:
            hot_lookback = proto.default_hot_lookback

    scores: list[ModelScore] = []
    for model_id in proto.models:
        lb = _lookback_for_model(model_id, hot_lookback=hot_lookback)
        dev = walkforward_on_segment(
            full,
            split.development,
            model_id=model_id,
            pool_size=proto.pool_size,
            lookback=lb,
            seed=proto.seed,
            min_history=proto.min_history,
        )
        val = walkforward_on_segment(
            full,
            split.validation,
            model_id=model_id,
            pool_size=proto.pool_size,
            lookback=lb,
            seed=proto.seed,
            min_history=proto.min_history,
        )
        scores.append(
            ModelScore(
                model_id=model_id,
                lookback=lb,
                development=dev,
                validation=val,
                complexity=MODEL_COMPLEXITY.get(model_id, 99),
            )
        )

    winner = _select_champion(scores)
    protocol_hash = proto.protocol_hash()

    if winner is None:
        return ModelTournamentResult(
            protocol_hash=protocol_hash,
            hot_lookback=hot_lookback,
            scores=tuple(scores),
            champion=None,
            frozen=False,
            test=None,
            holdout_status=HOLDOUT_SIGNAL_NOT_CONFIRMED,
            scientific_verdict="NO_RANKING_EDGE_FOUND",
        )

    champion = FrozenChampion(
        model_id=winner.model_id,
        lookback=winner.lookback,
        model_config_hash=_model_config_hash(winner.model_id, winner.lookback, proto.seed),
        protocol_hash=protocol_hash,
    )

    # FREEZE then Test confirm only.
    test_wf = walkforward_on_segment(
        full,
        split.test,
        model_id=champion.model_id,
        pool_size=proto.pool_size,
        lookback=champion.lookback,
        seed=proto.seed,
        min_history=proto.min_history,
    )

    val_ok = _positive(
        winner.validation,
        practical_delta=proto.practical_delta_mean_k,
        alpha=proto.alpha,
    )
    test_ok = _positive(
        test_wf,
        practical_delta=proto.practical_delta_mean_k,
        alpha=proto.alpha,
    )
    # Random baseline: champion should not lose badly to random on validation.
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

    return ModelTournamentResult(
        protocol_hash=protocol_hash,
        hot_lookback=hot_lookback,
        scores=tuple(scores),
        champion=champion,
        frozen=True,
        test=test_wf,
        holdout_status=holdout_status,
        scientific_verdict=scientific_verdict,
    )
