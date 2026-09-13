"""Canonical Parquet draws + DuckDB sync state / manifests."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any, cast

import duckdb
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from vietlott_quant_lab.config.constants import (
    CANONICAL_DRAWS_FILENAME,
    PRODUCT_MEGA645,
    SYNC_STATE_DB_FILENAME,
)
from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.observability.logging import get_logger, log_event

logger = get_logger(__name__)


def draws_to_dataframe(records: list[DrawRecord]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for r in records:
        rows.append(
            {
                "product": r.product,
                "draw_id": r.draw_id,
                "draw_date": r.draw_date.isoformat(),
                "n1": r.numbers[0],
                "n2": r.numbers[1],
                "n3": r.numbers[2],
                "n4": r.numbers[3],
                "n5": r.numbers[4],
                "n6": r.numbers[5],
                "source_url": r.source_url,
                "fetched_at": r.fetched_at.isoformat(),
            }
        )
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(["draw_id"]).reset_index(drop=True)
    return df


def dataframe_to_draws(df: pd.DataFrame) -> list[DrawRecord]:
    records: list[DrawRecord] = []
    for row in df.itertuples(index=False):
        fetched_raw = str(row.fetched_at)
        fetched_at = datetime.fromisoformat(fetched_raw.replace("Z", "+00:00"))
        records.append(
            DrawRecord(
                product=PRODUCT_MEGA645,
                draw_id=str(row.draw_id).zfill(5),
                draw_date=date.fromisoformat(str(row.draw_date)[:10]),
                numbers=(
                    int(cast(int, row.n1)),
                    int(cast(int, row.n2)),
                    int(cast(int, row.n3)),
                    int(cast(int, row.n4)),
                    int(cast(int, row.n5)),
                    int(cast(int, row.n6)),
                ),
                source_url=str(row.source_url),
                fetched_at=fetched_at,
            )
        )
    return records


def write_canonical_parquet(path: Path, records: list[DrawRecord]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    df = draws_to_dataframe(records)
    table = pa.Table.from_pandas(df, preserve_index=False)
    pq.write_table(table, path)
    log_event(logger, "canonical_parquet_written", path=str(path), rows=len(records))
    return path


def load_canonical_parquet(path: Path) -> list[DrawRecord]:
    if not path.exists():
        return []
    table = pq.read_table(path)
    df = table.to_pandas()
    return dataframe_to_draws(df)


def default_canonical_path(processed_dir: Path) -> Path:
    return processed_dir / CANONICAL_DRAWS_FILENAME


def default_sync_db_path(manifests_dir: Path) -> Path:
    return manifests_dir / SYNC_STATE_DB_FILENAME


class SyncStateStore:
    """DuckDB-backed sync cursor and sync run log."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = duckdb.connect(str(self.db_path))
        self._init_schema()

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> SyncStateStore:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _init_schema(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sync_cursor (
                product VARCHAR PRIMARY KEY,
                latest_draw_id VARCHAR,
                latest_draw_date VARCHAR,
                last_sync_at VARCHAR,
                dataset_sha256 VARCHAR
            )
            """
        )
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sync_runs (
                run_id VARCHAR PRIMARY KEY,
                started_at VARCHAR,
                finished_at VARCHAR,
                mode VARCHAR,
                records_fetched INTEGER,
                status VARCHAR,
                message VARCHAR
            )
            """
        )
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS manifests (
                product VARCHAR PRIMARY KEY,
                manifest_json VARCHAR,
                updated_at VARCHAR
            )
            """
        )

    def get_latest_draw_id(self, product: str = PRODUCT_MEGA645) -> str | None:
        row = self._conn.execute(
            "SELECT latest_draw_id FROM sync_cursor WHERE product = ?",
            [product],
        ).fetchone()
        return str(row[0]) if row and row[0] else None

    def upsert_cursor(
        self,
        *,
        latest_draw_id: str,
        latest_draw_date: str,
        dataset_sha256: str,
        product: str = PRODUCT_MEGA645,
        last_sync_at: str | None = None,
    ) -> None:
        ts = last_sync_at or datetime.now().astimezone().isoformat()
        self._conn.execute(
            """
            INSERT INTO sync_cursor AS t
                (product, latest_draw_id, latest_draw_date, last_sync_at, dataset_sha256)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT (product) DO UPDATE SET
                latest_draw_id = excluded.latest_draw_id,
                latest_draw_date = excluded.latest_draw_date,
                last_sync_at = excluded.last_sync_at,
                dataset_sha256 = excluded.dataset_sha256
            """,
            [product, latest_draw_id, latest_draw_date, ts, dataset_sha256],
        )

    def record_run(
        self,
        *,
        run_id: str,
        started_at: str,
        finished_at: str,
        mode: str,
        records_fetched: int,
        status: str,
        message: str = "",
    ) -> None:
        self._conn.execute(
            """
            INSERT INTO sync_runs
                (run_id, started_at, finished_at, mode, records_fetched, status, message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [run_id, started_at, finished_at, mode, records_fetched, status, message],
        )

    def save_manifest_json(self, manifest_json: str, *, product: str = PRODUCT_MEGA645) -> None:
        ts = datetime.now().astimezone().isoformat()
        self._conn.execute(
            """
            INSERT INTO manifests AS t (product, manifest_json, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT (product) DO UPDATE SET
                manifest_json = excluded.manifest_json,
                updated_at = excluded.updated_at
            """,
            [product, manifest_json, ts],
        )
