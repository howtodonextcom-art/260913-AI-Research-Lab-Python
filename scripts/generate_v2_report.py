"""Generate ALGORITHM_V2_RESEARCH.md and related report snippets from latest JSON."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "artifacts" / "experiments" / "algorithm_v2_latest.json"
OUT = ROOT / "artifacts" / "reports" / "ALGORITHM_V2_RESEARCH.md"


def _fmt(x: float, nd: int = 4) -> str:
    return f"{x:.{nd}f}"


def _ci(inf: dict | None) -> str:
    if not inf:
        return "n/a"
    hac = inf.get("newey_west_hac") or {}
    lo, hi = hac.get("ci_low"), hac.get("ci_high")
    if lo is None or hi is None:
        return "n/a"
    return f"[{lo:.3f}, {hi:.3f}]"


def _evidence(mean_k: float, lift: float, adj_p: float, practical: float = 0.05) -> str:
    if lift >= practical and adj_p <= 0.05 and mean_k > 2.4:
        return "SIGNAL_CANDIDATE"
    if lift > 0:
        return "WEAK_POSITIVE"
    return "NO_EDGE"


def phase_table(scores: list[dict], phase: str, *, use_adj: bool) -> str:
    lines = [
        "| Model | Complexity | Mean K | Δ vs null | P4 | P5 | P6 | Mean MCP | Rank metric | CI (HAC) | Adj p | Evidence |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---|",
    ]
    for s in scores:
        w = s[phase]
        p = s["adjusted_p_val"] if use_adj else w["one_sided_p_hac"]
        lines.append(
            "| {mid} | {c} | {mk} | {lift} | {p4} | {p5} | {p6} | {mcp} | {mwr} | {ci} | {p} | {ev} |".format(
                mid=s["model_id"],
                c=s["complexity"],
                mk=_fmt(w["mean_k"]),
                lift=_fmt(w["lift_mean_k"]),
                p4=_fmt(w["p_ge_4"]),
                p5=_fmt(w["p_ge_5"]),
                p6=_fmt(w["p_eq_6"]),
                mcp=_fmt(w["mean_mcp"], 2),
                mwr=_fmt(w["mean_winner_rank"], 2),
                ci=_ci(w.get("inference")),
                p=_fmt(p),
                ev=_evidence(w["mean_k"], w["lift_mean_k"], p),
            )
        )
    return "\n".join(lines)


def compression_table(comp: dict | None) -> str:
    if not comp:
        return "_Compression not computed._"
    lines = [
        "| Pool | Random Mean K | Model Mean K | Δ | P4 | P5 | P6 | MCP≤m | Tickets | Cost | Evidence |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in comp.get("rows") or []:
        lines.append(
            "| {m} | {nk} | {mk} | {d} | {p4} | {p5} | {p6} | {mcp} | {t} | {c} | {ev} |".format(
                m=r["pool_size"],
                nk=_fmt(r["null_mean_k"]),
                mk=_fmt(r["model_mean_k"]),
                d=_fmt(r["delta_mean_k"]),
                p4=_fmt(r["p_ge_4"]),
                p5=_fmt(r["p_ge_5"]),
                p6=_fmt(r["p_eq_6"]),
                mcp=_fmt(r["mcp_le_m_rate"]),
                t=r["tickets"],
                c=r["cost_vnd"],
                ev=r["evidence_status"],
            )
        )
    return "\n".join(lines)


def main() -> None:
    data = json.loads(SUMMARY.read_text(encoding="utf-8"))
    t = data["tournament"]
    champ = t.get("champion") or {}
    test = t.get("test") or {}
    ablation = data.get("ablation") or []
    fragility = data.get("fragility") or []

    abl_lines = [
        "| Feature group | Baseline Mean K | Ablated Mean K | Δ | Label |",
        "|---|---:|---:|---:|---|",
    ]
    for a in ablation:
        abl_lines.append(
            f"| {a['feature_group']} | {_fmt(a['baseline_mean_k'])} | "
            f"{_fmt(a['ablated_mean_k'])} | {_fmt(a['delta_mean_k'])} | {a['label']} |"
        )

    frag_lines = [
        "| Perturbation | Mean K | Lift | Unstable | Notes |",
        "|---|---:|---:|---|---|",
    ]
    for f in fragility:
        frag_lines.append(
            f"| {f['perturbation']} | {_fmt(f['mean_k'])} | {_fmt(f['lift_mean_k'])} | "
            f"{f['unstable']} | {f.get('notes','')} |"
        )

    md = f"""# Algorithm V2 Research Report

