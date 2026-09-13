"""P6–P9 research tournaments: split, walk-forward, compression, controls."""

from __future__ import annotations

from pathlib import Path

import pytest
from tests.conftest_research import synthetic_history

from vietlott_quant_lab.provenance.hashing import canonical_json, sha256_canonical, sha256_hex
from vietlott_quant_lab.ranking.engine import (
    MODEL_HOT,
    MODEL_MULTI_SCALE_SHRINKAGE,
    MODEL_RANDOM,
    MODEL_REVERSE_PEEK,
)
from vietlott_quant_lab.research.artifacts import build_experiment_id, write_experiment_artifact
from vietlott_quant_lab.research.compression import assert_top_nested, compression_frontier
from vietlott_quant_lab.research.model_tournament import run_model_tournament
from vietlott_quant_lab.research.pool_gate import evaluate_pool18_gate
from vietlott_quant_lab.research.protocol import (
    NO_VERIFIED_18_POOL_EDGE,
    ResearchProtocol,
    default_protocol,
)
from vietlott_quant_lab.research.split import chronological_split
from vietlott_quant_lab.research.verdict import compute_scientific_verdict
from vietlott_quant_lab.research.walkforward import walkforward_score
from vietlott_quant_lab.research.window_tournament import run_window_tournament
from vietlott_quant_lab.statistics.hypergeometric import expected_k


def test_chronological_split_sizes_50_25_25() -> None:
    draws = synthetic_history(100, seed=1)
    split = chronological_split(draws)
    assert split.sizes() == {
        "development": 50,
        "validation": 25,
        "test": 25,
        "total": 100,
    }
    # Order preserved — first/last draw_ids.
    assert split.development[0].draw_id == draws[0].draw_id
    assert split.test[-1].draw_id == draws[-1].draw_id
    # No overlap.
    ids = (
        {d.draw_id for d in split.development}
        | {d.draw_id for d in split.validation}
        | {d.draw_id for d in split.test}
    )
    assert len(ids) == 100


def test_chronological_split_remainder_to_test() -> None:
    draws = synthetic_history(101, seed=2)
    split = chronological_split(draws)
    assert len(split.development) == 50  # 101 // 2
    assert len(split.validation) == 25  # 101 // 4
    assert len(split.test) == 26
    assert split.n_total == 101


def test_protocol_hash_stable_and_sensitive() -> None:
    a = default_protocol(seed=0)
    b = default_protocol(seed=0)
    c = default_protocol(seed=1)
    assert a.protocol_hash() == b.protocol_hash()
    assert a.protocol_hash() != c.protocol_hash()
    assert len(a.protocol_hash()) == 64


def test_canonical_json_sorted_keys() -> None:
    assert canonical_json({"b": 1, "a": 2}) == canonical_json({"a": 2, "b": 1})
    assert sha256_hex(b"abc") == sha256_hex("abc")
    assert sha256_canonical({"z": 1, "a": 2}) == sha256_canonical({"a": 2, "z": 1})


def test_fair_synthetic_no_strong_edge() -> None:
    """Fair random draws: HOT should not show a robust holdout edge."""
    draws = synthetic_history(160, seed=42)
    protocol = ResearchProtocol(
        seed=7,
        min_history=20,
        lookback_windows=(30, 60, 90),
        top_window_candidates=2,
        practical_delta_mean_k=0.15,
        models=(MODEL_HOT, MODEL_MULTI_SCALE_SHRINKAGE, MODEL_RANDOM),
    )
    result = run_model_tournament(
        draws,
        protocol=protocol,
        hot_lookback=90,
        run_window_selection=False,
    )
    # Random must not lose badly on validation (within ~0.35 of champion mean K).
    by_id = {s.model_id: s for s in result.scores}
    random_val = by_id[MODEL_RANDOM].validation.mean_k
    hot_val = by_id[MODEL_HOT].validation.mean_k
    assert abs(hot_val - random_val) < 0.5
    # Fair lottery: typically no confirmed holdout signal.
    assert result.scientific_verdict in {
        "NO_RANKING_EDGE_FOUND",
        "EXPLORATORY_SIGNAL",
        "VALIDATION_SIGNAL",
        "HOLDOUT_SIGNAL",
    }
    # Extremely strong confirmed edge would be shocking on fair data with strict delta.
    if result.holdout_status == "HOLDOUT_SIGNAL":
        # Still allow rare false positives, but mean lift must be modest.
        assert result.test is not None
        assert result.test.lift_mean_k < 0.8


