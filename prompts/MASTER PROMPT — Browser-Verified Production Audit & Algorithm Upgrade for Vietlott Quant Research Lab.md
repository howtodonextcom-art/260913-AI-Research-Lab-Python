# MASTER PROMPT
# Browser-Verified Production Audit & Algorithm Upgrade
## Python · Streamlit · Vietlott Mega 6/45 · Evidence-First Algorithm Research

---

# 0. TARGET

Repository:

`https://github.com/howtodonextcom-art/260913-AI-Research-Lab-Python`

Project:

`Vietlott Quant Research Lab`

Technology constraint:

- Python >= 3.12
- Streamlit
- DuckDB
- Parquet
- NumPy / Pandas / SciPy
- Plotly
- Official Vietlott data only for production dataset

Do not migrate to:

- Next.js
- React
- TypeScript
- Firebase
- Supabase
- another frontend framework

unless explicitly requested by the human operator.

---

# 1. ROLE

Act as an autonomous senior engineering and quantitative-research team containing at minimum:

1. Principal Python Architect
2. Streamlit Product Engineer
3. Browser QA / Playwright Engineer
4. Data Engineer
5. Quantitative Researcher
6. Statistical Auditor
7. Probability / Combinatorics Expert
8. ML / Ranking Researcher
9. Reliability / SRE Engineer
10. Security Engineer
11. Independent Red-Team Reviewer

The implementer must not be the only reviewer.

Use independent sub-agents where available.

---

# 2. PRIMARY MISSION

Audit the repository as it actually exists at current HEAD, run it locally, open it in a real browser, test all major user journeys, identify product/runtime/scientific defects, fix the justified defects, then upgrade the ranking research programme.

The objective is not:

> make the model look smarter.

The objective is:

> determine whether any reproducible ranking method can place the six numbers of a future draw systematically nearer the top of a 01–45 ranking than exact-random expectation, while keeping the application production-reliable and scientifically honest.

The system must be allowed to conclude:

`NO_RANKING_EDGE_FOUND`

after all upgrades.

That is a valid result.

---

# 3. NON-NEGOTIABLE SCIENTIFIC PRINCIPLE

Never convert:

`historical pattern`

into:

`prediction claim`

without evidence.

Maintain permanently:

`DESCRIPTIVE PATTERN ≠ PREDICTIVE SIGNAL`

`PREDICTIVE SIGNAL ≠ PROVEN EDGE`

`BACKTEST ≠ HOLDOUT`

`HOLDOUT ≠ PROSPECTIVE`

`RANKING SCORE ≠ PROBABILITY`

`CANDIDATE POOL ≠ GUARANTEED WINNERS`

`COST REDUCTION ≠ ALGORITHMIC EDGE`

No model is required to beat randomness.

Never manipulate the research protocol merely to produce a positive result.

---

# 4. FIRST ACTION: FREEZE THE BASELINE

Before modifying code:

Record:

- exact HEAD SHA;
- branch;
- `git status`;
- Python version;
- dependency versions;
- dataset manifest;
- dataset SHA-256;
- latest draw;
- number of draws;
- existing experiment artifacts;
- prospective chain status;
- current scientific verdict;
- current production verdict.

Create:

`artifacts/reports/BASELINE_AUDIT.md`

Do not rely only on README or prior report.

Inspect source and runtime independently.

---

# 5. VERIFY CURRENT CLAIMS

The repository currently contains claims such as:

`PRODUCTION_READY`

and:

`NO_RANKING_EDGE_FOUND`

Do not accept either automatically.

Independently verify both.

Explicitly distinguish:

### Engineering verdict

`PRODUCTION_READY`

or

`NOT_PRODUCTION_READY`

### Scientific verdict

One of:

`NO_RANKING_EDGE_FOUND`

`EXPLORATORY_SIGNAL`

`VALIDATION_SIGNAL`

`HOLDOUT_SIGNAL`

`PROSPECTIVE_SIGNAL`

Engineering quality and predictive evidence are independent axes.

---

# 6. BASELINE STATIC QUALITY

Run from a clean environment:

```bash
python --version
pip install -e ".[dev]"
ruff check src tests scripts app.py pages
mypy src/vietlott_quant_lab
pytest -q
```

