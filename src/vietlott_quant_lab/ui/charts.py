"""Plotly chart helpers for Streamlit pages."""

from __future__ import annotations

from typing import Any

import plotly.graph_objects as go


def compression_frontier_figure(rows: list[dict[str, Any]]) -> go.Figure:
    """Pool size vs model Mean K and null Mean K."""
    if not rows:
        fig = go.Figure()
        fig.update_layout(title="Compression frontier (no data)")
        return fig
    sizes = [int(r["pool_size"]) for r in rows]
    model_k = [float(r.get("model_mean_k", 0.0)) for r in rows]
    null_k = [float(r.get("null_mean_k", 0.0)) for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sizes, y=model_k, mode="lines+markers", name="Model Mean K"))
    fig.add_trace(go.Scatter(x=sizes, y=null_k, mode="lines+markers", name="Null Mean K"))
    fig.update_layout(
        title="Pool size vs containment (Mean K)",
        xaxis_title="Pool size m",
        yaxis_title="Mean K",
        legend_title="Series",
    )
    return fig


def compression_cost_figure(rows: list[dict[str, Any]]) -> go.Figure:
    """Pool size vs full Bao cost (VND)."""
    if not rows:
        fig = go.Figure()
        fig.update_layout(title="Full Bao cost (no data)")
        return fig
    sizes = [int(r["pool_size"]) for r in rows]
    costs = [float(r.get("cost_vnd", 0.0)) for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sizes, y=costs, mode="lines+markers", name="Full Bao cost"))
    fig.update_layout(
        title="Pool size vs Full Bao cost",
        xaxis_title="Pool size m",
        yaxis_title="Cost (VND)",
    )
    return fig


def cost_vs_containment_figure(rows: list[dict[str, Any]]) -> go.Figure:
    """Cost vs model Mean K scatter (Pareto-style view)."""
    if not rows:
        fig = go.Figure()
        fig.update_layout(title="Cost vs Mean K (no data)")
        return fig
    fig = go.Figure(
        data=[
            go.Scatter(
                x=[float(r.get("cost_vnd", 0.0)) for r in rows],
                y=[float(r.get("model_mean_k", 0.0)) for r in rows],
                mode="markers+text",
                text=[str(r["pool_size"]) for r in rows],
                textposition="top center",
                name="Pools",
            )
        ]
    )
    fig.update_layout(
        title="Cost vs evidence-adjusted containment (Mean K)",
        xaxis_title="Full Bao cost (VND)",
        yaxis_title="Model Mean K",
    )
    return fig
