"""P3 feature / leak tests."""

from __future__ import annotations

from datetime import timedelta

import pytest
from tests.conftest_research import make_draw, synthetic_history

from vietlott_quant_lab.features.leak import assert_no_future_leak
from vietlott_quant_lab.features.vector import build_all_feature_vectors
from vietlott_quant_lab.features.windows import MULTI_SCALE_WINDOWS


def test_multi_scale_windows_contract() -> None:
    assert MULTI_SCALE_WINDOWS == (
        15,
        30,
        45,
        60,
        90,
        120,
        180,
        270,
        365,
        500,
        750,
        1000,
        "ALL",
    )


def test_assert_no_future_leak_passes_on_strict_past() -> None:
    history = synthetic_history(10)
    target = history[-1].draw_date + timedelta(days=1)
    assert_no_future_leak(history, target)


def test_assert_no_future_leak_fails_on_injected_future() -> None:
    history = synthetic_history(5)
    target = history[-1].draw_date
    future = make_draw(
        "99999",
        target,
        (1, 2, 3, 4, 5, 6),
    )
    with pytest.raises(ValueError, match="Future leak"):
        assert_no_future_leak([*history, future], target)


def test_feature_vectors_cover_1_to_45() -> None:
    history = synthetic_history(80)
    vectors = build_all_feature_vectors(history)
    assert set(vectors) == set(range(1, 46))
    assert all(v.history_size == len(history) for v in vectors.values())
    # Deterministic: second call identical shrinkage / gap
    again = build_all_feature_vectors(history)
    for n in range(1, 46):
        assert vectors[n].gap == again[n].gap
        assert vectors[n].shrinkage_signal == again[n].shrinkage_signal


def test_build_feature_vector_respects_target_leak_check() -> None:
    history = synthetic_history(3)
    bad = make_draw("00099", history[-1].draw_date, (7, 8, 9, 10, 11, 12))
    with pytest.raises(ValueError, match="Future leak"):
        build_all_feature_vectors([*history, bad], target_date=history[-1].draw_date)