Mypy must eventually be blocking.

Current CI behavior that allows mypy failure must be reviewed and, unless a concrete blocker exists, removed.

Do not call the repository production-ready while strict static typing is knowingly permitted to fail.

---

# 7. RUN THE REAL APPLICATION

Start:

```bash
streamlit run app.py
```

Use a deterministic port.

Wait for the app to become healthy.

Do not infer browser behavior from Python imports.

Do not treat Streamlit source compilation as browser testing.

---

# 8. MANDATORY REAL BROWSER TEST

Open the running application using one of:

1. Browser MCP / computer-use browser, if available
2. Playwright with real Chromium
3. equivalent real-browser automation

Do not substitute:

- `compile()`
- import tests
- requests-only tests
- HTML snapshots
- source inspection

for browser acceptance.

A real Chromium browser must render the application.

---

# 9. BROWSER VIEWPORT MATRIX

Mandatory minimum:

### Desktop

`1440 × 900`

### Tablet

`768 × 1024`

### Mobile

`390 × 844`

For every viewport:

- page must render;
- no horizontal overflow unless intentional;
- no clipped critical controls;
- charts readable;
- tables usable;
- sidebar/navigation usable;
- no uncaught exceptions;
- no permanent loading state.

---

# 10. BROWSER FAILURE CONDITIONS

Browser suite must fail on:

- uncaught JS exception;
- Streamlit frontend error;
- Python traceback rendered in UI;
- critical request failure;
- blank page;
- hydration/runtime crash;
- missing required chart;
- missing required data;
- broken navigation;
- control that changes no output;
- unexpected stale state;
- broken browser back/forward state where relevant.

Collect:

- screenshot on failure;
- Playwright trace if supported;
- console logs;
- failed network requests.

---

# 11. TEST ALL STREAMLIT PAGES

The application currently contains these major pages.

Browser-test every one:

1. Overview
2. Data Library
3. Number Lab
4. Candidate Pool
5. A/B Tournament
6. Compression Frontier
7. Prospective
8. System Health

Do not mark browser coverage complete until all are visited.

---

# 12. OVERVIEW ACCEPTANCE

Verify visibly:

- scientific verdict;
- dataset count;
- first draw;
- latest draw;
- last sync;
- dataset hash;
- selected/champion model;
- current evidence level;
- no misleading predictive language.

Test degraded state when artifact is unavailable.

---

# 13. DATA LIBRARY ACCEPTANCE

Verify:

- 1st and latest draw;
- filtering;
- sorting;
- pagination/table behavior;
- numbers displayed correctly;
- official-source metadata;
- manifest status;
- dataset freshness;
- error/degraded state.

Cross-check a sample of records against canonical local dataset.

If live-source verification is allowed in the environment, compare a small controlled sample against vietlott.vn.

Never bulk-fetch unnecessarily during UI testing.

---

# 14. NUMBER LAB ACCEPTANCE

Interact with several numbers including:

`01`

`23`

`45`

Verify the UI exposes, when applicable:

- frequency;
- recency/gap;
- momentum;
- mean reversion;
- stability;
- shrinkage;
- co-occurrence.

Verify changing number changes charts/data.

Detect stale Streamlit cache bugs.

---

# 15. CANDIDATE POOL ACCEPTANCE

Test pool sizes:

`18`

`15`

`12`

`10`

`7`

For every pool size verify:

- exactly m unique values;
- values ∈ [1,45];
- nested Top-m invariant;
- Mean K;
- exact random Mean K;
- lift;
- P≥4;
- P≥5;
- P=6;
- MCP;
- number of Bao tickets;
- cost.

Changing pool size must update all relevant outputs.

---

# 16. MODEL SELECTOR ACCEPTANCE

For every available research model:

- render ranking;
- verify ranking length = 45;
- every number 1–45 appears exactly once;
- select model;
- pool changes accordingly where expected;
- UI does not label score as probability.

---

# 17. A/B TOURNAMENT ACCEPTANCE

Verify UI clearly separates:

- Development;
- Validation;
- Test.

Verify:

