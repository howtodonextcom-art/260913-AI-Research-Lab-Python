"""Multiple-testing corrections."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class HolmResult:
    raw_p: float
    adjusted_p: float
    rejected: bool
    rank: int


def holm_bonferroni(
    p_values: Sequence[float],
    *,
    alpha: float = 0.05,
) -> list[HolmResult]:
    """Holm–Bonferroni step-down adjustment.

    Returns results aligned to the original order of ``p_values``.
    """
    n = len(p_values)
    if n == 0:
        return []
    for p in p_values:
        if not (0.0 <= p <= 1.0):
            msg = f"p-value out of [0,1]: {p}"
            raise ValueError(msg)

    order = sorted(range(n), key=lambda i: p_values[i])
    adjusted = [0.0] * n
    rejected = [False] * n
    ranks = [0] * n

    running_max = 0.0
    stop = False
    for rank_idx, i in enumerate(order):
        ranks[i] = rank_idx + 1
        factor = n - rank_idx
        adj = min(1.0, p_values[i] * factor)
        running_max = max(running_max, adj)
        adjusted[i] = running_max
        if not stop and adjusted[i] <= alpha:
            rejected[i] = True
        else:
            stop = True
            rejected[i] = False

    return [
        HolmResult(raw_p=p_values[i], adjusted_p=adjusted[i], rejected=rejected[i], rank=ranks[i])
        for i in range(n)
    ]