Evidence-first classical ranking research for Vietlott Mega 6/45.
**Scores are ranking signals only — never probabilities.**
`DESCRIPTIVE PATTERN ≠ PREDICTIVE SIGNAL`.

## Protocol

| Field | Value |
| --- | --- |
| Protocol name | `algorithm_v2_classical_v1` |
| Protocol hash | `{t["protocol_hash"]}` |
| Split | chronological 50/25/25 |
| Primary endpoint | Mean K @ Top18 (null = 2.4 exact) |
| Primary inference | Newey–West HAC (Student-t legacy retained) |
| Multiplicity | Holm–Bonferroni on Validation HAC p-values |
| Family | {t["family_definition"]} |
| HOT lookback (registered) | {t["hot_lookback"]} |
| EWF half-life (Dev-selected) | {t["ewf_half_life"]} |
| Practical Δ Mean K | 0.05 |
| Artifact | `artifacts/experiments/algorithm_v2_latest.json` |

## Scientific outcome

| Field | Value |
| --- | --- |
| Scientific verdict | `{t["scientific_verdict"]}` |
| Holdout status | `{t["holdout_status"]}` |
| Pool-18 gate | `NO_VERIFIED_18_POOL_EDGE` |
| Tournament champion (Val max Mean K) | `{champ.get("model_id")}` |
| Champion config hash | `{champ.get("model_config_hash")}` |
| Test Mean K | {_fmt(test.get("mean_k", 0))} (lift {_fmt(test.get("lift_mean_k", 0))}) |
| Test HAC p | {_fmt(test.get("one_sided_p_hac", 1))} |
| Fragility label | `{data.get("fragility_label")}` |
| ML status | `{data.get("ml_status")}` |

### Keep / reject decisions

| Model family | Decision | Reason |
| --- | --- | --- |
| Random / All-history / HOT / EWF / MultiScale V1/V2 / Momentum / Reversion / Hazard | `REJECTED_NO_BENEFIT` for predictive promotion | No Validation signal surviving practical Δ + Holm; Test lift negative for Val-selected champion |
| Regularized ML / pair / regime | `PRUNE_ML` | Classical V2 showed no Validation edge meeting promotion gates |
| Compression 18→7 specialized search | Skipped | Gate `NO_VERIFIED_18_POOL_EDGE`; transparency table from frozen ranking only |

## Development (explore only)

{phase_table(t["scores"], "development", use_adj=False)}

## Validation (select only)

{phase_table(t["scores"], "validation", use_adj=True)}

## Test (confirm once — frozen champion `{champ.get("model_id")}`)

| Model | Mean K | Δ vs null | P4 | P5 | P6 | Mean MCP | Mean winner rank | CI (HAC) | HAC p | Evidence |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| {champ.get("model_id")} | {_fmt(test.get("mean_k", 0))} | {_fmt(test.get("lift_mean_k", 0))} | {_fmt(test.get("p_ge_4", 0))} | {_fmt(test.get("p_ge_5", 0))} | {_fmt(test.get("p_eq_6", 0))} | {_fmt(test.get("mean_mcp", 0), 2)} | {_fmt(test.get("mean_winner_rank", 0), 2)} | {_ci(test.get("inference"))} | {_fmt(test.get("one_sided_p_hac", 1))} | NO_EDGE |

## Ablation (Multi-Scale V2 on Validation)

{chr(10).join(abl_lines)}

## Fragility / red-team

Label: **`{data.get("fragility_label")}`**

{chr(10).join(frag_lines)}

## Compression frontier (frozen ranking family; transparency)

Pool-18 gate did **not** pass. Table below is descriptive only — not a claim of algorithmic compression edge.

{compression_table(data.get("compression"))}

## Prospective

Existing append-only freeze for target `#01563` (`hot`/90) remains the chain tip.
V2 did not promote a holdout champion, so **no history rewrite** and no replacement freeze was appended.
See `PROVENANCE_AUDIT.md`.

## Honesty reminders

- Ranking score ≠ probability
- Candidate pool ≠ guaranteed winners
- Cost reduction ≠ algorithmic edge
- `NO_RANKING_EDGE_FOUND` is a valid research result
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(md, encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
