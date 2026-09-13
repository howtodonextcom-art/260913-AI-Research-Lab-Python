"""P5 ranking / pools / controls tests."""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st
from tests.conftest_research import synthetic_history

from vietlott_quant_lab.ranking.engine import (
    MODEL_HOT,
    MODEL_MULTI_SCALE_SHRINKAGE,
    MODEL_RANDOM,
    MODEL_REVERSE_PEEK,
    rank_all,
)
from vietlott_quant_lab.ranking.models.controls import (
    INVALID_AS_PREDICTIVE_EVIDENCE,
    reverse_peek,
)
from vietlott_quant_lab.ranking.pools import assert_nested, nested_pools
from vietlott_quant_lab.statistics.metrics import mcp_from_ranking


def test_hot_ranking_is_permutation() -> None:
    history = synthetic_history(100)
    result = rank_all(history, MODEL_HOT, seed=1)
    nums = sorted(r.number for r in result.ranked)
    ranks = sorted(r.rank for r in result.ranked)
    assert nums == list(range(1, 46))
    assert ranks == list(range(1, 46))


def test_top15_subset_top18() -> None:
    history = synthetic_history(100)
    result = rank_all(history, MODEL_MULTI_SCALE_SHRINKAGE, seed=2)
    top15 = set(result.top_m(15))
    top18 = set(result.top_m(18))
    assert top15 <= top18


def test_nested_pools_s7_subset_s18() -> None:
    history = synthetic_history(80)
    result = rank_all(history, MODEL_HOT, seed=0)
    pools = nested_pools(result)
    assert_nested(pools)
    assert pools[7] <= pools[18]


def test_random_seeded_deterministic() -> None:
    history = synthetic_history(30)
    a = rank_all(history, MODEL_RANDOM, seed=42)
    b = rank_all(history, MODEL_RANDOM, seed=42)
    assert [r.number for r in a.by_rank()] == [r.number for r in b.by_rank()]


def test_reverse_peek_full_containment_top6() -> None:
    winners = (3, 9, 14, 22, 31, 40)
    result = reverse_peek(winners, seed=7)
    assert result.label == INVALID_AS_PREDICTIVE_EVIDENCE
    top6 = set(result.top_m(6))
    assert set(winners) <= top6
    mcp = mcp_from_ranking(result.number_to_rank(), winners)
    assert mcp <= 6
    assert 6 <= mcp <= 45


def test_reverse_peek_via_engine() -> None:
    winners = (1, 2, 3, 4, 5, 6)
    history = synthetic_history(10)
    result = rank_all(history, MODEL_REVERSE_PEEK, seed=0, winners=winners)
    assert result.label == INVALID_AS_PREDICTIVE_EVIDENCE
    assert mcp_from_ranking(result.number_to_rank(), winners) <= 6


@given(seed=st.integers(min_value=0, max_value=10_000))
@settings(max_examples=25)
def test_property_ranking_permutation_and_nesting(seed: int) -> None:
    history = synthetic_history(60, seed=seed % 97)
    for model_id in (MODEL_HOT, MODEL_MULTI_SCALE_SHRINKAGE, MODEL_RANDOM):
        result = rank_all(history, model_id, seed=seed)
        assert sorted(r.number for r in result.ranked) == list(range(1, 46))
        assert sorted(r.rank for r in result.ranked) == list(range(1, 46))
        assert set(result.top_m(15)) <= set(result.top_m(18))


@given(
    winners=st.lists(st.integers(1, 45), min_size=6, max_size=6, unique=True).map(
        lambda xs: tuple(sorted(xs))
    ),
    seed=st.integers(0, 1000),
)
@settings(max_examples=20)
def test_property_mcp_in_6_45_after_reverse_peek(
    winners: tuple[int, ...],
    seed: int,
) -> None:
    result = reverse_peek(winners, seed=seed)
    mcp = mcp_from_ranking(result.number_to_rank(), winners)
    assert 6 <= mcp <= 45
    assert mcp <= 6
