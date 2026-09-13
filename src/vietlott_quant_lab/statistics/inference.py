"""Dependence-aware inference for walk-forward Mean K (P4).

Primary null remains the exact Hypergeometric expectation. Student-t is retained
as a legacy comparator; Newey–West HAC, moving-block bootstrap, and paired
permutation are preferred for reporting. Do not cherry-pick the method that
produces significance.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy import stats  # type: ignore[import-untyped]


@dataclass(frozen=True)
class InferenceReport:
    """Effect-size-first inference for a mean lift series."""

    method: str
    effect: float
    ci_low: float
    ci_high: float
    raw_p: float
    n: int
    null_value: float
    notes: str = ""

    def summary(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "effect": self.effect,
            "ci_low": self.ci_low,
            "ci_high": self.ci_high,
            "raw_p": self.raw_p,
            "n": self.n,
            "null_value": self.null_value,
            "notes": self.notes,
        }


def absolute_lift(mean_k: float, null_mean: float) -> float:
    return mean_k - null_mean


def relative_lift(mean_k: float, null_mean: float) -> float:
    if abs(null_mean) < 1e-15:
        return 0.0
    return (mean_k - null_mean) / null_mean


def student_t_onesided(
    values: Sequence[float],
    *,
    null_value: float,
) -> InferenceReport:
    """Legacy one-sided Student t (H1: mean > null). Not dependence-aware."""
    arr = np.asarray(values, dtype=float)
    n = int(arr.size)
    if n < 2:
        return InferenceReport(
            method="student_t",
            effect=float(arr.mean()) - null_value if n else 0.0,
            ci_low=float("nan"),
            ci_high=float("nan"),
            raw_p=1.0,
            n=n,
            null_value=null_value,
            notes="insufficient_n",
        )
    mean = float(arr.mean())
    effect = mean - null_value
    if float(arr.max()) == float(arr.min()):
        p = 0.0 if effect > 0 else 1.0
        return InferenceReport(
            method="student_t",
            effect=effect,
            ci_low=effect,
            ci_high=effect,
            raw_p=p,
            n=n,
            null_value=null_value,
            notes="constant_series",
        )
    result = stats.ttest_1samp(arr, null_value, alternative="greater")
    p = float(result.pvalue)
    if p != p:
        p = 1.0 if effect <= 0 else 0.0
    se = float(arr.std(ddof=1) / np.sqrt(n))
    tcrit = float(stats.t.ppf(0.975, n - 1))
    return InferenceReport(
        method="student_t",
        effect=effect,
        ci_low=effect - tcrit * se,
        ci_high=effect + tcrit * se,
        raw_p=min(1.0, max(0.0, p)),
        n=n,
        null_value=null_value,
        notes="assumes_iid",
    )


def newey_west_onesided(
    values: Sequence[float],
    *,
    null_value: float,
    max_lag: int | None = None,
) -> InferenceReport:
    """One-sided Newey–West HAC test for H1: E[x] > null_value."""
    arr = np.asarray(values, dtype=float)
    n = int(arr.size)
    if n < 2:
        return InferenceReport(
            method="newey_west_hac",
            effect=float(arr.mean()) - null_value if n else 0.0,
            ci_low=float("nan"),
            ci_high=float("nan"),
            raw_p=1.0,
            n=n,
            null_value=null_value,
            notes="insufficient_n",
        )
    mean = float(arr.mean())
    effect = mean - null_value
    centered = arr - mean
    if max_lag is None:
        # Common rule of thumb: floor(n^{1/4}) or floor(4*(n/100)^{2/9}).
        max_lag = max(1, int(np.floor(4.0 * (n / 100.0) ** (2.0 / 9.0))))
    max_lag = min(max_lag, n - 1)
    gamma0 = float(np.dot(centered, centered) / n)
    nw_var = gamma0
    for lag in range(1, max_lag + 1):
        weight = 1.0 - lag / (max_lag + 1.0)
        gamma = float(np.dot(centered[lag:], centered[:-lag]) / n)
        nw_var += 2.0 * weight * gamma
    nw_var = max(nw_var, 0.0)
    se = float(np.sqrt(nw_var / n)) if nw_var > 0 else 0.0
    if se <= 0:
        p = 0.0 if effect > 0 else 1.0
        return InferenceReport(
            method="newey_west_hac",
            effect=effect,
            ci_low=effect,
            ci_high=effect,
            raw_p=p,
            n=n,
            null_value=null_value,
            notes=f"max_lag={max_lag};zero_se",
        )
    z = effect / se
    p = float(1.0 - stats.norm.cdf(z))
    zcrit = float(stats.norm.ppf(0.975))
    return InferenceReport(
        method="newey_west_hac",
        effect=effect,
        ci_low=effect - zcrit * se,
        ci_high=effect + zcrit * se,
        raw_p=min(1.0, max(0.0, p)),
        n=n,
        null_value=null_value,
        notes=f"max_lag={max_lag}",
    )


def moving_block_bootstrap_ci(
    values: Sequence[float],
    *,
    null_value: float,
    block_size: int | None = None,
    n_boot: int = 999,
    seed: int = 0,
    alpha: float = 0.05,
) -> InferenceReport:
    """One-sided block-bootstrap p for H1: mean > null; percentile CI for lift."""
    arr = np.asarray(values, dtype=float)
    n = int(arr.size)
    if n < 2:
        return InferenceReport(
            method="moving_block_bootstrap",
            effect=float(arr.mean()) - null_value if n else 0.0,
            ci_low=float("nan"),
            ci_high=float("nan"),
            raw_p=1.0,
            n=n,
            null_value=null_value,
            notes="insufficient_n",
        )
    if block_size is None:
        block_size = max(2, int(np.floor(n ** (1.0 / 3.0))))
    block_size = min(max(1, block_size), n)
    rng = np.random.default_rng(seed)
    observed = float(arr.mean()) - null_value
    centered = arr - float(arr.mean()) + null_value  # under H0: mean = null
    boots: list[float] = []
    n_blocks = int(np.ceil(n / block_size))
    for _ in range(n_boot):
        starts = rng.integers(0, n, size=n_blocks)
        pieces: list[np.ndarray] = []
        for s in starts:
            end = s + block_size
            if end <= n:
                pieces.append(centered[s:end])
            else:
                pieces.append(np.concatenate([centered[s:], centered[: end - n]]))
        sample = np.concatenate(pieces)[:n]
        boots.append(float(sample.mean()) - null_value)
    boots_arr = np.asarray(boots, dtype=float)
    # One-sided: proportion of bootstrap lifts under H0 >= observed lift.
    raw_p = float((np.sum(boots_arr >= observed) + 1.0) / (n_boot + 1.0))
    # Percentile CI on observed series lifts (not under H0).
    obs_boots: list[float] = []
    for _ in range(n_boot):
        starts = rng.integers(0, n, size=n_blocks)
        pieces = []
        for s in starts:
            end = s + block_size
            if end <= n:
                pieces.append(arr[s:end])
            else:
                pieces.append(np.concatenate([arr[s:], arr[: end - n]]))
        sample = np.concatenate(pieces)[:n]
        obs_boots.append(float(sample.mean()) - null_value)
    lo = float(np.quantile(obs_boots, alpha / 2.0))
    hi = float(np.quantile(obs_boots, 1.0 - alpha / 2.0))
    return InferenceReport(
        method="moving_block_bootstrap",
        effect=observed,
        ci_low=lo,
        ci_high=hi,
        raw_p=min(1.0, max(0.0, raw_p)),
        n=n,
        null_value=null_value,
        notes=f"block_size={block_size};n_boot={n_boot}",
    )


def paired_permutation_pvalue(
    a: Sequence[float],
    b: Sequence[float],
    *,
    n_perm: int = 1999,
    seed: int = 0,
) -> InferenceReport:
    """One-sided paired permutation test H1: mean(a-b) > 0 (sign-flip)."""
    aa = np.asarray(a, dtype=float)
    bb = np.asarray(b, dtype=float)
    if aa.size != bb.size:
        msg = "paired series must have equal length"
        raise ValueError(msg)
    n = int(aa.size)
    diff = aa - bb
    if n < 1:
        return InferenceReport(
            method="paired_permutation",
            effect=0.0,
            ci_low=float("nan"),
            ci_high=float("nan"),
            raw_p=1.0,
            n=0,
            null_value=0.0,
            notes="empty",
        )
    observed = float(diff.mean())
    rng = np.random.default_rng(seed)
    count = 0
    for _ in range(n_perm):
        signs = rng.choice(np.array([-1.0, 1.0]), size=n)
        if float((diff * signs).mean()) >= observed:
            count += 1
    raw_p = (count + 1.0) / (n_perm + 1.0)
    # Simple percentile CI via additional sign-flip of centered diffs is omitted;
    # report effect with bootstrap-of-diff CI using same signs pool.
    boots = []
    for _ in range(min(999, n_perm)):
        idx = rng.integers(0, n, size=n)
        boots.append(float(diff[idx].mean()))
    lo = float(np.quantile(boots, 0.025))
    hi = float(np.quantile(boots, 0.975))
    return InferenceReport(
        method="paired_permutation",
        effect=observed,
        ci_low=lo,
        ci_high=hi,
        raw_p=min(1.0, max(0.0, float(raw_p))),
        n=n,
        null_value=0.0,
        notes=f"n_perm={n_perm}",
    )


def primary_inference_bundle(
    ks: Sequence[float],
    *,
    null_mean: float,
    seed: int = 0,
) -> dict[str, Any]:
    """Report all registered methods; HAC is the preferred dependence-aware primary."""
    student = student_t_onesided(ks, null_value=null_mean)
    hac = newey_west_onesided(ks, null_value=null_mean)
    boot = moving_block_bootstrap_ci(ks, null_value=null_mean, seed=seed)
    mean_val = float(np.mean(ks)) if len(ks) else 0.0
    return {
        "absolute_lift": absolute_lift(mean_val, null_mean),
        "relative_lift": relative_lift(mean_val, null_mean),
        "primary_method": "newey_west_hac",
        "student_t": student.summary(),
        "newey_west_hac": hac.summary(),
        "moving_block_bootstrap": boot.summary(),
        "primary_raw_p": hac.raw_p,
        "primary_ci": [hac.ci_low, hac.ci_high],
        "primary_effect": hac.effect,
    }
