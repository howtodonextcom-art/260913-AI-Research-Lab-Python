"""Lookback-window tournament on Development; promote top candidates to Validation."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal

from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.ranking.engine import MODEL_HOT
from vietlott_quant_lab.research.protocol import ResearchProtocol, default_protocol
from vietlott_quant_lab.research.split import ChronologicalSplit, chronological_split
from vietlott_quant_lab.research.walkforward import WalkForwardResult, walkforward_on_segment
from vietlott_quant_lab.statistics.multiplicity import HolmResult, holm_bonferroni

WindowSpec = int | Literal["ALL"]


@dataclass(frozen=True)
class WindowCandidate:
    lookback: WindowSpec
    development: WalkForwardResult
    holm: HolmResult | None = None


@dataclass(frozen=True)
class WindowTournamentResult:
    """Window comparison — Test is never used to pick a window."""

    protocol_hash: str
    development_ranked: tuple[WindowCandidate, ...]
    validation_candidates: tuple[WindowCandidate, ...]
    validation_scores: tuple[tuple[WindowSpec, WalkForwardResult], ...]
    selected_lookback: WindowSpec | None
    frozen: bool

    def summary(self) -> dict[str, Any]:
        return {
            "protocol_hash": self.protocol_hash,
            "development": [
                {
                    "lookback": c.lookback,
                    **c.development.summary(),
                    "holm_adjusted_p": None if c.holm is None else c.holm.adjusted_p,
                    "holm_rejected": None if c.holm is None else c.holm.rejected,
                }
                for c in self.development_ranked
            ],
            "validation": [
                {"lookback": lb, **wf.summary()} for lb, wf in self.validation_scores
            ],
            "selected_lookback": self.selected_lookback,
            "frozen": self.frozen,
        }


def _window_sort_key(c: WindowCandidate) -> tuple[float, float, str]:
    # Higher mean_k better; lower p better; stable lookback label.
    label = "ALL" if c.lookback == "ALL" else f"{int(c.lookback):05d}"
    return (-c.development.mean_k, c.development.one_sided_p_mean_k, label)


def run_window_tournament(
    draws: Sequence[DrawRecord],
    *,
    protocol: ResearchProtocol | None = None,
    split: ChronologicalSplit | None = None,
    model_id: str = MODEL_HOT,
) -> WindowTournamentResult:
    """Compare lookback windows on Development; select champion on Validation only.

    Never uses Test to pick a window.
    """
    proto = protocol or default_protocol()
    split = split or chronological_split(draws, protocol=proto)
    full = tuple(draws)

    # Development: score every registered window.
    raw: list[WindowCandidate] = []
    for window in proto.lookback_windows:
        wf = walkforward_on_segment(
            full,
            split.development,
            model_id=model_id,
            pool_size=proto.pool_size,
            lookback=window,
            seed=proto.seed,
            min_history=proto.min_history,
        )
        raw.append(WindowCandidate(lookback=window, development=wf))

    p_values = [c.development.one_sided_p_mean_k for c in raw]
    holm = holm_bonferroni(p_values, alpha=proto.alpha)
    with_holm = [
        WindowCandidate(lookback=c.lookback, development=c.development, holm=h)
        for c, h in zip(raw, holm, strict=True)
    ]
    ranked = tuple(sorted(with_holm, key=_window_sort_key))

    top_n = min(proto.top_window_candidates, len(ranked))
    candidates = ranked[:top_n]

    # Validation: re-score top candidates only; pick best.
    val_scores: list[tuple[WindowSpec, WalkForwardResult]] = []
    for c in candidates:
        wf = walkforward_on_segment(
            full,
            split.validation,
            model_id=model_id,
            pool_size=proto.pool_size,
            lookback=c.lookback,
            seed=proto.seed,
            min_history=proto.min_history,
        )
        val_scores.append((c.lookback, wf))

    selected: WindowSpec | None = None
    if val_scores:
        selected = max(val_scores, key=lambda x: (x[1].mean_k, -x[1].one_sided_p_mean_k))[0]

    return WindowTournamentResult(
        protocol_hash=proto.protocol_hash(),
        development_ranked=ranked,
        validation_candidates=candidates,
        validation_scores=tuple(val_scores),
        selected_lookback=selected,
        frozen=selected is not None,
    )
