# Vietlott Quant Research Lab

**This project does not claim to predict Vietlott results.**

It is a **quantitative research laboratory** for Mega 6/45: official historical draws, leak-safe features, ranking 01–45, nested candidate pools (18→7), exact null models, tournaments, holdout, and prospective scoring.

Historical patterns are **hypotheses** under registered protocols — not forecasts. A valid scientific outcome is:

```text
NO_RANKING_EDGE_FOUND
```

Scores must not be labeled as probabilities unless calibration evidence exists. Scientific edge and production readiness are separate verdicts.

Official data source (production): **vietlott.vn only**. No GitHub/Kaggle mirrors as production datasets.

## Requirements

- Python **>= 3.12**
- Recommended: a virtual environment
- Optional: Docker

## Install

```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

pip install -e ".[dev]"
```

Copy environment template if needed:

```bash
copy .env.example .env
```

## Run Streamlit UI

From the repository root:

```bash
streamlit run app.py
```

Pages under `pages/` appear in the Streamlit sidebar. UI reads local services/artifacts; it does not crawl vietlott.vn on each rerun.

## Tests and CI

```bash
pytest
ruff check src tests scripts app.py pages
mypy src/vietlott_quant_lab
```

GitHub Actions:

- **CI** (`.github/workflows/ci.yml`) — Python 3.12, `pip install -e ".[dev]"`, ruff, mypy, pytest. **No live fetch** to vietlott.vn.
- **Live source check** (`.github/workflows/live-source-check.yml`) — `workflow_dispatch` + optional weekly schedule; runs `scripts/live_source_check.py` read-only (must not write/corrupt canonical data).

## Docker

```bash
docker build -t vietlott-quant-lab .
docker run --rm -p 8501:8501 vietlott-quant-lab
```

See [docs/deployment.md](docs/deployment.md).

## Docs

- [Architecture](docs/architecture.md)
- [Data source](docs/data-source.md)
- [Research protocol](docs/research-protocol.md)
- [Statistical null](docs/statistical-null.md)
- [Prospective](docs/prospective.md)
- [Deployment](docs/deployment.md)
- [Runbook](docs/runbook.md)

Final report template: `artifacts/reports/FINAL_VERDICT.md`.

## Layout

```text
app.py
pages/01_overview.py … 08_system_health.py
src/vietlott_quant_lab/{config,data,features,ranking,research,statistics,
                        prospective,optimization,provenance,observability,ui}
data/{raw,processed,snapshots,manifests}
artifacts/{experiments,prospective,reports}
tests/  scripts/  docs/  .github/workflows/
```

Long-running work uses CLI modules under `scripts/` (sync, tournaments, prospective) — not live crawl from the UI.

## Research CLI

```bash
python -m scripts.sync_official              # incremental official sync
python -m scripts.sync_official --force      # full crawl to #00001
python -m scripts.run_window_tournament
python -m scripts.run_model_tournament --no-window-selection
python -m scripts.freeze_prospective --model hot
python -m scripts.score_prospective
python -m scripts.live_source_check          # read-only availability probe
```
