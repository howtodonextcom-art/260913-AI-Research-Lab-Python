"""Lightweight Streamlit smoke: import helpers/pages without starting the server."""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PAGE_FILES = sorted((ROOT / "pages").glob("0*.py"))


def test_ui_helpers_import() -> None:
    from vietlott_quant_lab.ui import cache, charts, labels, loaders

    assert labels.DEFAULT_SCIENTIFIC_VERDICT == "NO_RANKING_EDGE_FOUND"
    assert callable(loaders.load_dataset_bundle)
    assert callable(loaders.build_system_health)
    assert callable(charts.compression_frontier_figure)
    assert cache.PROSPECTIVE_CACHE_POLICY == "no_long_lived_cache"
    null = cache.cached_null_tails(18)
    assert null.mean_k == pytest.approx(2.4)


def test_pages_compile() -> None:
    assert len(PAGE_FILES) == 8
    for path in PAGE_FILES:
        source = path.read_text(encoding="utf-8")
        assert "streamlit" in source
        compile(source, str(path), "exec")


def test_app_entrypoint_compiles() -> None:
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    compile(source, "app.py", "exec")
    assert "P11" in source or "Streamlit" in source


def test_loaders_degrade_without_data() -> None:
    from vietlott_quant_lab.ui.loaders import (
        build_system_health,
        latest_tournament_artifact,
        list_experiment_artifacts,
        load_dataset_bundle,
        load_prospective_bundle,
    )

    bundle = load_dataset_bundle()
    assert isinstance(bundle.draws, list)
    assert isinstance(list_experiment_artifacts(), list)
    assert latest_tournament_artifact() is None or isinstance(latest_tournament_artifact(), dict)
    snap = load_prospective_bundle()
    assert snap.chain_ok is True or snap.chain_error
    health = build_system_health(app_version="0.0-test")
    assert health.app_version == "0.0-test"


def test_ui_package_exports() -> None:
    mod = importlib.import_module("vietlott_quant_lab.ui")
    for name in ("labels", "loaders", "charts", "cached_ranking", "PROSPECTIVE_CACHE_POLICY"):
        assert hasattr(mod, name)
