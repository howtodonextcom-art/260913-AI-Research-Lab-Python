"""Exact hypergeometric null for pool size m vs Mega 6/45."""

from __future__ import annotations

from math import comb

from vietlott_quant_lab.config.constants import DRAW_SIZE, NUMBER_MAX


def hypergeometric_pmf(m: int, k: int) -> float:
    """P(K = k) where K = |pool ∩ winning set|, pool size m, draw 6 from 45.

    Closed form: C(m,k) * C(45-m, 6-k) / C(45, 6). No Monte Carlo.
    """
    if m < 0 or m > NUMBER_MAX:
        msg = f"pool size m out of range: {m}"
        raise ValueError(msg)
    if k < 0 or k > DRAW_SIZE:
        return 0.0
    if k > m or (DRAW_SIZE - k) > (NUMBER_MAX - m):
        return 0.0
    return (comb(m, k) * comb(NUMBER_MAX - m, DRAW_SIZE - k)) / comb(NUMBER_MAX, DRAW_SIZE)


def expected_k(m: int) -> float:
    """E[K] = 6 * m / 45."""
    if m < 0 or m > NUMBER_MAX:
        msg = f"pool size m out of range: {m}"
        raise ValueError(msg)
    return DRAW_SIZE * m / float(NUMBER_MAX)


def hypergeometric_tail_ge(m: int, k: int) -> float:
    """Exact upper tail P(K >= k)."""
    if k <= 0:
        return 1.0
    return sum(hypergeometric_pmf(m, i) for i in range(k, DRAW_SIZE + 1))


def pmf_support(m: int) -> dict[int, float]:
    """Full PMF over k = 0..6."""
    return {k: hypergeometric_pmf(m, k) for k in range(DRAW_SIZE + 1)}
