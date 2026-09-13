"""Leak-safe Number Library features (P3)."""

from vietlott_quant_lab.features.leak import assert_no_future_leak
from vietlott_quant_lab.features.vector import (
    NumberFeatureVector,
    build_all_feature_vectors,
    build_feature_vector,
)
from vietlott_quant_lab.features.windows import MULTI_SCALE_WINDOWS

__all__ = [
    "MULTI_SCALE_WINDOWS",
    "NumberFeatureVector",
    "assert_no_future_leak",
    "build_all_feature_vectors",
    "build_feature_vector",
]
