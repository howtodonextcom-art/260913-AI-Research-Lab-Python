"""P4 inference + ranking-wide metric tests."""

from __future__ import annotations

import math

from hypothesis import given, settings
from hypothesis import strategies as st

from vietlott_quant_lab.statistics.inference import (
    absolute_lift,
    moving_block_bootstrap_ci,
    newey_west_onesided,
    paired_permutation_pvalue,
    primary_inference_bundle,
    relative_lift,
    student_t_onesided,
)
from vietlott_quant_lab.statistics.metrics import (
    mcp_le_rate,
    mean_winner_rank,
    median_winner_rank,
)


def test_absolute_and_relative_lift() -> None:
    assert abs(absolute_lift(2.45, 2.4) - 0.05) < 1e-12
    assert abs(relative_lift(2.45, 2.4) - 0.05 / 2.4) < 1e-12


def test_newey_west_detects_clear_lift() -> None:
    # Strong positive lift series
    ks = [3.0] * 80
    report = newey_west_onesided(ks, null_value=2.4)
    assert report.effect > 0.5
    assert report.raw_p < 0.01


def test_newey_west_nullish_series() -> None:
    ks = [2.4 + ((-1) ** i) * 0.01 for i in range(100)]
    report = newey_west_onesided(ks, null_value=2.4)
    assert report.raw_p > 0.05


def test_student_t_legacy_matches_direction() -> None:
    ks = [3.0] * 50
    t = student_t_onesided(ks, null_value=2.4)
    assert t.raw_p < 0.01


def test_block_bootstrap_returns_ci() -> None:
    ks = [2.5 + 0.1 * ((-1) ** i) for i in range(60)]
    boot = moving_block_bootstrap_ci(ks, null_value=2.4, n_boot=199, seed=0)
    assert boot.ci_low <= boot.effect <= boot.ci_high or math.isnan(boot.ci_low)
    assert 0.0 <= boot.raw_p <= 1.0


def test_paired_permutation_favors_a() -> None:
    a = [3.0] * 40
    b = [2.0] * 40
    report = paired_permutation_pvalue(a, b, n_perm=499, seed=1)
    assert report.effect > 0.5
    assert report.raw_p < 0.05


def test_primary_bundle_keys() -> None:
    bundle = primary_inference_bundle([2.5] * 40, null_mean=2.4, seed=0)
    assert bundle["primary_method"] == "newey_west_hac"
    assert "absolute_lift" in bundle
    assert "moving_block_bootstrap" in bundle


def test_mean_median_winner_rank() -> None:
    ranks = (1, 2, 3, 4, 5, 6)
    assert abs(mean_winner_rank(ranks) - 3.5) < 1e-12
    assert abs(median_winner_rank(ranks) - 3.5) < 1e-12
    assert abs(median_winner_rank((1, 2, 3)) - 2.0) < 1e-12


def test_mcp_le_rate() -> None:
    assert abs(mcp_le_rate([10, 18, 20, 18], 18) - 0.75) < 1e-12


@given(st.lists(st.floats(min_value=0, max_value=6, allow_nan=False), min_size=5, max_size=40))
@settings(max_examples=20)
def test_hac_p_in_unit_interval(vals: list[float]) -> None:
    report = newey_west_onesided(vals, null_value=2.4)
    assert 0.0 <= report.raw_p <= 1.0
