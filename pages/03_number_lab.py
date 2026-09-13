"""Number Lab — pick 01–45, features/history charts, ranking table (Score ≠ probability)."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from vietlott_quant_lab.ranking.engine import ROUND1_MODELS
from vietlott_quant_lab.ui import labels
from vietlott_quant_lab.ui.cache import cached_all_feature_vectors, cached_ranking
from vietlott_quant_lab.ui.loaders import load_dataset_bundle

st.set_page_config(page_title=f"{labels.PAGE_NUMBER_LAB} · Vietlott Quant Lab", layout="wide")
st.title(labels.PAGE_NUMBER_LAB)
st.info(labels.SCORE_NOT_PROBABILITY)

bundle = load_dataset_bundle()
if not bundle.draws:
    st.info(labels.MISSING_DATASET)
    st.stop()

number = st.selectbox(
    labels.PICK_NUMBER,
    options=list(range(1, 46)),
    format_func=lambda n: f"{n:02d}",
    index=0,
)
model_id = st.selectbox(labels.MODEL_SELECTOR, options=list(ROUND1_MODELS), index=0)

features = cached_all_feature_vectors(
    bundle.draws,
    dataset_hash=bundle.dataset_hash,
    model_version="features_v1",
)
fv = features[int(number)]
ranking = cached_ranking(
    bundle.draws,
    dataset_hash=bundle.dataset_hash,
    model_id=str(model_id),
    model_version="round1",
    seed=0,
    lookback=90,
)

left, right = st.columns(2)
with left:
    st.subheader(f"{labels.FEATURES} · {int(number):02d}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("gap", fv.gap)
    c2.metric("gap_z", f"{fv.gap_z:.3f}")
    c3.metric("momentum_short", f"{fv.momentum_short:.4f}")
    c4.metric("shrinkage", f"{fv.shrinkage_signal:.4f}")
    st.json(
        {
            "freq": fv.freq,
            "z_freq": fv.z_freq,
            "mean_reversion_score": fv.mean_reversion_score,
            "stability": fv.stability,
            "pair_signal": fv.pair_signal,
            "rank": ranking.number_to_rank().get(int(number)),
            "score": ranking.number_to_score().get(int(number)),
        }
    )

with right:
    st.subheader(labels.HISTORY)
    hits = [d for d in bundle.draws if int(number) in d.numbers]
    st.write(f"Xuất hiện {len(hits)} / {len(bundle.draws)} kỳ")
    # Simple appearance chart via dataframe sparkline substitute
    sample = bundle.draws[-300:] if len(bundle.draws) > 300 else bundle.draws
    chart_df = pd.DataFrame(
        {
            "draw_id": [d.draw_id for d in sample],
            "appeared": [1 if int(number) in d.numbers else 0 for d in sample],
        }
    )
    st.line_chart(chart_df.set_index("draw_id"))
    if hits:
        st.dataframe(
            pd.DataFrame(
                {
                    "draw_id": [d.draw_id for d in hits[-50:]],
                    "draw_date": [d.draw_date.isoformat() for d in hits[-50:]],
                    "numbers": [" ".join(f"{n:02d}" for n in d.numbers) for d in hits[-50:]],
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

st.subheader(labels.RANKING_TABLE)
score_map = ranking.number_to_score()
rank_map = ranking.number_to_rank()
rows = []
for n in range(1, 46):
    f = features[n]
    rows.append(
        {
            labels.COL_RANK: rank_map[n],
            labels.COL_NUMBER: f"{n:02d}",
            labels.COL_SCORE: round(score_map[n], 6),
            "Short": round(f.freq.get("30", 0.0), 4),
            "Medium": round(f.freq.get("90", 0.0), 4),
            "Long": round(f.freq.get("365", f.freq.get("ALL", 0.0)), 4),
            "Gap": f.gap,
            "Momentum": round(f.momentum_short, 4),
            "Reversion": round(f.mean_reversion_score, 4),
            "Stability": round(f.stability, 4),
        }
    )
st.dataframe(
    pd.DataFrame(rows).sort_values(labels.COL_RANK).reset_index(drop=True),
    use_container_width=True,
    hide_index=True,
)
st.caption(
    f"Model `{ranking.model_id}` · dataset `{(bundle.dataset_hash or '—')[:12]}…` · "
    "Score ≠ probability."
)
