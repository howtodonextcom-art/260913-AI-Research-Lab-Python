"""Exact null model, metrics, multiplicity, and dependence-aware inference (P4)."""

from vietlott_quant_lab.statistics.bao import cost, p6, tickets
from vietlott_quant_lab.statistics.hypergeometric import (
    expected_k,
    hypergeometric_pmf,
    hypergeometric_tail_ge,
    pmf_support,
)
from vietlott_quant_lab.statistics.inference import (
    InferenceReport,
    absolute_lift,
    moving_block_bootstrap_ci,
    newey_west_onesided,
    paired_permutation_pvalue,
    primary_inference_bundle,
    relative_lift,
    student_t_onesided,
)
from vietlott_quant_lab.statistics.metrics import (
    NullTailProbabilities,
    intersection_k,
    max_winner_rank,
    mcp_from_ranking,
    mcp_le_rate,
    mean_k,
    mean_winner_rank,
    median_winner_rank,
    null_tail_probabilities,
    winner_ranks,
)
from vietlott_quant_lab.statistics.multiplicity import HolmResult, holm_bonferroni

__all__ = [
    "HolmResult",
    "InferenceReport",
    "NullTailProbabilities",
    "absolute_lift",
    "cost",
    "expected_k",
    "holm_bonferroni",
    "hypergeometric_pmf",
    "hypergeometric_tail_ge",
    "intersection_k",
    "max_winner_rank",
    "mcp_from_ranking",
    "mcp_le_rate",
    "mean_k",
    "mean_winner_rank",
    "median_winner_rank",
    "moving_block_bootstrap_ci",
    "newey_west_onesided",
    "null_tail_probabilities",
    "p6",
    "paired_permutation_pvalue",
    "pmf_support",
    "primary_inference_bundle",
    "relative_lift",
    "student_t_onesided",
    "tickets",
    "winner_ranks",
]
