"""P4 exact null / bao / multiplicity tests."""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from vietlott_quant_lab.statistics.bao import cost, p6, tickets
from vietlott_quant_lab.statistics.hypergeometric import (
    expected_k,
    hypergeometric_pmf,
    hypergeometric_tail_ge,
    pmf_support,
)
from vietlott_quant_lab.statistics.multiplicity import holm_bonferroni


def test_pmf_sums_to_one_for_m18() -> None:
    total = sum(hypergeometric_pmf(18, k) for k in range(7))
    assert abs(total - 1.0) < 1e-12


def test_expected_k_m18_is_2_4() -> None:
    assert abs(expected_k(18) - 2.4) < 1e-12


def test_tail_ge_matches_sum() -> None:
    m = 18
    for k in range(7):
        expected = sum(hypergeometric_pmf(m, i) for i in range(k, 7))
        assert abs(hypergeometric_tail_ge(m, k) - expected) < 1e-12


def test_bao_identities() -> None:
    from math import comb

    assert tickets(18) == comb(18, 6)
    assert cost(18) == 10_000 * comb(18, 6)
    assert abs(p6(18) - comb(18, 6) / comb(45, 6)) < 1e-15


def test_holm_bonferroni_monotonic() -> None:
    raw = [0.01, 0.04, 0.03, 0.20]
    results = holm_bonferroni(raw, alpha=0.05)
    assert len(results) == 4
    # Adjusted p-values are nondecreasing in the sorted order of raw p.
    order = sorted(range(4), key=lambda i: raw[i])
    adj = [results[i].adjusted_p for i in order]
    assert adj == sorted(adj)


@given(m=st.integers(min_value=0, max_value=45))
@settings(max_examples=40)
def test_property_pmf_sums_approx_one(m: int) -> None:
    total = sum(pmf_support(m).values())
    assert abs(total - 1.0) < 1e-9


@given(m=st.integers(min_value=0, max_value=45))
@settings(max_examples=40)
def test_property_expected_k_formula(m: int) -> None:
    assert abs(expected_k(m) - 6 * m / 45) < 1e-12