- champion is read from experiment artifact;
- UI does not manufacture winner;
- model complexity is visible or inspectable;
- Test is not used for model selection;
- protocol hash visible;
- dataset hash visible.

If expected artifact is referenced by report but absent:

flag provenance inconsistency.

Fix the reporting/artifact chain.

---

# 18. COMPRESSION FRONTIER ACCEPTANCE

Verify:

`18 → 17 → ... → 7`

is generated from nested Top-m ranking logic.

For every m display:

- exact random baseline;
- model Mean K;
- delta;
- P4;
- P5;
- P6;
- MCP containment;
- Bao ticket count;
- Bao cost;
- evidence status.

Highlight clearly if:

`model <= random`

Do not cosmetically hide negative results.

---

# 19. PROSPECTIVE ACCEPTANCE

Verify:

- frozen record appears;
- target draw ID;
- frozen timestamp;
- model ID;
- ranking 01–45;
- Top7..Top18;
- dataset hash;
- feature hash;
- model hash;
- protocol hash;
- previous hash;
- record hash.

Verify pending record cannot silently mutate.

If target draw is not yet available:

status must remain pending.

Never fabricate scoring.

---

# 20. SYSTEM HEALTH ACCEPTANCE

System Health must derive meaningful status from reality.

Check:

- dataset exists;
- manifest valid;
- dataset hash consistent;
- DuckDB readable;
- experiment artifacts;
- prospective chain;
- application version;
- freshness;
- source health where appropriate.

A health component that always returns green regardless of failure is invalid.

---

# 21. ADD REAL BROWSER E2E TO CI

The repository currently needs true browser CI.

Implement Playwright or an equivalent real browser framework.

Preferred Python route:

```text
playwright
pytest-playwright
```

or controlled Playwright Python scripts.

GitHub Actions browser job:

1. install package;
2. install Chromium;
3. start Streamlit;
4. wait for health;
5. run browser tests;
6. upload screenshots/traces on failure.

Browser CI must use local bundled/canonical data.

Do not depend on live vietlott.vn availability.

---

# 22. STREAMLIT APPTEST

Browser tests are mandatory.

Additionally use:

`streamlit.testing.v1.AppTest`

where it reduces testing cost for:

- widget states;
- page-level exceptions;
- missing artifacts;
- deterministic interactions.

AppTest is supplementary.

It does not replace Chromium.

---

# 23. CI TARGET

Final CI should resemble:

```text
Install
↓
Ruff
↓
Mypy STRICT
↓
Unit
↓
Property
↓
Integration
↓
Data Integrity
↓
Provenance
↓
Research Controls
↓
Streamlit AppTest
↓
Start Streamlit
↓
Browser E2E Desktop
↓
Browser E2E Mobile
↓
Artifact/Trace Upload
```

No `continue-on-error` for required production gates.

---

# 24. CURRENT ALGORITHM BASELINE

Do not delete the current models before benchmarking.

Preserve as baselines:

### RANDOM

uniform seeded random ranking.

### HOT

single-window frequency-based ranking.

### MULTI_SCALE_SHRINKAGE_V1

current implementation using multiple windows and fixed manual weights.

Record their exact baseline performance before algorithm changes.

---

# 25. IMPORTANT EXISTING BLIND SPOT: MANUAL WEIGHTS

The current Multi-Scale Shrinkage model uses manually chosen coefficients.

Treat those coefficients as hypotheses, not truths.

Do not merely tweak:

`1.0 → 1.2`

until Test improves.

That would contaminate the holdout.

Instead:

- parameterize the scoring function;
- choose candidate configurations using Development;
- narrow on Validation;
- freeze;
- open Test exactly once for a new registered protocol.

---

# 26. DO NOT REUSE THE OLD TEST FOR TUNING

If the old Test result is already known, that dataset slice is no longer pristine for future model development.

This is critical.

Classify historical Test as:

`PREVIOUSLY_OBSERVED_HOLDOUT`

Do not tune new algorithms against it.

For new algorithm generations use one of:

### Option A

rolling-origin nested temporal validation entirely inside historical data, while treating old Test as diagnostic only;

and reserve prospective future draws as the true strongest evidence.

### Option B

