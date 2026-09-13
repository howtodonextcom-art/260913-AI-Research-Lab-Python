"""Compute scientific status from tournament / gate / prospective results."""

from __future__ import annotations

from typing import Any

from vietlott_quant_lab.research.model_tournament import ModelTournamentResult
from vietlott_quant_lab.research.pool_gate import PoolGateResult
from vietlott_quant_lab.research.protocol import (
    HOLDOUT_SIGNAL_NOT_CONFIRMED,
    NO_VERIFIED_18_POOL_EDGE,
    SCIENTIFIC_VERDICTS,
    ScientificVerdict,
)
from vietlott_quant_lab.research.window_tournament import WindowTournamentResult


def compute_scientific_verdict(
    *,
    model_tournament: ModelTournamentResult | None = None,
    window_tournament: WindowTournamentResult | None = None,
    pool_gate: PoolGateResult | None = None,
    prospective_scored: bool = False,
    exploratory_signal: bool | None = None,
) -> ScientificVerdict:
    """Map research outcomes onto the scientific status ladder.

    Tokens (exact):
    ``NO_RANKING_EDGE_FOUND`` | ``EXPLORATORY_SIGNAL`` | ``VALIDATION_SIGNAL`` |
    ``HOLDOUT_SIGNAL`` | ``PROSPECTIVE_SIGNAL``
    """
    if prospective_scored:
        return "PROSPECTIVE_SIGNAL"

    if model_tournament is not None:
        v = model_tournament.scientific_verdict
        if v in SCIENTIFIC_VERDICTS:
            return v

    if pool_gate is not None and pool_gate.passed:
        return "HOLDOUT_SIGNAL"

    if model_tournament is not None:
        if model_tournament.holdout_status == "HOLDOUT_SIGNAL":
            return "HOLDOUT_SIGNAL"
        if model_tournament.holdout_status == HOLDOUT_SIGNAL_NOT_CONFIRMED:
            return "VALIDATION_SIGNAL"

    if exploratory_signal is True:
        return "EXPLORATORY_SIGNAL"

    if window_tournament is not None:
        for c in window_tournament.development_ranked:
            if c.holm is not None and c.holm.rejected and c.development.beats_null:
                return "EXPLORATORY_SIGNAL"
            if c.development.beats_null and c.development.lift_mean_k > 0.05:
                return "EXPLORATORY_SIGNAL"

    if pool_gate is not None and pool_gate.status == NO_VERIFIED_18_POOL_EDGE:
        return "NO_RANKING_EDGE_FOUND"

    return "NO_RANKING_EDGE_FOUND"


def verdict_report(
    *,
    scientific: ScientificVerdict,
    pool_gate: PoolGateResult | None = None,
    model_tournament: ModelTournamentResult | None = None,
) -> dict[str, Any]:
    """Compact report for artifacts / UI."""
    return {
        "scientific_verdict": scientific,
        "pool_gate_status": None if pool_gate is None else pool_gate.status,
        "holdout_status": None if model_tournament is None else model_tournament.holdout_status,
        "champion_model": (
            None
            if model_tournament is None or model_tournament.champion is None
            else model_tournament.champion.model_id
        ),
    }
