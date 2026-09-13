"""Dataset manifest for canonical Mega 6/45 draws."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from vietlott_quant_lab.config.constants import (
    MANIFEST_FILENAME,
    OFFICIAL_SOURCE_ID,
    PARSER_VERSION,
    PRODUCT_MEGA645,
)
from vietlott_quant_lab.data.schema import DrawRecord

ValidationStatus = Literal["PASS", "FAIL", "UNKNOWN"]


class DatasetManifest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    product: str = PRODUCT_MEGA645
    source: str = OFFICIAL_SOURCE_ID
    parser_version: str = PARSER_VERSION
    record_count: int
    first_draw_id: str | None
    first_draw_date: str | None
    last_draw_id: str | None
    last_draw_date: str | None
    dataset_sha256: str
    last_sync: str
    validation_status: ValidationStatus = "UNKNOWN"


def compute_dataset_sha256(records: list[DrawRecord]) -> str:
    """Stable hash over sorted draw_id + date + numbers (not fetched_at)."""
    lines: list[str] = []
    for r in sorted(records, key=lambda x: x.draw_id):
        nums = ",".join(f"{n:02d}" for n in r.numbers)
        lines.append(f"{r.draw_id}|{r.draw_date.isoformat()}|{nums}")
    payload = "\n".join(lines).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build_manifest(
    records: list[DrawRecord],
    *,
    validation_status: ValidationStatus = "UNKNOWN",
    last_sync: str | None = None,
    parser_version: str = PARSER_VERSION,
    source: str = OFFICIAL_SOURCE_ID,
) -> DatasetManifest:
    ordered = sorted(records, key=lambda r: r.draw_id)
    first = ordered[0] if ordered else None
    last = ordered[-1] if ordered else None
    return DatasetManifest(
        product=PRODUCT_MEGA645,
        source=source,
        parser_version=parser_version,
        record_count=len(ordered),
        first_draw_id=first.draw_id if first else None,
        first_draw_date=first.draw_date.isoformat() if first else None,
        last_draw_id=last.draw_id if last else None,
        last_draw_date=last.draw_date.isoformat() if last else None,
        dataset_sha256=compute_dataset_sha256(ordered),
        last_sync=last_sync or datetime.now(UTC).isoformat(),
        validation_status=validation_status,
    )


def write_manifest(path: Path, manifest: DatasetManifest) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(manifest.model_dump(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def load_manifest(path: Path) -> DatasetManifest | None:
    if not path.exists():
        return None
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return DatasetManifest.model_validate(data)


def default_manifest_path(manifests_dir: Path) -> Path:
    return manifests_dir / MANIFEST_FILENAME


def manifest_as_json(manifest: DatasetManifest) -> str:
    return json.dumps(manifest.model_dump(), ensure_ascii=False, indent=2)