define a new chronological research protocol with strict frozen cutoffs justified before model selection.

Do not pretend an already-seen holdout is unseen.

---

# 27. UPGRADE THE STATISTICAL ENGINE

Current Mean K significance must not rely only on naive independent-observation Student t assumptions.

Investigate serial dependence caused by:

- overlapping lookback windows;
- adjacent draws;
- repeated rolling models.

Add where appropriate:

### Newey-West HAC

for mean-effect inference.

### Moving/block bootstrap

for robust uncertainty.

### Paired permutation / sign-flip

for A/B comparisons where assumptions permit.

Report:

- effect;
- confidence interval;
- raw p;
- adjusted p;
- sample count;
- method.

Do not choose whichever method produces significance.

---

# 28. PRIMARY ENDPOINT MUST BE LOCKED

For 45→18 research:

Primary:

`Mean K @ Top18`

Null:

`2.4`

Secondary:

- P(K≥4)
- P(K≥5)
- P(K=6)
- Mean winner rank
- Median winner rank
- MCP
- P(MCP≤18)
- compression-curve metrics

Do not change primary endpoint after viewing Test.

---

# 29. ADD A RANKING-WIDE METRIC

Pool18 alone throws away information.

Add at least one full-ranking metric.

Recommended:

### Mean Winner Rank

For each draw:

rank positions of six winners.

Measure mean.

### MCP

Maximum rank among the six winners.

### Compression AUC

Define containment performance over m=7…18 and summarize the full curve.

This helps distinguish:

a model that misses Top18 by one rank

from:

a model that scatters winners near rank 40.

---

# 30. ALGORITHM RESEARCH PROGRAMME V2

Do not jump immediately to neural networks.

Build challengers in controlled stages.

Mandatory candidate families:

### A. ALL-HISTORY BASELINE

Long-run frequency baseline.

### B. SINGLE WINDOW HOT

Existing baseline.

### C. MULTI-SCALE V1

Existing model.

### D. EXPONENTIALLY WEIGHTED FREQUENCY

Instead of hard window only:

\[
w(age)=e^{-\lambda age}
\]

Test several pre-registered half-lives.

### E. MULTI-SCALE SHRINKAGE V2

Improve V1 with properly normalized features and development-selected weights.

### F. MOMENTUM MODEL

Explicit continuation hypothesis.

### G. MEAN-REVERSION MODEL

Explicit opposite hypothesis.

Momentum and reversion must compete.

Do not blend them before measuring each separately.

### H. RECENCY / HAZARD MODEL

Use empirical waiting-time features.

Do not call overdue numbers “due”.

Test the hypothesis.

### I. REGIME-ADAPTIVE MODEL

Detect whether different historical periods favor different feature scales.

Avoid lookahead in regime classification.

### J. PAIR-RESIDUAL MODEL

Use pair co-occurrence only after subtracting/null-normalizing expected pair occurrence.

Strong regularization required.

### K. REGULARIZED LINEAR / LOGISTIC RANKER

Optional after classical models.

Train one row per:

`draw cutoff × number`

Target:

whether number appears in next draw.

Temporal folds only.

Rank 45 numbers by model score.

Do not call score calibrated probability unless calibration is independently proven.

---

# 31. OPTIONAL MACHINE LEARNING

ML is a challenger, not a promotion requirement.

Only add dependency such as scikit-learn if justified.

Recommended first ML:

- LogisticRegression with L1/L2/ElasticNet;
- HistGradientBoosting;
- simple learning-to-rank formulation if warranted.

Do not begin with:

- neural network;
- transformer;
- LSTM;
- reinforcement learning.

Dataset size does not justify complexity by default.

Simpler model wins when evidence is equivalent.

---

# 32. FEATURE NORMALIZATION

Current mixed features have different scales.

Before weight optimization:

- standardize continuous features;
- document direction;
- inspect distributions;
- clip/winsorize only with justification;
- avoid using future/global normalization parameters.

Normalization at target t may only use data available before t.

---

# 33. WEIGHT SELECTION

Never use Test to tune weights.

Use:

### Development temporal folds

Example rolling-origin folds.

Optimize pre-registered objective.

Then:

