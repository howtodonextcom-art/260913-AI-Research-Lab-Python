"""Chronological Development / Validation / Test split (never shuffle)."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from vietlott_quant_lab.data.schema import DrawRecord
from vietlott_quant_lab.research.protocol import ResearchProtocol, default_protocol


@dataclass(frozen=True)
class ChronologicalSplit:
    """Ordered slices of draws — Development → Validation → Test."""

    development: tuple[DrawRecord, ...]
    validation: tuple[DrawRecord, ...]
    test: tuple[DrawRecord, ...]

    @property
    def n_total(self) -> int:
        return len(self.development) + len(self.validation) + len(self.test)

    def sizes(self) -> dict[str, int]:
        return {
            "development": len(self.development),
            "validation": len(self.validation),
            "test": len(self.test),
            "total": self.n_total,
        }


def chronological_split(
    draws: Sequence[DrawRecord],
    *,
    protocol: ResearchProtocol | None = None,
) -> ChronologicalSplit:
    """Split draws chronologically into 50% / 25% / 25% (no shuffle).

    Remainder after floor(50%) and floor(25%) goes to Test so lengths sum to ``n``.
    """
    proto = protocol or default_protocol()
    if proto.split_rule != "chronological_50_25_25":
        msg = f"unsupported split_rule: {proto.split_rule!r}"
        raise ValueError(msg)

    ordered = tuple(draws)
    n = len(ordered)
    if n == 0:
        return ChronologicalSplit(development=(), validation=(), test=())

    n_dev = int(n * proto.development_fraction)
    n_val = int(n * proto.validation_fraction)
    # Prefer exact 50/25/25 via integer halves when fractions are defaults.
    if (
        proto.development_fraction == 0.50
        and proto.validation_fraction == 0.25
        and proto.test_fraction == 0.25
    ):
        n_dev = n // 2
        n_val = n // 4
    n_test = n - n_dev - n_val
    if n_test < 0:
        msg = f"split fractions exceed n={n}"
        raise ValueError(msg)

    development = ordered[:n_dev]
    validation = ordered[n_dev : n_dev + n_val]
    test = ordered[n_dev + n_val :]
    return ChronologicalSplit(
        development=development,
        validation=validation,
        test=test,
    )
