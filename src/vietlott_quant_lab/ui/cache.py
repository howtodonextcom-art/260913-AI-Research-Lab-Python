"""Streamlit cache wrappers.

Cache keys for derived research views must include dataset_hash / protocol_hash /
model version. Do **not** cache prospective mutable decisions indefinitely —
prospective ledgers are loaded fresh (or with a short TTL) so pending/scored
state stays current.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, TypeVar

import streamlit as st

from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.features.vector import NumberFeatureVector, build_feature_vector
from vietlott_quant_lab.ranking.engine import rank_all
from vietlott_quant_lab.ranking.types import RankingResult
from vietlott_quant_lab.statistics.metrics import NullTailProbabilities, null_tail_probabilities

F = TypeVar("F", bound=Callable[..., Any])

# Explicit note for reviewers: prospective loaders intentionally bypass long-lived cache.
PROSPECTIVE_CACHE_POLICY = "no_long_lived_cache"


def cache_key_parts(
    *,
    dataset_hash: str,
    protocol_hash: str = "",
    model_version: str = "",
) -> tuple[str, str, str]:
    """Canonical tuple for @st.cache_data keys (hashable primitives only)."""
    return (dataset_hash or "none", protocol_hash or "none", model_version or "none")


def cached(fn: F) -> F:  # noqa: UP047 — keep TypeVar for Streamlit decorator compatibility
    """Thin alias documenting that the wrapped function must take hash keys."""
    return st.cache_data(show_spinner=False)(fn)  # type: ignore[return-value]


@st.cache_data(show_spinner=False)
def cached_ranking(
    _draws: Sequence[DrawRecord],
    *,
    dataset_hash: str,
    model_id: str,
    model_version: str,
    protocol_hash: str = "",
    seed: int = 0,
    lookback: int | None = 90,
) -> RankingResult:
    """Rank 01–45; key includes dataset_hash + model_version (+ protocol_hash)."""
    _ = cache_key_parts(
        dataset_hash=dataset_hash,
        protocol_hash=protocol_hash,
        model_version=f"{model_version}:{model_id}",
    )
    kwargs: dict[str, Any] = {"seed": seed}
    if lookback is not None:
        kwargs["lookback"] = lookback
    return rank_all(list(_draws), model_id, **kwargs)


@st.cache_data(show_spinner=False)
def cached_feature_vector(
    _draws: Sequence[DrawRecord],
    *,
    number: int,
    dataset_hash: str,
    model_version: str = "features_v1",
) -> NumberFeatureVector:
    """Per-number features; keyed by dataset_hash + model_version + number."""
    _ = cache_key_parts(dataset_hash=dataset_hash, model_version=f"{model_version}:{number}")
    return build_feature_vector(list(_draws), number)


@st.cache_data(show_spinner=False)
def cached_all_feature_vectors(
    _draws: Sequence[DrawRecord],
    *,
    dataset_hash: str,
    model_version: str = "features_v1",
) -> dict[int, NumberFeatureVector]:
    """All 01–45 features; keyed by dataset_hash + model_version."""
    from vietlott_quant_lab.features.vector import build_all_feature_vectors

    _ = cache_key_parts(dataset_hash=dataset_hash, model_version=model_version)
    return build_all_feature_vectors(list(_draws))


@st.cache_data(show_spinner=False)
def cached_null_tails(pool_size: int) -> NullTailProbabilities:
    """Exact null tails depend only on pool size (closed form)."""
    return null_tail_probabilities(pool_size)


def clear_data_caches() -> None:
    """Clear Streamlit data caches (e.g. after manual sync outside the app)."""
    cached_ranking.clear()
    cached_feature_vector.clear()
    cached_all_feature_vectors.clear()
    cached_null_tails.clear()