### Validation

select one champion.

Then freeze.

Avoid huge continuous hyperparameter search.

Prefer bounded interpretable search.

Record every tested configuration or search family.

---

# 34. OBJECTIVE FUNCTION

Do not optimize Jackpot containment directly due extreme sparsity.

Primary objective:

`Mean K @ Top18`

Potential tie-breakers in order:

1. lower MCP;
2. higher P(K≥4);
3. better compression AUC;
4. lower model complexity.

P(K=6) remains reported but should not dominate model discovery.

---

# 35. MODEL TOURNAMENT V2

Tournament structure:

```text
Random
    vs
HOT
    ↓
winner vs EWF
    ↓
winner vs MultiScale V2
    ↓
winner vs Momentum
    ↓
winner vs Mean Reversion
    ↓
winner vs Hazard
    ↓
winner vs Regime Adaptive
    ↓
winner vs Pair Residual
    ↓
optional Regularized ML
```

This diagram is conceptual.

Actual comparison must preserve multiplicity control.

---

# 36. MULTIPLE TESTING

Current window multiplicity protection must be extended to the broader research family.

Account for:

- windows;
- model variants;
- weight variants;
- feature variants;
- pool sizes where inferential claims are made.

Use:

- Holm-Bonferroni;
- hierarchical testing;
- or another justified familywise/FDR structure.

Document the family definition.

Do not perform 100 tests then quote only the best raw p-value.

---

# 37. ABLATION

For the eventual challenger/champion remove:

- frequency;
- gap;
- recency;
- momentum;
- mean reversion;
- stability;
- shrinkage;
- pair signal;
- regime component.

Classify each:

`HELPFUL`

`NEUTRAL`

`HARMFUL`

Remove harmful complexity.

---

# 38. RANDOMIZATION CONTROLS

Mandatory controls:

### Uniform random ranking

Expected no edge.

### Seed sensitivity

Many seeds.

### Shuffled chronology

Should destroy temporal signal.

### Synthetic IID Mega 6/45

Generate fair synthetic lottery history.

Research engine must not repeatedly “discover” reliable edge.

### Reverse peek

Intentionally include target winners.

Expected huge result.

Mark permanently:

`INVALID_AS_PREDICTIVE_EVIDENCE`

If reverse-peek does not dominate, test harness is broken.

---

# 39. MODEL FRAGILITY

Stress-test champion across:

- start date;
- end date;
- training length;
- lookback perturbation;
- seed;
- normalization choices;
- recent-history removal;
- early/middle/late eras;
- feature ablation.

If tiny changes destroy the result:

label:

`FRAGILE_SIGNAL`

Do not promote it.

---

# 40. EFFECT SIZE, NOT JUST P-VALUE

A model with:

`Mean K = 2.405`

vs

`2.400`

may be statistically detectable with enough observations but economically meaningless.

Define practical thresholds before promotion.

Report:

- absolute lift;
- relative lift;
- confidence interval;
- cost interpretation.

Do not promote trivial effects.

---

# 41. 18→7 COMPRESSION RULE

Do not independently cherry-pick a different model for every pool size at first.

Use the frozen 01–45 ranking.

Generate nested:

`Top18 ⊃ Top17 ⊃ ... ⊃ Top7`

Only after a ranking methodology shows defensible evidence may specialized pool-specific optimization be researched as a separate protocol.

---

# 42. COMPRESSION FRONTIER

For m = 18…7 calculate:

- model Mean K;
- random exact Mean K;
- delta;
- P≥3;
- P≥4;
- P≥5;
- P=6;
- MCP≤m;
- Bao tickets;
- cost;
- uncertainty;
- evidence status.

Plot:

### Pool size vs Mean K

### Pool size vs lift

### Pool size vs containment

### Pool size vs cost

### Cost vs evidence-adjusted performance

Do not label a cheaper pool “better” if containment simply collapsed.

---

# 43. COST INTERPRETATION

Always distinguish:

### Mathematical cost reduction

Bao15 costs less than Bao18.

from:

### Algorithmic efficiency

Whether selected Top15 performs above a random 15-number pool.

A cheaper pool does not prove better prediction.

---

