"""Ablation and fragility red-team for Algorithm V2 (P7)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal

from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.ranking.engine import MODEL_MULTI_SCALE_V2, rank_all
from vietlott_quant_lab.ranking.models.multi_scale_v2 import DEFAULT_WEIGHTS
from vietlott_quant_lab.research.protocol_v2 import ResearchProtocolV2, default_protocol_v2
from vietlott_quant_lab.research.split import chronological_split
from vietlott_quant_lab.research.walkforward import WalkForwardResult, walkforward_on_segment
from vietlott_quant_lab.statistics.metrics import intersection_k, mcp_from_ranking

AblationLabel = Literal["HELPFUL", "NEUTRAL", "HARMFUL"]


FEATURE_GROUPS: tuple[str, ...] = (
    "z_freq",
    "momentum_short",
    "momentum_medium",
    "stability",
    "shrinkage",
    "gap",
    "mean_reversion",
)


@dataclass(frozen=True)
class AblationRow:
    feature_group: str
    baseline_mean_k: float
    ablated_mean_k: float
    delta_mean_k: float
    label: AblationLabel

    def summary(self) -> dict[str, Any]:
        return {
            "feature_group": self.feature_group,
            "baseline_mean_k": self.baseline_mean_k,
            "ablated_mean_k": self.ablated_mean_k,
            "delta_mean_k": self.delta_mean_k,
            "label": self.label,
        }


@dataclass(frozen=True)
class FragilityResult:
    perturbation: str
    mean_k: float
    lift_mean_k: float
    unstable: bool
    notes: str

    def summary(self) -> dict[str, Any]:
        return {
            "perturbation": self.perturbation,
            "mean_k": self.mean_k,
            "lift_mean_k": self.lift_mean_k,
            "unstable": self.unstable,
            "notes": self.notes,
        }


def _label(delta: float, *, tol: float = 0.01) -> AblationLabel:
    """Removing a HELPFUL feature hurts mean_k (ablated < baseline → positive delta here)."""
    if delta > tol:
        return "HELPFUL"
    if delta < -tol:
        return "HARMFUL"
    return "NEUTRAL"


def run_ablation_v2(
    draws: Sequence[DrawRecord],
    *,
    protocol: ResearchProtocolV2 | None = None,
    segment: Literal["validation"] = "validation",
) -> tuple[AblationRow, ...]:
    """Ablate each Multi-Scale V2 feature group on Validation (never Test)."""
    proto = protocol or default_protocol_v2()
    split = chronological_split(draws, protocol=proto.as_round1_compatible())
    seg = split.validation if segment == "validation" else split.validation
    full = tuple(draws)

    baseline = walkforward_on_segment(
        full,
        seg,
        model_id=MODEL_MULTI_SCALE_V2,
        pool_size=proto.pool_size,
        lookback=None,
        seed=proto.seed,
        min_history=proto.min_history,
    )

    rows: list[AblationRow] = []
    for group in FEATURE_GROUPS:
        weights = dict(DEFAULT_WEIGHTS)
        weights[group] = 0.0
        ablated = walkforward_on_segment(
            full,
            seg,
            model_id=MODEL_MULTI_SCALE_V2,
            pool_size=proto.pool_size,
            lookback=None,
            seed=proto.seed,
            min_history=proto.min_history,
            extra_kwargs={"weights": weights},
        )
        delta = baseline.mean_k - ablated.mean_k
        rows.append(
            AblationRow(
                feature_group=group,
                baseline_mean_k=baseline.mean_k,
                ablated_mean_k=ablated.mean_k,
                delta_mean_k=delta,
                label=_label(delta),
            )
        )
    return tuple(rows)


def run_fragility_battery(
    draws: Sequence[DrawRecord],
    *,
    model_id: str,
    lookback: int | None = 90,
    protocol: ResearchProtocolV2 | None = None,
    practical_delta: float | None = None,
) -> tuple[FragilityResult, ...]:
    """Stress champion-like config; mark FRAGILE if tiny changes destroy lift."""
    proto = protocol or default_protocol_v2()
    delta_gate = (
        practical_delta if practical_delta is not None else proto.practical_delta_mean_k
    )
    split = chronological_split(draws, protocol=proto.as_round1_compatible())
    full = tuple(draws)
    base = walkforward_on_segment(
        full,
        split.validation,
        model_id=model_id,
        pool_size=proto.pool_size,
        lookback=lookback,
        seed=proto.seed,
        min_history=proto.min_history,
    )

    results: list[FragilityResult] = []

    def _row(name: str, wf: WalkForwardResult, *, notes: str = "") -> FragilityResult:
        unstable = abs(wf.lift_mean_k - base.lift_mean_k) > max(0.05, delta_gate)
        return FragilityResult(
            perturbation=name,
            mean_k=wf.mean_k,
            lift_mean_k=wf.lift_mean_k,
            unstable=unstable,
            notes=notes,
        )

    results.append(_row("baseline_validation", base, notes="reference"))

    # Seed sensitivity
    for seed in (1, 2, 7, 42):
        wf = walkforward_on_segment(
            full,
            split.validation,
            model_id=model_id,
            pool_size=proto.pool_size,
            lookback=lookback,
            seed=seed,
            min_history=proto.min_history,
        )
        results.append(_row(f"seed_{seed}", wf))

    # Lookback perturbation (±20%) when applicable
    if lookback is not None and lookback >= 10:
        for lb in (max(10, int(lookback * 0.8)), int(lookback * 1.2)):
            wf = walkforward_on_segment(
                full,
                split.validation,
                model_id=model_id,
                pool_size=proto.pool_size,
                lookback=lb,
                seed=proto.seed,
                min_history=proto.min_history,
            )
            results.append(_row(f"lookback_{lb}", wf))

    # Era splits: early / middle / late thirds of validation
    val = list(split.validation)
    if len(val) >= 30:
        third = len(val) // 3
        eras = {
            "era_early": val[:third],
            "era_middle": val[third : 2 * third],
            "era_late": val[2 * third :],
        }
        for name, era in eras.items():
            wf = walkforward_on_segment(
                full,
                era,
                model_id=model_id,
                pool_size=proto.pool_size,
                lookback=lookback,
                seed=proto.seed,
                min_history=proto.min_history,
            )
            results.append(_row(name, wf))

    # Shuffled chronology control (should destroy temporal signal)
    shuffled = walkforward_on_segment(
        full,
        split.validation,
        model_id="shuffled_history",
        pool_size=proto.pool_size,
        lookback=lookback if lookback is not None else 90,
        seed=proto.seed,
        min_history=proto.min_history,
    )
    results.append(
        _row(
            "shuffled_history_control",
            shuffled,
            notes="control_expected_near_null",
        )
    )

    # Reverse peek harness check on a tiny recent window (must dominate)
    if len(full) > proto.min_history + 5:
        peek_ks: list[int] = []
        for t in range(len(full) - 5, len(full)):
            hist = list(full[:t])
            target = full[t]
            ranking = rank_all(hist, "reverse_peek", winners=target.numbers, seed=0)
            peek_ks.append(intersection_k(ranking.top_m(proto.pool_size), target.numbers))
            _ = mcp_from_ranking(ranking.number_to_rank(), target.numbers)
        peek_mean = sum(peek_ks) / len(peek_ks)
        results.append(
            FragilityResult(
                perturbation="reverse_peek_harness",
                mean_k=peek_mean,
                lift_mean_k=peek_mean - 2.4,
                unstable=peek_mean < 5.0,
                notes=(
                    "INVALID_AS_PREDICTIVE_EVIDENCE; harness broken if mean_k < 5"
                    if peek_mean < 5.0
                    else "INVALID_AS_PREDICTIVE_EVIDENCE; harness_ok"
                ),
            )
        )

    return tuple(results)


def fragility_label(results: Sequence[FragilityResult]) -> str:
    """Return FRAGILE_SIGNAL if seed/lookback/era perturbations flip the lift sign."""
    base = next((r for r in results if r.perturbation == "baseline_validation"), None)
    if base is None:
        return "UNKNOWN"
    unstable_count = sum(
        1
        for r in results
        if r.perturbation.startswith(("seed_", "lookback_", "era_")) and r.unstable
    )
    if unstable_count >= 3:
        return "FRAGILE_SIGNAL"
    return "STABLE_ENOUGH"


def ablation_summary_table(rows: Sequence[AblationRow]) -> list[dict[str, Any]]:
    return [r.summary() for r in rows]


def weights_without(group: str, base: Mapping[str, float] | None = None) -> dict[str, float]:
    w = dict(DEFAULT_WEIGHTS if base is None else base)
    w[group] = 0.0
    return w
