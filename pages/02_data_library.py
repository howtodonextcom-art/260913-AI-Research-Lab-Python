"""Data Library — draws table, filters, integrity (cache by dataset hash)."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from vietlott_quant_lab.ui import labels
from vietlott_quant_lab.ui.loaders import (
    integrity_for_draws,
    load_dataset_bundle,
    official_detail_url,
)

st.set_page_config(page_title=f"{labels.PAGE_DATA_LIBRARY} · Vietlott Quant Lab", layout="wide")
st.title(labels.PAGE_DATA_LIBRARY)
st.caption(labels.NO_NETWORK_RERUN)

bundle = load_dataset_bundle()
if not bundle.draws:
    st.info(labels.MISSING_DATASET)
    st.stop()

m = bundle.manifest


@st.cache_data(show_spinner=False)
def _draws_frame(_dataset_hash: str, rows: list[dict[str, object]]) -> pd.DataFrame:
    """Cache key includes dataset hash; no network on rerun."""
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def _integrity_summary(_dataset_hash: str, n: int) -> dict[str, object]:
    report = integrity_for_draws(load_dataset_bundle().draws)
    return {"ok": report.ok, "issues": list(report.issues), "n": n}


rows = [
    {
        "draw_id": d.draw_id,
        "draw_date": d.draw_date.isoformat(),
        "numbers": " ".join(f"{n:02d}" for n in d.numbers),
        "source_url": official_detail_url(d.draw_id),
    }
    for d in bundle.draws
]
df = _draws_frame(bundle.dataset_hash, rows)
integrity = _integrity_summary(bundle.dataset_hash, len(bundle.draws))

st.write(
    f"**{labels.INTEGRITY}:** "
    f"`{labels.STATUS_PASS if integrity['ok'] else labels.STATUS_FAIL}` · "
    f"**{labels.VALIDATION}:** `{m.validation_status if m else 'UNKNOWN'}` · "
    f"**{labels.DATASET_HASH}:** `{(bundle.dataset_hash or '—')[:16]}…` · "
    f"**{labels.SYNC_STATUS}:** `{(m.last_sync if m else '—')}`"
)
if integrity["ok"] is False:
    for issue in list(integrity["issues"])[:15]:
        st.write(f"- {issue}")

st.subheader(labels.FILTERS)
c1, c2 = st.columns(2)
id_q = c1.text_input(labels.DRAW_ID, value="")
date_q = c2.text_input(labels.DRAW_DATE, value="", placeholder="YYYY-MM-DD substring")
view = df
if id_q.strip():
    view = view[view["draw_id"].astype(str).str.contains(id_q.strip(), regex=False)]
if date_q.strip():
    view = view[view["draw_date"].astype(str).str.contains(date_q.strip(), regex=False)]

st.dataframe(
    view.rename(
        columns={
            "draw_id": labels.DRAW_ID,
            "draw_date": labels.DRAW_DATE,
            "numbers": labels.NUMBERS,
            "source_url": labels.OFFICIAL_LINK,
        }
    ),
    use_container_width=True,
    hide_index=True,
)
st.caption(f"{len(view)} / {len(df)} rows")