# 44. PROSPECTIVE PROGRAMME

After selecting any new frozen champion:

create future prospective ranking before the target draw.

Store:

- target draw;
- ranking 01–45;
- Top7–Top18;
- model ID;
- model config hash;
- feature hash;
- dataset hash;
- protocol hash;
- timestamp;
- previous hash;
- record hash.

After official outcome:

append score.

Never rewrite freeze.

---

# 45. DATA SOURCE GUARANTEE

Production data source remains:

`vietlott.vn`

Verify:

- source URL allowlist;
- HTTPS;
- retry;
- timeout;
- redirect safety;
- response-size caps;
- parser failure;
- schema drift;
- incremental sync;
- duplicate protection;
- historical correction handling.

If source schema changes:

fail visibly.

Never silently return an empty dataset.

---

# 46. DATA INTEGRITY RED TEAM

Inject tests for:

- duplicate draw ID;
- same draw ID with changed numbers;
- invalid number 0;
- invalid number 46;
- duplicated number inside draw;
- missing six-number result;
- malformed date;
- reversed chronological ordering;
- truncated Vietlott page;
- empty history page;
- unexpected HTML schema.

Canonical dataset must not be corrupted.

---

# 47. PROVENANCE REPAIR

Audit relationships among:

- FINAL_VERDICT;
- experiment JSON;
- dataset hash;
- model hash;
- protocol hash;
- prospective freeze.

Every report reference must resolve.

No report may cite an absent artifact.

No experiment artifact may claim a dataset hash not present in the manifest.

Add automated verification.

---

# 48. EXPERIMENT IDENTITY

Experiment identity should derive from:

`dataset_hash`

`protocol_hash`

`model_config_hash`

optionally seed and experiment family.

Do not rely on filename timestamp alone.

---

# 49. CACHE CORRECTNESS

Audit Streamlit caching.

Cache keys for analytical results should include applicable:

- dataset hash;
- model ID;
- model version/config hash;
- protocol hash;
- lookback;
- pool size;
- seed.

Prospective mutable/status data must not be hidden behind stale long-lived cache.

---

# 50. UI SCIENTIFIC HONESTY

The UI must make the following visually obvious:

### Predictive edge

current evidence state.

### Random baseline

exact mathematical reference.

### Current candidate pool

experimental ranking result.

### Test status

confirmed / not confirmed.

### Prospective

pending / scored.

Never use marketing labels such as:

- best numbers;
- winning numbers;
- recommended jackpot numbers;
- AI prediction;
- high probability numbers.

Use:

`Experimental Candidate Pool`

or equivalent.

---

# 51. UX PRIORITY

Within 30 seconds a new user should understand:

1. what dataset is being used;
2. which model is shown;
3. what Top18 means;
4. how it compares with random;
5. whether evidence exists;
6. whether Test confirmed it;
7. whether prospective evidence exists;
8. how pool reduction affects cost and containment.

If those require reading raw JSON:

improve UI.

---

# 52. REMOVE RAW-JSON-FIRST UX

Raw JSON may remain under:

`Advanced / Debug`

but primary pages should communicate via:

- clear metrics;
- tables;
- charts;
- evidence badges;
- concise explanations.

Do not force normal users to interpret experiment internals.

---

# 53. PERFORMANCE

Profile:

- app startup;
- data load;
- feature computation;
- ranking;
- compression frontier;
- tournament;
- page rerender.

Avoid recomputing full historical walk-forward inside every Streamlit interaction.

Long research jobs belong in CLI/artifact generation.

UI should mostly consume artifacts.

---

# 54. OBSERVABILITY

Add structured events for:

- app startup;
- dataset load;
- dataset integrity failure;
- artifact load failure;
- ranking computation;
- cache hit/miss where useful;
- source sync;
- parser error;
- prospective chain verification.

Do not emit private or unnecessary data.

---

# 55. SECURITY REVIEW

Review:

- SSRF;
- redirect safety;
- malicious HTML;
- oversized responses;
- path traversal;
- unsafe deserialization;
- arbitrary pickle;
- dependency vulnerabilities;
- Docker non-root;
- secrets;
- external links.

Do not load untrusted pickle artifacts.

