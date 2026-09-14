"""Vietlott Quant Research Lab — Streamlit entrypoint."""

from __future__ import annotations

import streamlit as st

from vietlott_quant_lab import __version__
from vietlott_quant_lab.ui import labels
from vietlott_quant_lab.ui.dataset_panel import render_dataset_status_panel
from vietlott_quant_lab.ui.loaders import list_experiment_artifacts

st.set_page_config(
    page_title=labels.APP_TITLE,
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title(labels.APP_TITLE)
st.caption(f"v{__version__} · {labels.APP_SUBTITLE}")

st.warning(labels.DISCLAIMER_VI)

st.sidebar.header("Điều hướng")
st.sidebar.markdown(
    """
Dùng menu multipage (`pages/`):

1. Tổng quan (Overview)
2. Thư viện dữ liệu (Data Library)
3. Number Lab
4. Candidate Pool
5. A/B Tournament
6. Compression Frontier
7. Prospective
8. System Health
"""
)

bundle = render_dataset_status_panel(key_prefix="home")
artifacts = list_experiment_artifacts()
st.metric(labels.EXPERIMENT_ARTIFACTS, len(artifacts))

st.markdown(
    """
## Đây là gì?

Phòng thí nghiệm **định lượng** cho Mega 6/45:

- Chỉ dữ liệu chính thức Vietlott (snapshot local; UI **không** crawl mỗi rerun)
- Ranking 01–45 và candidate pool lồng nhau 18→7
- Exact null, tournament, holdout, prospective hash-chain

## Trạng thái

**Streamlit UI** nối 8 trang tới services/artifacts.
Research dài chạy qua CLI; UI đọc kết quả đã ghi và có thể **Cập nhật dữ liệu** (incremental sync).

```text
python -m scripts.sync_official
python -m scripts.run_window_tournament
python -m scripts.run_model_tournament
python -m scripts.freeze_prospective
```
"""
)

if not bundle.draws:
    st.info(labels.MISSING_DATASET)

st.caption(labels.NO_NETWORK_RERUN)
