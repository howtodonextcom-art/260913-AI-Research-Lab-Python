"""Helpers for research-core tests."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from vietlott_quant_lab.data.schema import DrawRecord


def make_draw(
    draw_id: str,
    draw_date: date,
    numbers: tuple[int, int, int, int, int, int],
) -> DrawRecord:
    return DrawRecord(
        product="mega645",
        draw_id=draw_id,
        draw_date=draw_date,
        numbers=numbers,
        source_url="https://vietlott.vn/test",
        fetched_at=datetime(2020, 1, 1, tzinfo=UTC),
    )


def synthetic_history(n: int = 120, *, seed: int = 0) -> list[DrawRecord]:
    """Deterministic fair-ish synthetic history for unit tests."""
    import random

    rng = random.Random(seed)
    base = date(2016, 7, 20)
    out: list[DrawRecord] = []
    for i in range(n):
        nums = tuple(sorted(rng.sample(range(1, 46), 6)))
        out.append(
            make_draw(
                f"{i + 1:05d}",
                base + timedelta(days=i * 3),
                nums,  # type: ignore[arg-type]
            )
        )
    return out
