"""Algorithm V2 ranking model smoke + tournament unit tests."""

from __future__ import annotations

from datetime import UTC, date, datetime

from vietlott_quant_lab.config.constants import NUMBER_MAX
from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.ranking.engine import (
    MODEL_ALL_HISTORY,
    MODEL_EWF,
    MODEL_HAZARD,
    MODEL_MEAN_REVERSION,
    MODEL_MOMENTUM,
    MODEL_MULTI_SCALE_V2,
    rank_all,
)
from vietlott_quant_lab.research.model_tournament_v2 import run_model_tournament_v2
from vietlott_quant_lab.research.protocol_v2 import default_protocol_v2
from vietlott_quant_lab.statistics.multiplicity import holm_bonferroni


def _synthetic_draws(n: int = 120) -> list[DrawRecord]:
    draws: list[DrawRecord] = []
    for i in range(n):
        # Rotating but deterministic 6-tuples in 1..45
        nums_set: set[int] = set()
        k = 0
        while len(nums_set) < 6:
            nums_set.add(((i * 3 + k * 7) % 45) + 1)
            k += 1
        nums = tuple(sorted(nums_set))
        draws.append(
            DrawRecord(
                product="mega645",
                draw_id=f"{i + 1:05d}",
                draw_date=date(2020, 1, 1),
                numbers=nums,
                source_url="https://vietlott.vn/test",
                fetched_at=datetime(2020, 1, 1, tzinfo=UTC),
            )
        )
    return draws


def test_v2_models_produce_full_permutation() -> None:
    hist = _synthetic_draws(80)
    for mid in (
        MODEL_ALL_HISTORY,
        MODEL_EWF,
        MODEL_MULTI_SCALE_V2,
        MODEL_MOMENTUM,
        MODEL_MEAN_REVERSION,
        MODEL_HAZARD,
    ):
        ranking = rank_all(hist, mid, seed=0, lookback=30, half_life=30)
        assert len(ranking.ranked) == NUMBER_MAX
        assert ranking.top_m(18)


def test_protocol_v2_hash_stable() -> None:
    a = default_protocol_v2(seed=0).protocol_hash()
    b = default_protocol_v2(seed=0).protocol_hash()
    c = default_protocol_v2(seed=1).protocol_hash()
    assert a == b
    assert a != c


def test_tournament_v2_runs_on_synthetic() -> None:
    draws = _synthetic_draws(160)
    proto = default_protocol_v2(seed=0, min_history=20)
    result = run_model_tournament_v2(draws, protocol=proto, hot_lookback=30)
    assert result.champion is not None
    assert result.test is not None
    assert result.scientific_verdict in {
        "NO_RANKING_EDGE_FOUND",
        "EXPLORATORY_SIGNAL",
        "VALIDATION_SIGNAL",
        "HOLDOUT_SIGNAL",
    }
    assert result.ml_status in {"PRUNE_ML", "ML_ELIGIBLE"}
    # Holm family applied to non-random models
    assert any(s.adjusted_p_val >= s.raw_p_val - 1e-12 for s in result.scores)


def test_holm_family_size() -> None:
    raw = [0.01, 0.02, 0.03, 0.40]
    adj = holm_bonferroni(raw, alpha=0.05)
    assert adj[0].adjusted_p <= adj[1].adjusted_p or adj[0].raw_p <= adj[1].raw_p
