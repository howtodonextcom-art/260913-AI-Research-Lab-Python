# Prospective scoring (hash chain)

Prospective evaluation freezes commitments **before** a future draw is known, then appends scores after the official result. The UI is **read-only** over this store.

## What is frozen

Before the target draw:

- Full ranking 01–45 (`RankedNumber` permutation)
- Nested pools top-18 … top-7 from that same ranking
- Model id / feature version / lookback(s)
- `dataset_sha256`, `protocol_hash`, model/feature hashes
- Target `draw_id` (future) and freeze timestamp

> **Note on `protocol_hash`:** this is *not* the same value as the `protocol_hash` recorded
> in tournament experiment artifacts (`research/protocol.py`'s `ResearchProtocol`). Prospective
> freezes hash their own `DEFAULT_PROTOCOL` object, defined in `prospective/freeze.py`, which
> is a distinct, independently-registered protocol from the Round-1 tournament protocol
> described in `research-protocol.md`. The two protocol-hash domains are expected to differ —
> do not treat a mismatch between an experiment artifact's `protocol_hash` and a freeze
> record's `protocol_hash` as a provenance break; compare each hash only within its own
> domain (tournament artifacts against each other, freeze records against each other).

## Hash chain (append-only)

Each record includes:

- `record_hash` — hash of the record payload (canonical encoding)
- `previous_hash` — hash of the prior chain tip (genesis uses a documented zero / null sentinel)

Rules:

1. **Append-only** — never edit or delete prior freeze/score rows in place.
2. After the official result arrives, **only append** a score record linking to the freeze (match counts, Mean K contribution, pool hits, etc.).
3. Chain integrity checks verify `previous_hash` linkage and recomputed `record_hash`.
4. Failures (missing draw, integrity mismatch) are logged as observability events — they do not rewrite history.

## CLI

Long-running freeze/score flows run via CLI (e.g. `python -m scripts.freeze_prospective`), not via Streamlit network calls.

## UI

The Prospective page shows frozen / pending / scored / chain status. It must not mutate the chain. Cache keys must not treat mutable prospective tips as immortal cache content.
