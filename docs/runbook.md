# Runbook

Operational cheatsheet for maintainers. This lab does **not** predict Vietlott.

## Everyday

| Task | Command / action |
| --- | --- |
| Install | `pip install -e ".[dev]"` |
| UI | `streamlit run app.py` |
| Unit tests | `pytest` |
| Lint | `ruff check src tests scripts app.py pages` |
| Types | `mypy src/vietlott_quant_lab` |

## Data sync (when client exists)

```bash
python -m scripts.sync_official
```

- Prefer incremental sync after the first full crawl.
- On `SOURCE_SCHEMA_CHANGED` or historical conflict: **stop**, preserve snapshots, reconcile — do not force-overwrite canonical.
- Raw snapshots are immutable; never “fix” by deleting history silently.

## Live source probe

```bash
python scripts/live_source_check.py
```

| Exit | Meaning |
| --- | --- |
| 0 | Pass (read-only) |
| 1 | Source/structure fail; canonical untouched |
| 2 | Not executed (no client / network); canonical untouched |

GitHub Actions: workflow **Live source check** (`workflow_dispatch` / weekly schedule).

## Research CLIs (when implemented)

```bash
python -m scripts.run_window_tournament
python -m scripts.run_model_tournament
python -m scripts.freeze_prospective
```

Artifacts land under `artifacts/experiments/` and `artifacts/prospective/`. Final scientific summary template: `artifacts/reports/FINAL_VERDICT.md`.

## Integrity incidents

1. Duplicate draw id / date / result → fail closed.
2. Missing ids vs continuity from `#00001` → fail closed / health alert.
3. Manifest `dataset_sha256` drift without intentional sync → investigate before UI republish.
4. Prospective chain break → stop scoring; repair by append-only audit, never rewrite hashes.

## Docker health

```bash
docker build -t vietlott-quant-lab .
docker run --rm -p 8501:8501 vietlott-quant-lab
# HEALTHCHECK: python -c "import vietlott_quant_lab"
```

## Disclaimer reminder

Do not market rankings or scores as winning probabilities. Valid outcomes include `NO_RANKING_EDGE_FOUND` and `NOT_PRODUCTION_READY`.
