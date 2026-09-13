"""Walk-forward scoring — anti-leak by construction (history = draws[:t]).

P4: primary endpoint remains Mean K @ Top-m vs exact Hypergeometric null.
Adds ranking-wide metrics (mean/median winner rank, MCP, P(MCP≤m)) and
dependence-aware inference (Newey–West HAC primary; Student-t legacy).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal

from vietlott_quant_lab.config.constants import DRAW_SIZE
from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.ranking.engine import MODEL_REVERSE_PEEK, rank_all
from vietlott_quant_lab.ranking.types import RankingResult
from vietlott_quant_lab.statistics.hypergeometric import expected_k
from vietlott_quant_lab.statistics.inference import (
    newey_west_onesided,
    primary_inference_bundle,
    student_t_onesided,
)
from vietlott_quant_lab.statistics.metrics import (
    empirical_tail_rate,
    intersection_k,
    mcp_from_ranking,
    mcp_le_rate,
    mean_k,
    mean_winner_rank,
    median_winner_rank,
    null_tail_probabilities,
    winner_ranks,
)

WindowSpec = int | Literal["ALL"]


@dataclass(frozen=True)
class WalkForwardStep:
    target_index: int
    draw_id: str
    k: int
    mcp: int
    pool: tuple[int, ...]
    winner_rank_mean: float = 0.0
    winner_ranks: tuple[int, ...] = ()


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
    mean_winner_rank: float = 0.0
    median_winner_rank: float = 0.0
    p_mcp_le_pool: float = 0.0
    one_sided_p_hac: float = 1.0
    inference: dict[str, Any] | None = None

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
            "mean_winner_rank": self.mean_winner_rank,
            "median_winner_rank": self.median_winner_rank,
            "p_mcp_le_pool": self.p_mcp_le_pool,
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
            "one_sided_p_hac": self.one_sided_p_hac,
            "inference": self.inference,
            "beats_null": self.beats_null,
        }


def _resolve_lookback(history_len: int, lookback: WindowSpec | None) -> int | None:
    if lookback is None:
        return None
    if lookback == "ALL":
        return max(history_len, 1)
    return int(lookback)


def _one_sided_p_greater(ks: Sequence[int], null_mean: float) -> float:
    """Legacy Student-t one-sided p (kept for Round-1 artifact compatibility)."""
    return student_t_onesided([float(k) for k in ks], null_value=null_mean).raw_p


def _build_result(
    *,
    model_id: str,
    pool_size: int,
    lookback: WindowSpec | None,
    seed: int,
    steps: list[WalkForwardStep],
) -> WalkForwardResult:
    ks = [s.k for s in steps]
    mcps = [s.mcp for s in steps]
    all_ranks: list[int] = []
    for s in steps:
        all_ranks.extend(s.winner_ranks)
    null = null_tail_probabilities(pool_size)
    emp_mean = mean_k(ks)
    emp_mcp = mean_k(mcps) if mcps else 0.0
    null_m = expected_k(pool_size)
    ks_f = [float(k) for k in ks]
    inference = primary_inference_bundle(ks_f, null_mean=null_m, seed=seed) if ks else None
    hac_p = (
        newey_west_onesided(ks_f, null_value=null_m).raw_p if ks else 1.0
    )
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
        one_sided_p_mean_k=_one_sided_p_greater(ks, null_m),
        n_scored=len(steps),
        mean_winner_rank=mean_winner_rank(all_ranks) if all_ranks else 0.0,
        median_winner_rank=median_winner_rank(all_ranks) if all_ranks else 0.0,
        p_mcp_le_pool=mcp_le_rate(mcps, pool_size),
        one_sided_p_hac=hac_p,
        inference=inference,
    )


def _score_step(
    history: list[DrawRecord],
    target: DrawRecord,
    *,
    target_index: int,
    model_id: str,
    pool_size: int,
    lookback: WindowSpec | None,
    seed: int,
    extra_kwargs: dict[str, Any] | None = None,
) -> WalkForwardStep:
    lb = _resolve_lookback(len(history), lookback)
    rank_kwargs: dict[str, Any] = {"seed": seed}
    if lb is not None:
        rank_kwargs["lookback"] = lb
    if model_id == MODEL_REVERSE_PEEK:
        rank_kwargs["winners"] = target.numbers
    if extra_kwargs:
        rank_kwargs.update(extra_kwargs)
    # EWF uses half_life; map lookback int → half_life when provided as lookback.
    if model_id == "ewf" and lb is not None and "half_life" not in rank_kwargs:
        rank_kwargs["half_life"] = int(lb)

    ranking: RankingResult = rank_all(history, model_id, **rank_kwargs)
    pool = ranking.top_m(pool_size)
    k = intersection_k(pool, target.numbers)
    n2r = ranking.number_to_rank()
    ranks = winner_ranks(n2r, target.numbers)
    mcp = mcp_from_ranking(n2r, target.numbers)
    return WalkForwardStep(
        target_index=target_index,
        draw_id=target.draw_id,
        k=k,
        mcp=mcp,
        pool=pool,
        winner_rank_mean=mean_winner_rank(ranks),
        winner_ranks=ranks,
    )


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
    extra_kwargs: dict[str, Any] | None = None,
) -> WalkForwardResult:
    """Score model walk-forward on ``draws[start_index:end_index]``.

    For each target index ``t``, ranking uses only ``draws[:t]`` (anti-leak).
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
        steps.append(
            _score_step(
                list(draws[:t]),
                draws[t],
                target_index=t,
                model_id=model_id,
                pool_size=pool_size,
                lookback=lookback,
                seed=seed,
                extra_kwargs=extra_kwargs,
            )
        )
    return _build_result(
        model_id=model_id,
        pool_size=pool_size,
        lookback=lookback,
        seed=seed,
        steps=steps,
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
    extra_kwargs: dict[str, Any] | None = None,
) -> WalkForwardResult:
    """Walk-forward over ``segment`` indices within ``full_draws`` (same order)."""
    if not segment:
        return _build_result(
            model_id=model_id,
            pool_size=pool_size,
            lookback=lookback,
            seed=seed,
            steps=[],
        )

    id_to_index = {d.draw_id: i for i, d in enumerate(full_draws)}
    indices = [id_to_index[d.draw_id] for d in segment]
    start = min(indices)
    end = max(indices) + 1
    segment_ids = {d.draw_id for d in segment}
    steps: list[WalkForwardStep] = []
    for t in range(start, end):
        if full_draws[t].draw_id not in segment_ids:
            continue
        if t < min_history:
            continue
        steps.append(
            _score_step(
                list(full_draws[:t]),
                full_draws[t],
                target_index=t,
                model_id=model_id,
                pool_size=pool_size,
                lookback=lookback,
                seed=seed,
                extra_kwargs=extra_kwargs,
            )
        )
    return _build_result(
        model_id=model_id,
        pool_size=pool_size,
        lookback=lookback,
        seed=seed,
        steps=steps,
    )
