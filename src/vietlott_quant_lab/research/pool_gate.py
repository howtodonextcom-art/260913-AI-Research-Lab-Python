"""Pool-18 gate: 45→18 verification checklist."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.research.model_tournament import FrozenChampion, ModelTournamentResult
from vietlott_quant_lab.research.protocol import (
    NO_VERIFIED_18_POOL_EDGE,
    ResearchProtocol,
    default_protocol,
)
from vietlott_quant_lab.research.split import ChronologicalSplit, chronological_split
from vietlott_quant_lab.research.walkforward import WalkForwardResult, walkforward_on_segment


@dataclass(frozen=True)
class PoolGateChecks:
    mean_k_gt_null: bool
    validation_positive: bool
    test_positive: bool
    practical: bool
    no_leak: bool
    robust: bool

    @property
    def passed(self) -> bool:
        return (
            self.mean_k_gt_null
            and self.validation_positive
            and self.test_positive
            and self.practical
            and self.no_leak
            and self.robust
        )

    def as_dict(self) -> dict[str, bool]:
        return {
            "mean_k_gt_null": self.mean_k_gt_null,
            "validation_positive": self.validation_positive,
            "test_positive": self.test_positive,
            "practical": self.practical,
            "no_leak": self.no_leak,
            "robust": self.robust,
            "passed": self.passed,
        }


@dataclass(frozen=True)
class PoolGateResult:
    passed: bool
    status: str
    checks: PoolGateChecks
    validation: WalkForwardResult | None
    test: WalkForwardResult | None
    champion: FrozenChampion | None

    def summary(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "status": self.status,
            "checks": self.checks.as_dict(),
            "validation": None if self.validation is None else self.validation.summary(),
            "test": None if self.test is None else self.test.summary(),
            "champion": None
            if self.champion is None
            else {
                "model_id": self.champion.model_id,
                "lookback": self.champion.lookback,
                "model_config_hash": self.champion.model_config_hash,
            },
        }


def evaluate_pool18_gate(
    draws: Sequence[DrawRecord],
    *,
    tournament: ModelTournamentResult | None = None,
    champion: FrozenChampion | None = None,
    validation: WalkForwardResult | None = None,
    test: WalkForwardResult | None = None,
    protocol: ResearchProtocol | None = None,
    split: ChronologicalSplit | None = None,
    leak_detected: bool = False,
) -> PoolGateResult:
    """45→18 gate: Mean K > null AND Val+ AND Test+ AND practical AND no leak.

    Fail → ``NO_VERIFIED_18_POOL_EDGE``.
    """
    proto = protocol or default_protocol()
    split = split or chronological_split(draws, protocol=proto)
    full = tuple(draws)

    if tournament is not None:
        champion = tournament.champion
        test = tournament.test
        if champion is not None and validation is None:
            # Recompute validation for the frozen champion.
            validation = walkforward_on_segment(
                full,
                split.validation,
                model_id=champion.model_id,
                pool_size=proto.pool_size,
                lookback=champion.lookback,
                seed=proto.seed,
                min_history=proto.min_history,
            )

    if champion is None or validation is None or test is None:
        checks = PoolGateChecks(
            mean_k_gt_null=False,
            validation_positive=False,
            test_positive=False,
            practical=False,
            no_leak=not leak_detected,
            robust=False,
        )
        return PoolGateResult(
            passed=False,
            status=NO_VERIFIED_18_POOL_EDGE,
            checks=checks,
            validation=validation,
            test=test,
            champion=champion,
        )

    mean_k_gt_null = validation.beats_null and test.beats_null
    validation_positive = (
        validation.beats_null and validation.one_sided_p_mean_k <= proto.alpha
    )
    test_positive = test.beats_null and test.one_sided_p_mean_k <= proto.alpha
    practical = (
        validation.lift_mean_k >= proto.practical_delta_mean_k
        and test.lift_mean_k >= proto.practical_delta_mean_k
    )
    # Robustness: both segments agree on direction (both beat null).
    robust = validation.beats_null and test.beats_null
    no_leak = not leak_detected

    checks = PoolGateChecks(
        mean_k_gt_null=mean_k_gt_null,
        validation_positive=validation_positive,
        test_positive=test_positive,
        practical=practical,
        no_leak=no_leak,
        robust=robust,
    )
    status = "POOL18_GATE_PASSED" if checks.passed else NO_VERIFIED_18_POOL_EDGE
    return PoolGateResult(
        passed=checks.passed,
        status=status,
        checks=checks,
        validation=validation,
        test=test,
        champion=champion,
    )
