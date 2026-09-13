# Statistical null model

Mega 6/45 draws are samples **without replacement**. The null for “how many of a fixed pool of size `m` appear in a random 6-number draw” is **hypergeometric** (equivalently, exact combinatorial).

## Exact PMF

For pool size `m` (typically 7…18), match count `K`:

```text
P(K = k) = C(m, k) * C(45 - m, 6 - k) / C(45, 6)
```

for admissible `k`. Implement with `math.comb` and/or SciPy; unit-test that the PMF sums to 1.

Expected matches under the null:

```text
E[K] = 6 * m / 45
```

For `m = 18`, `E[K] = 2.4`.

## Primary endpoint: Mean K

**Mean K** (average matched numbers per evaluated draw / ticket under the protocol) is the **primary** endpoint for model and window selection because:

- Its null expectation is exact and tractable.
- It is sensitive across the bulk of the distribution, not only rare jackpot events.
- It supports clean paired comparisons (walk-forward, A/B) and multiple-testing corrections (e.g. Holm-Bonferroni).

Secondary reporting may include `P(K ≥ 3)`, `P(K ≥ 4)`, `P(K ≥ 5)`, winner ranks, `MCP = max(r1..r6)`, and `P(MCP ≤ m)`.

## Why not optimize P6

`P6(m) = C(m, 6) / C(45, 6)` is exact but:

- Jackpot / full-match events are extremely rare; noise dominates selection.
- Optimizing P6 as the model-selection endpoint overfits to sparse tails and confuses cost with evidence.
- Cost formulas `Tickets(m) = C(m, 6)`, `Cost = 10000 * C(m, 6)` are for **reporting** and cost-efficiency only when incremental evidence vs random at the same `m` exists.

**Do not** choose champions by maximizing P6. Report P6 lift if useful, but keep Mean K primary.

## Monte Carlo

Prefer closed-form hypergeometric quantities when available. Use seeded, deterministic Monte Carlo only for statistics without a convenient closed form (or for fairness diagnostics under dependence). Never replace the exact null with Monte Carlo for Mean K / PMF when the formula exists.

## Dependence

When comparing walk-forward series, prefer paired permutation tests or HAC / Newey-West style adjustments rather than treating draws as independent if dependence matters for inference.
