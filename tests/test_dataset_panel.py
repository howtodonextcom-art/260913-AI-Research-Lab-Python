"""Dataset status panel helpers (last date + update affordance)."""

from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path

from vietlott_quant_lab.config.settings import Settings, get_settings
from vietlott_quant_lab.data.manifest import DatasetManifest
from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.ui import labels
from vietlott_quant_lab.ui.dataset_panel import format_dataset_headline
from vietlott_quant_lab.ui.loaders import DatasetBundle


def test_format_dataset_headline_includes_date_and_id() -> None:
    draw = DrawRecord(
        draw_id="01562",
        draw_date=date(2026, 9, 13),
        numbers=(1, 2, 3, 4, 5, 6),
        source_url="https://vietlott.vn/x",
        fetched_at=datetime(2026, 9, 13, tzinfo=UTC),
    )
    bundle = DatasetBundle(
        draws=[draw],
        manifest=DatasetManifest(
            product="mega645",
            source="vietlott-official",
            parser_version="1.0.0",
            record_count=1,
            first_draw_id="01562",
            first_draw_date="2026-09-13",
            last_draw_id="01562",
            last_draw_date="2026-09-13",
            dataset_sha256="abc123def4567890",
            last_sync="2026-09-13T16:16:27+00:00",
            validation_status="PASS",
        ),
        dataset_hash="abc123def4567890",
        parquet_path=Path("."),
        manifest_path=Path("."),
    )
    text = format_dataset_headline(bundle)
    assert "2026-09-13" in text
    assert "#01562" in text
    assert "abc123def456" in text


def test_format_empty_dataset() -> None:
    bundle = DatasetBundle(
        draws=[],
        manifest=None,
        dataset_hash="",
        parquet_path=Path("."),
        manifest_path=Path("."),
    )
    assert format_dataset_headline(bundle) == labels.DATASET_BANNER_EMPTY


def test_update_labels_visible_in_copy() -> None:
    assert labels.UPDATE_DATA == "Cập nhật dữ liệu"
    assert labels.LAST_DRAW_DATE == "Ngày dữ liệu cuối"


def test_live_fetch_env_gate(monkeypatch) -> None:
    monkeypatch.setenv("VIETLOTT_ALLOW_LIVE_FETCH", "0")
    get_settings.cache_clear()
    try:
        assert Settings().vietlott_allow_live_fetch is False
    finally:
        get_settings.cache_clear()


def test_app_mentions_update_control() -> None:
    source = (Path(__file__).resolve().parents[1] / "app.py").read_text(encoding="utf-8")
    assert "render_dataset_status_panel" in source
    assert labels.UPDATE_DATA == "Cập nhật dữ liệu"
