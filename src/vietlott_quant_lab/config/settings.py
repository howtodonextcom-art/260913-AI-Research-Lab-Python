"""Pydantic Settings for environment-backed configuration."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from vietlott_quant_lab.config.constants import (
    ARTIFACTS_DIR_NAME,
    DATA_DIR_NAME,
    EXPERIMENTS_DIR_NAME,
    MANIFESTS_DIR_NAME,
    PROCESSED_DIR_NAME,
    PRODUCT_MEGA645,
    PROSPECTIVE_DIR_NAME,
    RAW_DIR_NAME,
    REPORTS_DIR_NAME,
    SNAPSHOTS_DIR_NAME,
    default_project_root,
)


class Settings(BaseSettings):
    """Runtime settings loaded from environment / `.env`."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    project_root: Path = Field(default_factory=default_project_root)
    product: str = PRODUCT_MEGA645
    log_level: str = "INFO"
    http_timeout_seconds: float = 30.0
    http_request_delay_ms: int = 400
    # When false, UI still shows "Cập nhật dữ liệu" but refuses live crawl (CLI only).
    vietlott_allow_live_fetch: bool = True

    @property
    def data_dir(self) -> Path:
        return self.project_root / DATA_DIR_NAME

    @property
    def raw_dir(self) -> Path:
        return self.data_dir / RAW_DIR_NAME

    @property
    def processed_dir(self) -> Path:
        return self.data_dir / PROCESSED_DIR_NAME

    @property
    def snapshots_dir(self) -> Path:
        return self.data_dir / SNAPSHOTS_DIR_NAME

    @property
    def manifests_dir(self) -> Path:
        return self.data_dir / MANIFESTS_DIR_NAME

    @property
    def artifacts_dir(self) -> Path:
        return self.project_root / ARTIFACTS_DIR_NAME

    @property
    def experiments_dir(self) -> Path:
        return self.artifacts_dir / EXPERIMENTS_DIR_NAME

    @property
    def prospective_dir(self) -> Path:
        return self.artifacts_dir / PROSPECTIVE_DIR_NAME

    @property
    def reports_dir(self) -> Path:
        return self.artifacts_dir / REPORTS_DIR_NAME


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
