"""Fail-closed integrity checks for canonical Mega 6/45 draws."""

from __future__ import annotations

from dataclasses import dataclass, field

from vietlott_quant_lab.config.constants import (
    DRAW_SIZE,
    FIRST_DRAW_ID,
    NUMBER_MAX,
    NUMBER_MIN,
)
from vietlott_quant_lab.data.errors import ValidationError
from vietlott_quant_lab.data.schema import DrawRecord


@dataclass
class IntegrityReport:
    ok: bool
    issues: list[str] = field(default_factory=list)

    def raise_if_failed(self) -> None:
        if not self.ok:
            raise ValidationError("; ".join(self.issues) or "integrity check failed")


def validate_draw_numbers(numbers: tuple[int, ...]) -> list[str]:
    issues: list[str] = []
    if len(numbers) != DRAW_SIZE:
        issues.append(f"expected {DRAW_SIZE} numbers, got {len(numbers)}")
    if len(set(numbers)) != len(numbers):
        issues.append("duplicate numbers within draw")
    for n in numbers:
        if n < NUMBER_MIN or n > NUMBER_MAX:
            issues.append(f"number out of range: {n}")
    if numbers != tuple(sorted(numbers)):
        issues.append("numbers are not sorted ascending")
    return issues


def check_integrity(
    records: list[DrawRecord],
    *,
    require_continuity_from_first: bool = True,
) -> IntegrityReport:
    issues: list[str] = []
    if not records:
        if require_continuity_from_first:
            issues.append("empty dataset")
        return IntegrityReport(ok=not issues, issues=issues)

    ordered = sorted(records, key=lambda r: r.draw_id)
    seen_ids: dict[str, DrawRecord] = {}
    seen_dates: dict[str, str] = {}

    for rec in ordered:
        if rec.draw_id in seen_ids:
            issues.append(f"duplicate draw_id {rec.draw_id}")
        seen_ids[rec.draw_id] = rec

        date_key = rec.draw_date.isoformat()
        if date_key in seen_dates and seen_dates[date_key] != rec.draw_id:
            issues.append(
                f"duplicate draw_date {date_key} for ids "
                f"{seen_dates[date_key]} and {rec.draw_id}"
            )
        seen_dates[date_key] = rec.draw_id

        issues.extend(f"{rec.draw_id}: {msg}" for msg in validate_draw_numbers(rec.numbers))

    # Date order must be non-decreasing with draw_id order.
    for prev, curr in zip(ordered, ordered[1:], strict=False):
        if curr.draw_date < prev.draw_date:
            issues.append(
                f"date order violation: {prev.draw_id}@{prev.draw_date} > "
                f"{curr.draw_id}@{curr.draw_date}"
            )

    if require_continuity_from_first:
        ids = [int(r.draw_id) for r in ordered]
        if ordered[0].draw_id != FIRST_DRAW_ID:
            issues.append(f"first draw_id is {ordered[0].draw_id}, expected {FIRST_DRAW_ID}")
        expected = list(range(ids[0], ids[-1] + 1))
        missing = sorted(set(expected) - set(ids))
        if missing:
            sample = ", ".join(f"{m:05d}" for m in missing[:20])
            more = "" if len(missing) <= 20 else f" (+{len(missing) - 20} more)"
            issues.append(f"missing draw ids in continuity: {sample}{more}")

    return IntegrityReport(ok=not issues, issues=issues)
