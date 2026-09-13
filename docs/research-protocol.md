# Research protocol

This lab registers **hashable** research protocols. Changing any methodological field changes the protocol hash; experiment artifacts must pin that hash.

## Chronological split (50 / 25 / 25)

Draws are ordered by time (`draw_id` / `draw_date`). **Never shuffle.**

| Split | Fraction | Role |
| --- | --- | --- |
| Development | 50% | Explore features, windows, model variants |
| Validation | 25% | Select champion only |
| Test (holdout) | 25% | Confirm once after freeze — no tuning |

Champion is chosen on **Validation**, then **FREEZE**. Test only confirms. If Test fails: emit `HOLDOUT_SIGNAL_NOT_CONFIRMED` and open a **new** protocol — do **not** retune on Test.

## Freeze rules

1. Register protocol object (primary endpoint, alpha, lookbacks, model set, split rule, selection rule, multiple-testing method).
2. Compute `protocol_hash` (canonical JSON → SHA-256).
3. Select champion on Validation only.
4. Freeze model identity, feature version, lookback(s), dataset hash, and protocol hash.
5. Run Test once; record outcome.
6. Prospective work freezes **full ranking 01–45** (and nested top-18…top-7) **before** the future draw; scoring appends later (see [prospective.md](prospective.md)).

Evidence classification: a draw is **prospective** only if its id is at or after the protocol lock’s prospective start; earlier draws remain **retrospective** even if they fall in the Test slice chronologically.

## Round 1 models (no ML)

| ID | Name | Description |
| --- | --- | --- |
| **A** | HOT | Frequency ranking on a registered lookback (default 90). Top-18 = HOT18 baseline. |
| **B** | Multi-Scale Shrinkage | Windows 30/60/90/180/365/ALL; z-freq + gap + short-vs-medium / medium-vs-long momentum + long-run prior + stability; empirical-Bayes / weighted shrink so window 15 does not dominate. |
| **C** | Random | Seeded permutation of 01–45. |

Order of work: window tournament → model A/B sequence. If B does not beat A/C robustly, optional mean-reversion / adaptive-window follow-ups are allowed under a **new** registered protocol. Persistent failure → valid verdict `NO_RANKING_EDGE_FOUND`. Do **not** add ML in Round 1.

## Features and ranking contracts

- Features at cutoff `t` use only `draws < t`; every feature path calls `assert_no_future_leak`.
- Mandatory lookbacks: 15, 30, 45, 60, 90, 120, 180, 270, 365, 500, 750, 1000, ALL.
- Every model outputs a full permutation: `RankedNumber(number, score, rank)` for 01–45.
- Nested pools: `S7 ⊂ … ⊂ S18` = top-m of the **same** frozen ranking.

## Gate 45→18 and compression

Pool-18 requires Mean K > null **and** Validation+ **and** Test+ **and** practical **and** robust **and** no leak. Fail → `NO_VERIFIED_18_POOL_EDGE`. Compression 18→7 uses the frozen ranking only — no separate model per pool size `m`.

## Controls

Uniform random, seeded random, shuffled-history, synthetic fair lottery. Reverse-peek (force winners to top) must show 100% containment and is labeled `INVALID_AS_PREDICTIVE_EVIDENCE`.
