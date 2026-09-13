# Provenance Audit

Independent verification of artifact ↔ dataset ↔ protocol ↔ prospective relationships
after the P4–P10 Algorithm V2 pass.

## Chain under audit

```text
dataset (parquet + manifest)
    → experiment JSON (Round-1 + Algorithm V2)
    → FINAL_VERDICT / ALGORITHM_V2_RESEARCH
    → prospective freezes.jsonl (append-only)
```

## Dataset

| Check | Result |
| --- | --- |
| Canonical path | `data/processed/draws_mega645.parquet` |
| Record count | 1562 |
| Latest draw | `#01562` |
| Dataset SHA-256 | `c84b1714266aeebb4d7ea5446bf809143bf4569aa69db2b4ca154061d7fc5b05` |
| Manifest agrees | YES (`data/manifests/manifest_mega645.json`) |
| Experiment artifacts cite this hash | YES (Round-1 `c84b1714266a_…` prefix; V2 `algorithm_v2_latest.json` written from same load) |

## Experiment artifacts

| Artifact | Protocol hash | Model | Scientific verdict | Resolves? |
| --- | --- | --- | --- | --- |
| `artifacts/experiments/c84b1714266a_c4e8160e291f_3bf36a2e445a.json` | Round-1 tournament | `hot`/90 | `NO_RANKING_EDGE_FOUND` | YES |
| `artifacts/experiments/algorithm_v2_latest.json` | `ad821d506775c081…` (`algorithm_v2_classical_v1`) | Val-selected `multi_scale_v2` (not promoted) | `NO_RANKING_EDGE_FOUND` | YES |
| Hashed V2 write via `write_experiment_artifact` | same protocol family | same | same | YES (path printed at CLI run) |

## Protocol-hash domains (intentional dual domain)

| Domain | Purpose | Hash source |
| --- | --- | --- |
| Round-1 tournament | `ResearchProtocol` / `round1_default_v1` | model tournament artifact |
| Algorithm V2 tournament | `ResearchProtocolV2` / `algorithm_v2_classical_v1` | `algorithm_v2_latest.json` |
| Prospective freeze | `round1_prospective` freeze protocol | `freezes.jsonl` `protocol_hash` |

These are **different by design**. Matching them is not required; confusing them is a
documentation bug (addressed in `docs/research-protocol.md` / `docs/prospective.md`).

## Prospective ledger

| Check | Result |
| --- | --- |
| Path | `artifacts/prospective/freezes.jsonl` |
| Records | 1 |
| Target | `#01563` (next undrawn after `#01562`) |
| Model | `hot` (lookback 90) — Round-1 registered baseline |
| Status | pending (unscored; `actual_numbers` null) |
| `previous_hash` | genesis |
| Chain verify | `PASS` (`verify_chain`) |
| History rewrite | NONE — V2 did not append a replacement freeze because no holdout champion was promoted |

## Report citation integrity

| Report | Cited artifacts present? |
| --- | --- |
| `BASELINE_AUDIT.md` | YES |
| `BROWSER_ACCEPTANCE.md` | YES |
| `ALGORITHM_V2_RESEARCH.md` | YES → `algorithm_v2_latest.json` |
| `PRODUCTION_SCORECARD.md` | YES (this pass) |
| `FINAL_VERDICT.md` | YES — cites dataset hash, both experiment families, prospective tip |

## Gaps (honest)

1. **No dependency lockfile** (`uv.lock` / `requirements.txt`) — install reproducibility is soft.
2. **`data/raw/` snapshot** is a sync marker, not full HTTP body archive.
3. **Docker image never built** in this environment — deployment provenance for container path is unverified.
4. Round-1 hashed artifact filename remains the historical champion reference; V2 results live in `algorithm_v2_latest.json` (stable name for reports) plus the hashed write from the same CLI run.

## Verdict

**Provenance: PASS with documented gaps.** No report cites a missing artifact. Dataset hash is
consistent. Prospective chain verifies. Protocol dual-domain is documented rather than treated
as corruption.
