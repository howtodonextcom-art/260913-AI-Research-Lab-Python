"""Prospective — frozen / pending / scored / hash chain (READ-ONLY)."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from vietlott_quant_lab.ui import labels
from vietlott_quant_lab.ui.cache import PROSPECTIVE_CACHE_POLICY
from vietlott_quant_lab.ui.loaders import load_prospective_bundle, prospective_pending_scored

st.set_page_config(page_title=f"{labels.PAGE_PROSPECTIVE} · Vietlott Quant Lab", layout="wide")
st.title(labels.PAGE_PROSPECTIVE)
st.info(f"{labels.READ_ONLY} · cache policy: `{PROSPECTIVE_CACHE_POLICY}`")

# Fresh load every rerun — do not long-cache mutable prospective decisions.
bundle = load_prospective_bundle()
if not bundle.freezes and not bundle.scores:
    st.info(labels.MISSING_PROSPECTIVE)
    st.stop()

st.subheader(labels.HASH_CHAIN)
if bundle.chain_ok:
    st.success(labels.CHAIN_OK)
else:
    st.error(f"{labels.CHAIN_FAIL}: {bundle.chain_error}")

pending, scored = prospective_pending_scored(bundle)

c1, c2, c3 = st.columns(3)
c1.metric(labels.FROZEN, len(bundle.freezes))
c2.metric(labels.PENDING, len(pending))
c3.metric(labels.SCORED, len(scored))

st.subheader(labels.PENDING)
if pending:
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "target_draw_id": f.target_draw_id,
                    "model_id": f.model_id,
                    "frozen_at": f.frozen_at.isoformat(),
                    "record_hash": f.record_hash[:16] + "…",
                    "dataset_hash": f.dataset_hash[:12] + "…",
                }
                for f in pending
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.caption("Không có freeze pending.")

st.subheader(labels.FROZEN)
st.dataframe(
    pd.DataFrame(
        [
            {
                "target_draw_id": f.target_draw_id,
                "model_id": f.model_id,
                "frozen_at": f.frozen_at,
                "record_hash": f.record_hash[:16] + "…",
                "previous_hash": f.previous_hash[:16] + "…",
                "top18": " ".join(f"{n:02d}" for n in f.top18),
            }
            for f in bundle.freezes
        ]
    ),
    use_container_width=True,
    hide_index=True,
)

st.subheader(labels.SCORED)
if not bundle.scores:
    st.write("—")
else:
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "freeze_record_hash": s.freeze_record_hash[:16] + "…",
                    "target_draw_id": s.target_draw_id,
                    "k18": s.k18,
                    "k7": s.k7,
                    "mcp": s.mcp,
                    "scored_at": s.scored_at,
                    "record_hash": s.record_hash[:16] + "…",
                }
                for s in bundle.scores
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )
