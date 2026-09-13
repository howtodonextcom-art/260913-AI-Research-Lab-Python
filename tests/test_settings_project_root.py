"""Settings / project_root resolution for local and Docker layouts."""

from __future__ import annotations

from pathlib import Path

from vietlott_quant_lab.config.constants import default_project_root
from vietlott_quant_lab.config.settings import Settings, get_settings


def test_default_project_root_points_at_app_py() -> None:
    root = default_project_root()
    assert (root / "app.py").is_file()
    assert (root / "data").is_dir()


def test_project_root_env_override(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("PROJECT_ROOT", str(tmp_path))
    get_settings.cache_clear()
    try:
        settings = Settings()
        assert settings.project_root == tmp_path
        assert settings.data_dir == tmp_path / "data"
    finally:
        get_settings.cache_clear()
