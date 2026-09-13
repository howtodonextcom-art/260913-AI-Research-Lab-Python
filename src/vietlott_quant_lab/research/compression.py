"""Compression frontier m=18..7 from a single frozen ranking (nested pools)."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal

from vietlott_quant_lab.config.constants import POOL_SIZES
from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.ranking.engine import rank_all
from vietlott_quant_lab.ranking.pools import assert_nested, nested_pools
from vietlott_quant_lab.ranking.types import RankingResult
from vietlott_quant_lab.research.walkforward import WalkForwardResult, walkforward_score
from vietlott_quant_lab.statistics import bao
from vietlott_quant_lab.statistics.hypergeometric import expected_k
from vietlott_quant_lab.statistics.metrics import null_tail_probabilities

WindowSpec = int | Literal["ALL"]


@dataclass(frozen=True)
class CompressionRow:
    pool_size: int
    null_mean_k: float
    model_mean_k: float
    delta_mean_k: float
    p_ge_4: float
    p_ge_5: float
    p_eq_6: float
    mean_mcp: float
    mcp_le_m_rate: float
    tickets: int
    cost_vnd: int
    p6_bao: float
    evidence_status: str
    pool_numbers: tuple[int, ...]

    def summary(self) -> dict[str, Any]:
        return {
            "pool_size": self.pool_size,
            "null_mean_k": self.null_mean_k,
            "model_mean_k": self.model_mean_k,
            "delta_mean_k": self.delta_mean_k,
            "p_ge_4": self.p_ge_4,
            "p_ge_5": self.p_ge_5,
            "p_eq_6": self.p_eq_6,
            "mean_mcp": self.mean_mcp,
            "mcp_le_m_rate": self.mcp_le_m_rate,
            "tickets": self.tickets,
            "cost_vnd": self.cost_vnd,
            "p6_bao": self.p6_bao,
            "evidence_status": self.evidence_status,
            "pool_numbers": list(self.pool_numbers),
        }


@dataclass(frozen=True)
class CompressionFrontier:
    model_id: str
    lookback: WindowSpec | None
    seed: int
    ranking_snapshot: RankingResult | None
    rows: tuple[CompressionRow, ...]
    nested_ok: bool

    def summary(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "lookback": self.lookback,
            "seed": self.seed,
            "nested_ok": self.nested_ok,
            "rows": [r.summary() for r in self.rows],
        }


def _evidence_status(wf: WalkForwardResult, *, practical_delta: float) -> str:
    if wf.n_scored == 0:
        return "NO_DATA"
    if wf.lift_mean_k >= practical_delta and wf.beats_null:
        return "POSITIVE_DELTA"
    if wf.beats_null:
        return "WEAK_POSITIVE"
    return "NO_EDGE"


def compression_frontier(
    draws: Sequence[DrawRecord],
    *,
    model_id: str,
    lookback: WindowSpec | None = 90,
    seed: int = 0,
    min_history: int = 30,
    pool_sizes: tuple[int, ...] = POOL_SIZES,
    practical_delta_mean_k: float = 0.05,
    ranking_for_nest_check: RankingResult | None = None,
) -> CompressionFrontier:
    """Build m=18..7 frontier from the same frozen ranking family (nested Top-m).

    Walk-forward scores each pool size independently but from the same model /
    lookback / seed so pools remain nested Top-m of one ranking per step.
    """
    sizes = tuple(sorted(pool_sizes, reverse=True))
    rows: list[CompressionRow] = []

    # Nest check on a single ranking snapshot at end of history (documentation).
    history = list(draws)
    if ranking_for_nest_check is None and history:
        kwargs: dict[str, Any] = {"seed": seed}
        if lookback == "ALL":
            kwargs["lookback"] = len(history)
        elif lookback is not None:
            kwargs["lookback"] = int(lookback)
        ranking_for_nest_check = rank_all(history, model_id, **kwargs)

    nested_ok = True
    snapshot_pools: dict[int, frozenset[int]] = {}
    if ranking_for_nest_check is not None:
        snapshot_pools = nested_pools(ranking_for_nest_check, sizes=tuple(sorted(pool_sizes)))
        try:
            assert_nested(snapshot_pools)
        except AssertionError:
            nested_ok = False

    for m in sizes:
        wf = walkforward_score(
            draws,
            model_id=model_id,
            pool_size=m,
            lookback=lookback,
            seed=seed,
            min_history=min_history,
        )
        null = null_tail_probabilities(m)
        mcp_le = (
            sum(1 for s in wf.steps if s.mcp <= m) / len(wf.steps) if wf.steps else 0.0
        )
        pool_nums = (
            tuple(sorted(snapshot_pools[m]))
            if m in snapshot_pools
            else ranking_for_nest_check.top_m(m)
            if ranking_for_nest_check is not None
            else ()
        )
        rows.append(
            CompressionRow(
                pool_size=m,
                null_mean_k=null.mean_k,
                model_mean_k=wf.mean_k,
                delta_mean_k=wf.mean_k - expected_k(m),
                p_ge_4=wf.p_ge_4,
                p_ge_5=wf.p_ge_5,
                p_eq_6=wf.p_eq_6,
                mean_mcp=wf.mean_mcp,
                mcp_le_m_rate=mcp_le,
                tickets=bao.tickets(m),
                cost_vnd=bao.cost(m),
                p6_bao=bao.p6(m),
                evidence_status=_evidence_status(wf, practical_delta=practical_delta_mean_k),
                pool_numbers=pool_nums,
            )
        )

    # Nested invariant on snapshot Top-m sets.
    if nested_ok and len(rows) >= 2:
        by_m = {r.pool_size: set(r.pool_numbers) for r in rows if r.pool_numbers}
        ordered = sorted(by_m)
        for i in range(1, len(ordered)):
            if not by_m[ordered[i - 1]] <= by_m[ordered[i]]:
                nested_ok = False
                break

    return CompressionFrontier(
        model_id=model_id,
        lookback=lookback,
        seed=seed,
        ranking_snapshot=ranking_for_nest_check,
        rows=tuple(rows),
        nested_ok=nested_ok,
    )


def assert_top_nested(frontier: CompressionFrontier, smaller: int, larger: int) -> None:
    """Assert Top-``smaller`` ⊂ Top-``larger`` on the frontier snapshot pools."""
    by_m = {r.pool_size: set(r.pool_numbers) for r in frontier.rows}
    if smaller not in by_m or larger not in by_m:
        msg = f"missing pool sizes {smaller}/{larger} in frontier"
        raise KeyError(msg)
    if not by_m[smaller] <= by_m[larger]:
        msg = f"Top{smaller} not subset of Top{larger}"
        raise AssertionError(msg)