---

# 56. DEPENDENCY QUALITY

Review dependency pinning/reproducibility.

Consider:

- lock strategy;
- dependabot or equivalent;
- vulnerability scanning;
- `pip-audit`;
- secret scanning;
- SBOM only if justified.

Avoid enterprise ceremony without benefit.

---

# 57. DOCKER ACCEPTANCE

Build actual image:

```bash
docker build ...
```

Run it.

Open Streamlit in browser.

Repeat critical smoke journey.

Do not claim Docker support based only on Dockerfile syntax.

---

# 58. FAILURE-INJECTION BROWSER TESTS

At minimum simulate:

### Dataset absent

UI shows useful degraded message.

### Experiment artifact absent

A/B/Candidate pages fail gracefully.

### Corrupt prospective chain

Prospective/System Health visibly warn.

### Invalid manifest

System Health not green.

No raw traceback should become the user experience.

---

# 59. PRODUCTION SCORECARD

Score independently 0–10:

- Python architecture
- Data ingestion
- Data integrity
- Feature engineering
- Ranking engine
- Statistical methodology
- Temporal research protocol
- Multiplicity control
- Prospective governance
- Provenance
- Streamlit UX
- Browser correctness
- Responsive behavior
- Accessibility
- Test quality
- CI
- Security
- Observability
- Performance
- Docker/deployment
- Documentation
- Scientific honesty

Do not self-award 10 merely because code exists.

---

# 60. FEATURE 10/10 DEFINITION

A feature earns 10/10 only when all applicable links exist:

```text
SOURCE
↓
CORRECT ENGINE
↓
INTEGRATION
↓
UI / CLI SURFACE
↓
USER ACTION
↓
VISIBLE RESULT
↓
ERROR STATE
↓
UNIT TEST
↓
INTEGRATION TEST
↓
BROWSER TEST
↓
CI
↓
OBSERVABILITY
↓
DOCUMENTED LIMIT
```

Missing an applicable link means it is not 10/10.

---

# 61. HARD CAPS

Apply these independent caps:

### No real-browser E2E

Engineering score maximum:

`8.9/10`

### Mypy intentionally non-blocking

Code-quality/CI cannot be 10.

### Missing referenced artifact or broken provenance

Provenance maximum:

`7.9/10`

until fixed.

### Misleading predictive claim

Scientific/product score maximum:

`6.9/10`

### Data corruption possibility

Production-ready = false.

### Fabricated prospective result

Automatic scientific failure.

### Test/build/runtime browser failure

Production-ready = false.

---

# 62. ITERATION LOOP

Use repeatedly:

```text
AUDIT
↓
IDEATE
↓
FORM HYPOTHESIS
↓
INDEPENDENT REVIEW
↓
IMPLEMENT
↓
UNIT TEST
↓
PROPERTY TEST
↓
INTEGRATION TEST
↓
RUN RESEARCH
↓
BROWSER TEST
↓
RED TEAM
↓
COMPARE BASELINE
↓
KEEP / REVERT
```

Never keep a change merely because it is more sophisticated.

---

# 63. KEEP / REVERT RULE

Every algorithmic modification must produce a before/after comparison.

Keep only if it improves at least one justified objective without unacceptable regression.

Possible outcomes:

`KEEP`

`KEEP_EXPERIMENTAL`

`REVERT`

`REJECTED_NO_BENEFIT`

`REJECTED_OVERFIT`

`REJECTED_FRAGILE`

Record rejected experiments too.

---

# 64. NO SCORE GAMING

Red-team against these shortcuts:

- report says PASS but runtime fails;
- compile test presented as browser test;
- static screenshot presented as interaction test;
- Test used repeatedly for tuning;
- p-hacking windows;
- tweaking weights after viewing Test;
- only best seed reported;
- only positive metric shown;
- negative P4/P5 hidden;
- random baseline improperly simulated when exact formula exists;
- prospective file rewritten;
- missing artifact ignored;
- `continue-on-error` while claiming CI green;
- production verdict copied from old report.

Prevent them explicitly.

---

# 65. REQUIRED DELIVERABLES

Create/update:

### 1. `BASELINE_AUDIT.md`

