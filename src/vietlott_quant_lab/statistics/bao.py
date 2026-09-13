"""Bao (full combinatorial coverage) cost identities for pool size m."""

from __future__ import annotations

from math import comb

from vietlott_quant_lab.config.constants import DRAW_SIZE, NUMBER_MAX

TICKET_PRICE_VND = 10_000


def tickets(m: int) -> int:
    """Tickets(m) = C(m, 6)."""
    if m < DRAW_SIZE:
        return 0
    if m > NUMBER_MAX:
        msg = f"pool size m out of range: {m}"
        raise ValueError(msg)
    return comb(m, DRAW_SIZE)


def cost(m: int, *, ticket_price: int = TICKET_PRICE_VND) -> int:
    """Cost(m) = ticket_price * C(m, 6)."""
    return ticket_price * tickets(m)


def p6(m: int) -> float:
    """Exact P6(m) = C(m, 6) / C(45, 6) for full bao of pool m."""
    if m < DRAW_SIZE:
        return 0.0
    if m > NUMBER_MAX:
        msg = f"pool size m out of range: {m}"
        raise ValueError(msg)
    return comb(m, DRAW_SIZE) / comb(NUMBER_MAX, DRAW_SIZE)
