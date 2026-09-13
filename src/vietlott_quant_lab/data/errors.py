"""Data-layer exception hierarchy."""

from __future__ import annotations


class DataLayerError(Exception):
    """Base class for ingest / storage failures."""


class FetchError(DataLayerError):
    """HTTP or network failure talking to the official source."""


class SourceSchemaChangedError(DataLayerError):
    """Official HTML/JSON shape no longer matches expected parsers.

    Code ``SOURCE_SCHEMA_CHANGED`` must never be treated as EOF.
    """

    code: str = "SOURCE_SCHEMA_CHANGED"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ValidationError(DataLayerError):
    """A draw or dataset violates Mega 6/45 / continuity invariants."""


class MergeConflictError(DataLayerError):
    """Same draw_id disagrees on numbers or date — fail closed."""

    code: str = "MERGE_CONFLICT"
