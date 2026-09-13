# Docker smoke evidence

Date: 2026-09-14 (local) / 2026-09-13 UTC build window  
Host: Windows 10, Docker Desktop CLI at `D:\DockerDesktop\resources\bin`  
Image: `vietlott-quant-lab:latest` (`sha256:ce3a3deca21cd80a4606abbf70f01da122b0cfb359da54570840dfa40b4af18f`)

## Commands

```bash
docker build -t vietlott-quant-lab:latest .
docker run -d --name vietlott-quant-lab-smoke -p 8501:8501 vietlott-quant-lab:latest
```

## Results

| Check | Result |
| --- | --- |
| Image build | PASS |
| Container start | PASS (`vietlott-quant-lab-smoke`) |
| Process user | `uid=10001(labuser)` non-root |
| `PROJECT_ROOT` | `/app` |
| Dataset path | `/app/data` |
| Draws loaded | **1562** |
| Dataset hash | `c84b1714266aeebb4d7ea5446bf809143bf4569aa69db2b4ca154061d7fc5b05` |
| Manifest validation | `PASS` |
| `GET /_stcore/health` | **200** body `ok` |
| `GET /` | **200** (Streamlit shell HTML) |
| Docker `HEALTHCHECK` | **healthy** |

## Fix applied during smoke

Installed package layout previously resolved `project_root` under site-packages (`/usr/local/lib/python3.12/...`), so the UI saw zero draws despite parquet being present under `/app/data`. Fixed by:

1. `PROJECT_ROOT=/app` in the Dockerfile
2. `default_project_root()` falling back to CWD when `app.py` is present
3. `.dockerignore` allowing `data/processed/**/*.parquet` into the image

## Notes

- Smoke used the in-image canonical snapshot (no live Vietlott fetch).
- Full Playwright browser suite remains the CI `browser-e2e` job against a local venv Streamlit; Docker smoke verifies deploy path (build/run/health/dataset).
- Container may remain running locally on `http://127.0.0.1:8501` after this pass.
