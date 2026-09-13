"""Pydantic draw schema for Mega 6/45 official records."""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from vietlott_quant_lab.config.constants import (
    DRAW_SIZE,
    NUMBER_MAX,
    NUMBER_MIN,
    PRODUCT_MEGA645,
)

_DRAW_ID_RE = re.compile(r"^\d{5}$")


class DrawRecord(BaseModel):
    """Canonical official draw row."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    product: Literal["mega645"] = PRODUCT_MEGA645
    draw_id: str = Field(..., description="Five-digit official draw id, e.g. 00001")
    draw_date: date
    numbers: tuple[int, ...]
    source_url: str
    fetched_at: datetime

    @field_validator("draw_id")
    @classmethod
    def _validate_draw_id(cls, value: str) -> str:
        if not _DRAW_ID_RE.fullmatch(value):
            raise ValueError(f"draw_id must be exactly 5 digits, got {value!r}")
        return value

    @field_validator("numbers")
    @classmethod
    def _validate_numbers_shape(cls, value: tuple[int, ...]) -> tuple[int, ...]:
        if len(value) != DRAW_SIZE:
            raise ValueError(f"expected {DRAW_SIZE} numbers, got {len(value)}")
        if len(set(value)) != DRAW_SIZE:
            raise ValueError("numbers must be unique")
        for n in value:
            if not isinstance(n, int) or isinstance(n, bool):
                raise ValueError(f"number must be int, got {n!r}")
            if n < NUMBER_MIN or n > NUMBER_MAX:
                raise ValueError(f"number out of range [{NUMBER_MIN}, {NUMBER_MAX}]: {n}")
        return tuple(sorted(value))

    @model_validator(mode="after")
    def _ensure_sorted(self) -> DrawRecord:
        # numbers validator already sorts; keep invariant explicit for frozen model.
        if self.numbers != tuple(sorted(self.numbers)):
            raise ValueError("numbers must be sorted ascending")
        return self