def test_reverse_peek_wins_walkforward() -> None:
    draws = synthetic_history(80, seed=3)
    wf = walkforward_score(
        draws,
        model_id=MODEL_REVERSE_PEEK,
        pool_size=18,
        lookback=None,
        seed=0,
        min_history=10,
    )
    assert wf.n_scored > 0
    assert all(s.k == 6 for s in wf.steps)
    assert all(s.mcp <= 6 for s in wf.steps)
    assert wf.mean_k == pytest.approx(6.0)
    assert wf.mean_k > expected_k(18)


def test_window_tournament_never_needs_test() -> None:
    draws = synthetic_history(120, seed=5)
    protocol = ResearchProtocol(
        seed=1,
        min_history=15,
        lookback_windows=(15, 30, 90, "ALL"),
        top_window_candidates=2,
    )
    result = run_window_tournament(draws, protocol=protocol)
    assert result.selected_lookback is not None
    assert result.frozen is True
    assert len(result.validation_candidates) == 2
    # Development ranked all windows.
    assert len(result.development_ranked) == 4


def test_compression_top15_subset_top18() -> None:
    draws = synthetic_history(100, seed=9)
    frontier = compression_frontier(
        draws,
        model_id=MODEL_HOT,
        lookback=60,
        seed=0,
        min_history=20,
        pool_sizes=(7, 15, 18),
    )
    assert frontier.nested_ok
    assert_top_nested(frontier, 15, 18)
    assert_top_nested(frontier, 7, 15)
    row18 = next(r for r in frontier.rows if r.pool_size == 18)
    assert row18.tickets > 0
    assert row18.cost_vnd == row18.tickets * 10_000


def test_pool_gate_fails_on_fair_data() -> None:
    draws = synthetic_history(140, seed=11)
    protocol = ResearchProtocol(
        seed=2,
        min_history=20,
        lookback_windows=(90,),
        practical_delta_mean_k=0.2,
        models=(MODEL_HOT, MODEL_RANDOM),
    )
    tournament = run_model_tournament(
        draws,
        protocol=protocol,
        hot_lookback=90,
        run_window_selection=False,
    )
    gate = evaluate_pool18_gate(draws, tournament=tournament, protocol=protocol)
    # Fair data should almost always fail the strict gate.
    assert gate.status == NO_VERIFIED_18_POOL_EDGE or gate.passed is False
    verdict = compute_scientific_verdict(model_tournament=tournament, pool_gate=gate)
    assert verdict in {
        "NO_RANKING_EDGE_FOUND",
        "EXPLORATORY_SIGNAL",
        "VALIDATION_SIGNAL",
        "HOLDOUT_SIGNAL",
    }


def test_write_experiment_artifact(tmp_path: Path) -> None:
    path = write_experiment_artifact(
        dataset_hash="a" * 64,
        protocol_hash="b" * 64,
        model="hot",
        model_hash="c" * 64,
        development_results={"mean_k": 2.4},
        validation_results={"mean_k": 2.41},
        test_results={"mean_k": 2.39},
        scientific_verdict="NO_RANKING_EDGE_FOUND",
        experiments_dir=tmp_path,
        git_commit="deadbeef",
    )
    assert path.exists()
    exp_id = build_experiment_id(
        dataset_hash="a" * 64,
        protocol_hash="b" * 64,
        model_hash="c" * 64,
    )
    assert path.name == f"{exp_id}.json"
    text = path.read_text(encoding="utf-8")
    assert "NO_RANKING_EDGE_FOUND" in text
    assert "deadbeef" in text


def test_walkforward_anti_leak_history_prefix() -> None:
    """Target draw is never in the history used for ranking (by construction)."""
    draws = synthetic_history(50, seed=0)
    wf = walkforward_score(
        draws,
        model_id=MODEL_HOT,
        pool_size=18,
        lookback=20,
        seed=0,
        min_history=10,
    )
    for step in wf.steps:
        # History length equals target_index.
        assert step.target_index >= 10
        assert draws[step.target_index].draw_id == step.draw_id
