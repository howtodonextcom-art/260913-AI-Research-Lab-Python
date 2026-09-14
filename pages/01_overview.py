"""Overview — Scientific Verdict, dataset, best evidence."""

from __future__ import annotations

import streamlit as st

from vietlott_quant_lab import __version__
from vietlott_quant_lab.ui import labels
from vietlott_quant_lab.ui.dataset_panel import render_dataset_status_panel
from vietlott_quant_lab.ui.loaders import (
    latest_tournament_artifact,
    load_prospective_bundle,
)

st.set_page_config(page_title=f"{labels.PAGE_OVERVIEW} · Vietlott Quant Lab", layout="wide")
st.title(labels.PAGE_OVERVIEW)
st.warning(labels.DISCLAIMER_VI)
st.caption("UI chỉ đọc services/artifacts — không chứa research logic.")

render_dataset_status_panel(key_prefix="overview")
artifact = latest_tournament_artifact()
prosp = load_prospective_bundle()

verdict = labels.DEFAULT_SCIENTIFIC_VERDICT
production = labels.DEFAULT_PRODUCTION_VERDICT
best_model = "—"
best_window = "—"
evidence = "—"
protocol_hash = "—"
best_cutoff = "—"

if artifact:
    verdict = str(artifact.get("scientific_verdict") or verdict)
    champion = artifact.get("champion")
    if isinstance(champion, dict):
        best_model = str(champion.get("model_id") or champion.get("model") or best_model)
        lookback = champion.get("lookback")
        best_window = str(lookback if lookback is not None else best_window)
    else:
        best_model = str(artifact.get("model") or best_model)
    extra = artifact.get("extra") or {}
    if isinstance(extra, dict):
        if best_window == "—":
            best_window = str(extra.get("best_window") or best_window)
        best_cutoff = str(extra.get("best_validated_cutoff") or best_cutoff)
    if artifact.get("windows") is not None and best_window == "—":
        best_window = str(artifact.get("windows"))
    if artifact.get("hot_lookback") is not None and best_window == "—":
        best_window = str(artifact.get("hot_lookback"))
    protocol_hash = str(artifact.get("protocol_hash") or protocol_hash)
    evidence = str(artifact.get("holdout_status") or verdict)
    if best_cutoff == "—":
        best_cutoff = str(artifact.get("pool_size") or "18")

if prosp.scores:
    verdict = "PROSPECTIVE_SIGNAL"

st.subheader(labels.SCIENTIFIC_VERDICT)
st.markdown(f"### `{verdict}`")
st.caption(f"{labels.PRODUCTION_VERDICT}: `{production}` · app v{__version__}")

st.subheader(labels.RESEARCH_SECTION)
if not artifact:
    st.warning(labels.MISSING_ARTIFACT)
else:
    st.write(f"**{labels.BEST_MODEL}:** `{best_model}`")
    st.write(f"**{labels.BEST_WINDOW}:** `{best_window}`")
    st.write(f"**{labels.EVIDENCE_LEVEL}:** `{evidence}`")
    st.write(f"**{labels.PROTOCOL_HASH}:** `{protocol_hash}`")

st.subheader(labels.CANDIDATE_POOL_SECTION)
st.write(f"**{labels.BEST_CUTOFF}:** `{best_cutoff}`")
st.caption(labels.NO_NETWORK_RERUN)
