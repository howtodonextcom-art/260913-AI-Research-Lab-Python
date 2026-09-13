"""Walk-forward scoring — anti-leak by construction (history = draws[:t])."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal

from scipy import stats  # type: ignore[import-untyped]

from vietlott_quant_lab.config.constants import DRAW_SIZE
from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.ranking.engine import MODEL_REVERSE_PEEK, rank_all
from vietlott_quant_lab.ranking.types import RankingResult
from vietlott_quant_lab.statistics.hypergeometric import expected_k
from vietlott_quant_lab.statistics.metrics import (
    empirical_tail_rate,
    intersection_k,
    mcp_from_ranking,
    mean_k,
    null_tail_probabilities,
)

WindowSpec = int | Literal["ALL"]


@dataclass(frozen=True)
class WalkForwardStep:
    target_index: int
    draw_id: str
    k: int
    mcp: int
    pool: tuple[int, ...]


@dataclass(frozen=True)
class WalkForwardResult:
    model_id: str
    pool_size: int
    lookback: WindowSpec | None
    seed: int
    steps: tuple[WalkForwardStep, ...]
    mean_k: float
    mean_mcp: float
    null_mean_k: float
    lift_mean_k: float
    p_ge_3: float
    p_ge_4: float
    p_ge_5: float
    p_eq_6: float
    null_p_ge_3: float
    null_p_ge_4: float
    null_p_ge_5: float
    null_p_eq_6: float
    one_sided_p_mean_k: float
    n_scored: int

    @property
    def beats_null(self) -> bool:
        return self.mean_k > self.null_mean_k

    def summary(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "pool_size": self.pool_size,
            "lookback": self.lookback,
            "seed": self.seed,
            "n_scored": self.n_scored,
            "mean_k": self.mean_k,
            "mean_mcp": self.mean_mcp,
            "null_mean_k": self.null_mean_k,
            "lift_mean_k": self.lift_mean_k,
            "p_ge_3": self.p_ge_3,
            "p_ge_4": self.p_ge_4,
            "p_ge_5": self.p_ge_5,
            "p_eq_6": self.p_eq_6,
            "null_p_ge_3": self.null_p_ge_3,
            "null_p_ge_4": self.null_p_ge_4,
            "null_p_ge_5": self.null_p_ge_5,
            "null_p_eq_6": self.null_p_eq_6,
            "one_sided_p_mean_k": self.one_sided_p_mean_k,
            "beats_null": self.beats_null,
        }


def _resolve_lookback(history_len: int, lookback: WindowSpec | None) -> int | None:
    if lookback is None:
        return None
    if lookback == "ALL":
        return max(history_len, 1)
    return int(lookback)


def _one_sided_p_greater(ks: Sequence[int], null_mean: float) -> float:
    """One-sided p-value for H1: E[K] > null_mean (Student t)."""
    if len(ks) < 2:
        return 1.0
    # Constant series → avoid SciPy precision-loss warning; p=0 if above null.
    if max(ks) == min(ks):
        return 0.0 if mean_k(ks) > null_mean else 1.0
    result = stats.ttest_1samp(list(ks), null_mean, alternative="greater")
    p = float(result.pvalue)
    if p != p:  # NaN
        return 1.0 if mean_k(ks) <= null_mean else 0.0
    return min(1.0, max(0.0, p))


def walkforward_score(
    draws: Sequence[DrawRecord],
    *,
    model_id: str,
    pool_size: int = 18,
    lookback: WindowSpec | None = 90,
    seed: int = 0,
    start_index: int | None = None,
    end_index: int | None = None,
    min_history: int = 30,
) -> WalkForwardResult:
    """Score model walk-forward on ``draws[start_index:end_index]``.

    For each target index ``t``, ranking uses only ``draws[:t]`` (anti-leak).
    ``start_index`` defaults to ``min_history``; ``end_index`` defaults to ``len(draws)``.
    """
    n = len(draws)
    if start_index is None:
        start_index = min_history
    if end_index is None:
        end_index = n
    if not (0 <= start_index <= end_index <= n):
        msg = f"invalid range [{start_index}, {end_index}) for n={n}"
        raise ValueError(msg)

    steps: list[WalkForwardStep] = []
    for t in range(start_index, end_index):
        history = list(draws[:t])
        target = draws[t]
        lb = _resolve_lookback(len(history), lookback)
        rank_kwargs: dict[str, Any] = {"seed": seed}
        if lb is not None:
            rank_kwargs["lookback"] = lb
        if model_id == MODEL_REVERSE_PEEK:
            rank_kwargs["winners"] = target.numbers

        ranking: RankingResult = rank_all(history, model_id, **rank_kwargs)
        pool = ranking.top_m(pool_size)
        k = intersection_k(pool, target.numbers)
        mcp = mcp_from_ranking(ranking.number_to_rank(), target.numbers)
        steps.append(
            WalkForwardStep(
                target_index=t,
                draw_id=target.draw_id,
                k=k,
                mcp=mcp,
                pool=pool,
            )
        )

    ks = [s.k for s in steps]
    mcps = [s.mcp for s in steps]
    null = null_tail_probabilities(pool_size)
    emp_mean = mean_k(ks)
    emp_mcp = mean_k(mcps) if mcps else 0.0
    return WalkForwardResult(
        model_id=model_id,
        pool_size=pool_size,
        lookback=lookback,
        seed=seed,
        steps=tuple(steps),
        mean_k=emp_mean,
        mean_mcp=emp_mcp,
        null_mean_k=null.mean_k,
        lift_mean_k=emp_mean - null.mean_k,
        p_ge_3=empirical_tail_rate(ks, 3),
        p_ge_4=empirical_tail_rate(ks, 4),
        p_ge_5=empirical_tail_rate(ks, 5),
        p_eq_6=empirical_tail_rate(ks, DRAW_SIZE),
        null_p_ge_3=null.p_ge_3,
        null_p_ge_4=null.p_ge_4,
        null_p_ge_5=null.p_ge_5,
        null_p_eq_6=null.p_eq_6,
        one_sided_p_mean_k=_one_sided_p_greater(ks, expected_k(pool_size)),
        n_scored=len(steps),
    )


def walkforward_on_segment(
    full_draws: Sequence[DrawRecord],
    segment: Sequence[DrawRecord],
    *,
    model_id: str,
    pool_size: int = 18,
    lookback: WindowSpec | None = 90,
    seed: int = 0,
    min_history: int = 30,
) -> WalkForwardResult:
    """Walk-forward over ``segment`` indices within ``full_draws`` (same order).

    Uses global indices so history always includes all draws before the target
    in the full chronological series (not only the segment prefix).
    """
    if not segment:
        null = null_tail_probabilities(pool_size)
        return WalkForwardResult(
            model_id=model_id,
            pool_size=pool_size,
            lookback=lookback,
            seed=seed,
            steps=(),
            mean_k=0.0,
            mean_mcp=0.0,
            null_mean_k=null.mean_k,
            lift_mean_k=-null.mean_k,
            p_ge_3=0.0,
            p_ge_4=0.0,
            p_ge_5=0.0,
            p_eq_6=0.0,
            null_p_ge_3=null.p_ge_3,
            null_p_ge_4=null.p_ge_4,
            null_p_ge_5=null.p_ge_5,
            null_p_eq_6=null.p_eq_6,
            one_sided_p_mean_k=1.0,
            n_scored=0,
        )

    id_to_index = {d.draw_id: i for i, d in enumerate(full_draws)}
    indices = [id_to_index[d.draw_id] for d in segment]
    start = min(indices)
    end = max(indices) + 1
    # Ensure contiguous segment scoring: score every index in [start, end)
    # that belongs to the segment set.
    segment_ids = {d.draw_id for d in segment}
    steps: list[WalkForwardStep] = []
    for t in range(start, end):
        if full_draws[t].draw_id not in segment_ids:
            continue
        if t < min_history:
            continue
        history = list(full_draws[:t])
        target = full_draws[t]
        lb = _resolve_lookback(len(history), lookback)
        rank_kwargs: dict[str, Any] = {"seed": seed}
        if lb is not None:
            rank_kwargs["lookback"] = lb
        if model_id == MODEL_REVERSE_PEEK:
            rank_kwargs["winners"] = target.numbers
        ranking = rank_all(history, model_id, **rank_kwargs)
        pool = ranking.top_m(pool_size)
        k = intersection_k(pool, target.numbers)
        mcp = mcp_from_ranking(ranking.number_to_rank(), target.numbers)
        steps.append(
            WalkForwardStep(
                target_index=t,
                draw_id=target.draw_id,
                k=k,
                mcp=mcp,
                pool=pool,
            )
        )

    ks = [s.k for s in steps]
    mcps = [s.mcp for s in steps]
    null = null_tail_probabilities(pool_size)
    emp_mean = mean_k(ks)
    emp_mcp = mean_k(mcps) if mcps else 0.0
    return WalkForwardResult(
        model_id=model_id,
        pool_size=pool_size,
        lookback=lookback,
        seed=seed,
        steps=tuple(steps),
        mean_k=emp_mean,
        mean_mcp=emp_mcp,
        null_mean_k=null.mean_k,
        lift_mean_k=emp_mean - null.mean_k,
        p_ge_3=empirical_tail_rate(ks, 3),
        p_ge_4=empirical_tail_rate(ks, 4),
        p_ge_5=empirical_tail_rate(ks, 5),
        p_eq_6=empirical_tail_rate(ks, DRAW_SIZE),
        null_p_ge_3=null.p_ge_3,
        null_p_ge_4=null.p_ge_4,
        null_p_ge_5=null.p_ge_5,
        null_p_eq_6=null.p_eq_6,
        one_sided_p_mean_k=_one_sided_p_greater(ks, expected_k(pool_size)),
        n_scored=len(steps),
    )
