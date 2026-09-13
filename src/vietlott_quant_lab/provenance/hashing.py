"""SHA-256 helpers and canonical JSON for protocol / experiment identity."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json(obj: Any) -> str:
    """Deterministic JSON: sorted keys, compact separators, UTF-8 safe."""
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=_json_default,
    )


def _json_default(obj: Any) -> Any:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "__dict__"):
        return {k: v for k, v in vars(obj).items() if not k.startswith("_")}
    msg = f"Object of type {type(obj).__name__} is not JSON serializable"
    raise TypeError(msg)


def sha256_hex(data: str | bytes) -> str:
    """SHA-256 hex digest of text or bytes."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def sha256_canonical(obj: Any) -> str:
    """SHA-256 of canonical JSON for ``obj``."""
    return sha256_hex(canonical_json(obj))


def short_hash(hex_digest: str, *, n: int = 12) -> str:
    """Truncate a hex digest for human-readable IDs."""
    if n < 1:
        msg = f"n must be >= 1, got {n}"
        raise ValueError(msg)
    return hex_digest[:n]