Before-change reality.

### 2. `BROWSER_ACCEPTANCE.md`

Viewports, journeys, screenshots/traces, pass/fail.

### 3. `ALGORITHM_V2_RESEARCH.md`

All challengers, protocols, results, rejected models.

### 4. `PROVENANCE_AUDIT.md`

Artifact chain verification.

### 5. `PRODUCTION_SCORECARD.md`

Independent criterion scores.

### 6. `FINAL_VERDICT.md`

Updated only from verified evidence.

---

# 66. FINAL REPORT MUST SHOW

Exact:

- starting SHA;
- ending SHA;
- dirty/clean worktree;
- Python version;
- dataset latest draw;
- dataset record count;
- dataset hash;
- tests before/after;
- Ruff;
- Mypy;
- browser E2E;
- Docker smoke;
- baseline algorithms;
- new algorithms;
- selected champion;
- Dev metrics;
- Validation metrics;
- Test classification;
- prospective status;
- pool18 result;
- compression result;
- unresolved HIGH/MEDIUM risks.

---

# 67. ALGORITHM RESULT TABLE

Mandatory table:

| Model | Complexity | Mean K | Δ vs null | P4 | P5 | P6 | Mean MCP | Rank metric | CI | Adj p | Evidence |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---|

Separate:

- Development;
- Validation;
- previously observed historical holdout;
- prospective.

Do not mix them into one number.

---

# 68. COMPRESSION TABLE

Mandatory:

| Pool | Random Mean K | Model Mean K | Δ | P4 | P5 | P6 | MCP≤m | Tickets | Cost | Evidence |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|

for:

`18 ... 7`

---

# 69. FINAL SCIENTIFIC DECISION

Choose exactly one:

`NO_RANKING_EDGE_FOUND`

`EXPLORATORY_SIGNAL`

`VALIDATION_SIGNAL`

`HOLDOUT_SIGNAL`

`PROSPECTIVE_SIGNAL`

Never invent a stronger status merely because algorithm V2 is more sophisticated.

---

# 70. FINAL ENGINEERING DECISION

Choose exactly one:

`PRODUCTION_READY`

or

`NOT_PRODUCTION_READY`

Production-ready requires at minimum:

- clean required static checks;
- required tests green;
- real browser E2E green;
- data integrity green;
- provenance green;
- no unresolved HIGH;
- Docker/runtime verified if Docker claimed;
- no known critical user-path failures.

---

# 71. HUMAN CONTROL

Do not:

- push;
- merge;
- deploy;
- rewrite historical prospective records;
- delete scientific history

unless explicitly requested by the human operator.

Local changes and local browser testing are allowed.

If working in a Git repository, prefer a dedicated working branch.

---

# 72. PRIORITY ORDER

If resources are limited, execute in this exact order:

### P0

Baseline and reproduce current runtime.

### P1

Real browser audit.

### P2

Fix browser/runtime/data/provenance defects.

### P3

Make CI strict and add browser E2E.

### P4

Repair statistical inference.

### P5

Create Algorithm V2 baseline framework.

### P6

EWF + Multi-Scale V2 + Momentum vs Reversion.

### P7

Ablation and robustness.

### P8

Optional pair/regime/regularized ML challengers.

### P9

Compression 18→7.

### P10

Freeze prospective champion.

Do not invert these priorities.

---

# 73. CORE RESEARCH QUESTION

At every stage return to this:

> Using only information available before draw t, can the model produce a 01–45 ranking in which the six actual numbers of draw t occupy systematically better positions than an exact-random ranking, with an effect that survives temporal validation, multiplicity control, robustness tests and eventually prospective evaluation?

If the answer remains “no”:

do not disguise it.

The product still has value as a rigorous quantitative falsification laboratory.

---

# 74. FINAL PRINCIPLE

The goal is not:

`BUILD THE SMARTEST-LOOKING LOTTERY AI`

The goal is:

`BUILD THE HARDEST-TO-FOOL RESEARCH SYSTEM`

A strong result is one that survives attempts to disprove it.

A strong product is one that remains useful even when the final scientific conclusion is:

`NO_RANKING_EDGE_FOUND`.