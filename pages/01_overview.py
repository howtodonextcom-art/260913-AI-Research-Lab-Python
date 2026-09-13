"""Overview — Scientific Verdict, dataset, best evidence."""

from __future__ import annotations

import streamlit as st

from vietlott_quant_lab import __version__
from vietlott_quant_lab.ui import labels
from vietlott_quant_lab.ui.loaders import (
    latest_tournament_artifact,
    load_dataset_bundle,
    load_prospective_bundle,
)

st.set_page_config(page_title=f"{labels.PAGE_OVERVIEW} · Vietlott Quant Lab", layout="wide")
st.title(labels.PAGE_OVERVIEW)
st.warning(labels.DISCLAIMER_VI)
st.caption("UI chỉ đọc services/artifacts — không chứa research logic.")

bundle = load_dataset_bundle()
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

st.subheader(labels.DATASET_SECTION)
if not bundle.draws:
    st.info(labels.MISSING_DATASET)
else:
    m = bundle.manifest
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(labels.DRAW_COUNT, m.record_count if m else len(bundle.draws))
    c2.metric(labels.FIRST_DRAW, (m.first_draw_id if m else bundle.draws[0].draw_id))
    c3.metric(labels.LATEST_DRAW, (m.last_draw_id if m else bundle.draws[-1].draw_id))
    c4.metric(labels.LAST_SYNC, (m.last_sync if m else "—")[:19])
    st.write(f"**{labels.SOURCE}:** `{m.source if m else 'vietlott-official'}`")
    st.write(f"**{labels.DATASET_HASH}:** `{bundle.dataset_hash or '—'}`")
    if m:
        st.write(f"**{labels.VALIDATION}:** `{m.validation_status}`")

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
