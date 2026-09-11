# Phase 5 Build Plan — Model Validation & Monitoring — Lending Club

**Status as of this writing: not started.** This phase is different in kind
from Phases 1–4: it doesn't produce a new model, it **tests the ones already
built** — and unlike every other phase, part of it can start as soon as
Phase 1 (PD) exists, without waiting for LGD/EAD/ECL. This is the closing
phase of the core Lending Club modeling chain the user asked for ("the end"
of PD → LGD → EAD → ECL → validation) — see §6 for what falls outside that
chain and is deliberately not part of this phase.

---

## 1. What Phase 5 is, and an important scope note

The `credit-risk-curriculum` skill's own reference material for this phase
(`08-model-validation-and-monitoring.md`) is written specifically around
**PD validation** — it names an exact notebook
(`04_modeling/NN_pd_validation.ipynb`), sequenced right after the PD
scorecard, and every worked number in it (baseline AUC CI, `int_rate` PSI,
concentration HHI) is PD/EDA-side, already sitting in this project. **No
reference file in this skill set yet gives the same depth of detail for
validating LGD, EAD, or the assembled ECL number** — those need the same
SR 11-7 framework (§5) applied by analogy, not a ready-made checklist. This
build plan is explicit about that gap rather than inventing LGD/EAD/ECL
validation detail that doesn't exist in the project's own reference
material yet.

**Practical sequencing implication:** the PD-validation section below (§2–4)
can be built as soon as Phase 1 exists — it does not need to wait for
Phases 2–4. The LGD/EAD/ECL validation extensions (§6) genuinely do need
their respective phases to exist first.

---

## 2. Discriminatory power — the project already has one real number to reconcile against

- **No verified prior baseline exists — corrected, do not cite the old
  figure.** An earlier draft of `phase_1_build_plan.md` cited a Phase 0
  logistic AUC bootstrap 95% CI of [0.695, 0.698]; this does not reproduce
  against live data (multiple re-derivation variants during Phase 1
  planning consistently landed at 0.68–0.69 AUC instead — see
  `phase_1_build_plan.md` §11 for the full reproduction table). **Whatever
  Phase 1's own notebook produces on its own train/test/OOT split is this
  project's real baseline** — pull that number live from Phase 1's fitted
  model and its saved model card (§18 of that plan), don't re-cite either
  figure from memory.
- **Concrete build**, mapped onto KB §15.1.1's shared bucket construction
  (one bucketed table drives ROC/AUC, KS, and CAP):
  1. Score the fitted PD model (Phase 1's output) on `windowed` or a
     held-out slice; bucket predicted PD into ~20 buckets (a practical
     default given ~1.2M rows; KB's own worked example uses 67).
  2. Compute cumulative good/bad rate per bucket; write this table to
     `ASSETS_TABLES` — it is the base object every statistic below reuses.
  3. **ROC/AUC**: recompute via `sklearn.metrics.roc_auc_score`; cross-check
     it reconciles with Phase 1's own reported test/OOT AUC (from that
     notebook's model card, §18 of `phase_1_build_plan.md`) — same model,
     same population, should not silently drift. There is no separate,
     independently-cited historical figure to reconcile against.
  4. **Gini** = `2×AUC − 1`, reported alongside AUC, not computed separately.
  5. **KS** = `max |cumulative bad rate − cumulative good rate|` from the
     same bucket table — genuinely new to this project, one line of code
     once the bucket table exists.
  6. **CAP/Accuracy Ratio**: same bucket table, re-axised (cumulative % bad
     vs. cumulative % of population); confirm `Accuracy Ratio = Gini` as an
     internal consistency check, not a separate finding.
- **F1 vs. accuracy**: the population is 20.5% bad — not extreme, but
  imbalanced enough that raw accuracy misleads (predicting "always good"
  clears ~79.5% accuracy while being useless). Report precision/recall/F1
  at the KS-optimal cutoff alongside AUC; don't lead with accuracy.
- **IV/WOE as a validation diagnostic**: not new work — apply the same
  WOE/IV logic to the **fitted score/output grade bucket** itself, the same
  question already asked of `grade`/`int_rate` individually in Phase 0.
- Rank-correlation measures (Gamma, Somers' D, Kendall's Tau-b) and the
  Pietra Index are optional depth-adds, not required for a first pass — the
  AUC/Gini/KS/F1 set covers this pillar adequately for this project's scope.

---

## 3. Stability — PSI, already computed once, just not yet framed as model stability

- **Existing result**: Phase 0's EDA computed PSI on `int_rate` (2013 vs.
  2017 vintage) = **0.140** (moderate drift) — this is not a preview of PSI
  methodology, it is KB §15.2's exact PSI formula already correctly applied.
  What's missing is the framing: it was an EDA/feature-drift finding, not a
  named "model stability" deliverable.
- **The concrete gap this phase closes**: KB §15.2 distinguishes PSI
  (applied to the overall score/grade distribution) from CSI (per input
  characteristic) — the existing `int_rate` PSI is CSI-style. This phase
  needs the PSI-proper version: bucket the **fitted PD score** (or final
  rating grade) into a development-vs-application split and compute PSI on
  that distribution, not on any one input feature.
- **Reuse the proven pattern** — two natural splits: (a) development window
  (2013–2015) vs. later window (2016–2017) as the "application" period; (b)
  `windowed` (2013–2017, in-model) vs. any years Phase 0 currently excludes,
  if/when those become available as an out-of-time sample.
- **Concentration**: HHI is already computed (528, geographic). Same
  reframe applies — decide whether grade-level/score-band-level
  concentration also warrants an HHI cut, rather than redoing the
  geographic one.
- **Interpretation thresholds to state explicitly** next to any PSI result
  (KB gives no universal cutoff, but the field convention consistent with
  reading 0.140 as "moderate" is: <0.10 stable, 0.10–0.25 moderate/monitor,
  >0.25 material/consider rebuild) — cite this in the notebook's markdown
  rather than leaving "moderate" unexplained.

---

## 4. Calibration accuracy — testing, not building (cross-reference Phase 1, don't repeat it)

Phase 1 (§ its own build plan, informed by KB §10.3) covers the calibration
**build** — this phase covers calibration **testing**, a distinct concern:
does the already-calibrated score still match reality, checked
independently.

- **Hosmer-Lemeshow test**: grouped chi-square comparing expected vs.
  observed goods/bads across score deciles/grades — a one-cell addition
  once Phase 1's calibrated PD exists, reusing the same decile/grade
  grouping as §2's bucket table. High p-value = good fit.
- **Brier score**: `mean((actual_default − predicted_PD)²)` — one line
  against `is_bad` and the fitted PD column, reported as a scalar alongside
  Hosmer-Lemeshow.
- **K-Score / Vasicek / Jeffrey's Bayesian** (Low-Default-Portfolio tools):
  **out of scope** — `windowed`'s ~245K defaults is not an LDP in any grade
  of practical interest here. Flag as out of scope unless a specific thin
  sub-segment (grade G, or a rare `addr_state_grouped` bucket) turns up a
  genuinely low-default cell later.

---

## 5. SR 11-7 framing — closing markdown, not a regulatory requirement

This project is a personal portfolio build on public data, not a regulatory
submission — but SR 11-7's three-pillar structure (conceptual soundness,
ongoing monitoring, outcomes analysis) is the vocabulary Devesh's actual
work environment (credit risk at LBG via EXL) uses, so mapping this
notebook's own content onto it is a genuine demonstration of the framework,
worth doing explicitly:

- **Conceptual soundness**: did the scorecard's variable choices have a
  documented economic rationale (Phase 1's IV-driven feature selection,
  `grade`'s near-definitional status stated rather than hidden)?
- **Outcomes analysis**: §2's AUC/KS/Gini re-derivation, §4's
  Hosmer-Lemeshow/Brier check, both against data the model wasn't fit on
  where possible.
- **Ongoing monitoring**: §3's PSI re-application to the fitted score,
  positioned as the recurring check a real monitoring cadence would repeat.
- **Three Lines of Defense / validation-type taxonomy** (Initial / Periodic
  / Annual / OPA): worth one summary paragraph for context — there is no
  LoD2/LoD3 in a solo portfolio project. State that plainly rather than
  manufacturing a governance structure that doesn't exist here.
- **Early Warning Signals**: operate at the individual-account level and
  don't map to a static historical dataset with no live account monitoring —
  explicitly out of scope, for the same reason a live-monitoring dataset
  doesn't exist here.

---

## 6. Extending validation to LGD, EAD, and the ECL assembly — a real gap, not filled here

No reference file yet gives LGD/EAD/ECL the same depth of validation detail
as PD gets in §2–5. **This build plan does not invent that detail** — it
flags what the analogous work should cover, by extension of the same
SR 11-7 structure, once Phases 2–4 exist:

- **LGD validation**: calibration accuracy of the fitted recovery-rate
  model against realized recoveries (an LGD-appropriate analogue of
  Hosmer-Lemeshow/Brier — e.g. an R²/pseudo-R² comparison, or a
  predicted-vs-actual recovery-rate scatter by segment); stability of the
  segment-level LGD curve across vintages, echoing §3's PSI logic but
  applied to LGD-by-grade rather than PD-by-grade.
- **EAD validation**: how well the expected-exposure curve (Phase 3)
  predicts realized exposure-at-charge-off for loans that actually
  defaulted — this is partially already built into Phase 3 itself (its own
  validation-against-`Charged Off`-realized-exposure step), so this phase's
  job is to confirm that check still holds on any new data, not to build it
  from scratch again.
- **ECL validation**: does the assembled ECL number (Phase 4) track
  realized losses over time as vintages mature? This needs a forward
  monitoring cadence this static historical dataset can only partially
  simulate (by holding out the most recent vintage as a pseudo-"future"
  check) — flag this limitation explicitly rather than presenting a
  backtest on historical data as equivalent to live monitoring.

This section should be revisited and filled in with the same rigor as §2–5
once Phases 2–4 are actually built, rather than treated as complete now.

---

## 7. Notebook structure — cell-by-cell plan (PD validation; §6 by extension later)

1. **Intro + cell-map** — standard front matter; explicit note that this
   notebook covers PD validation now, with LGD/EAD/ECL validation as a
   planned extension once those phases exist (§6).
2. **Section: population/scoring** — connect via direct
   `duckdb.connect(DUCKDB_FILE, read_only=True)`; score `windowed` (or a
   held-out slice) with Phase 1's fitted PD model.
3. **Section: bucket table** — goods-vs-bads bucketing (~20 buckets),
   cumulative good/bad rate, written to `ASSETS_TABLES`.
4. **Section: discriminatory power** — ROC/AUC (reconciled against Phase
   1's own reported test/OOT AUC, per its model card — no separate
   historical figure exists to check against, §2), Gini, KS, F1 at the
   KS-optimal cutoff (§2).
5. **Section: stability** — PSI on the fitted score, development-vs-
   application split, reusing Phase 0's exact vintage-split pattern (§3).
6. **Section: calibration testing** — Hosmer-Lemeshow, Brier score against
   the 20.5% pooled bad rate (§4).
7. **Section: SR 11-7 mapping** — closing markdown cell mapping the above
   onto conceptual soundness / ongoing monitoring / outcomes analysis (§5).
8. **Section: forward pointer** — explicit note that §6's LGD/EAD/ECL
   validation extensions are the next work once those phases exist; not a
   deliverable of this notebook.

---

## 8. Checklist — what is built vs. what is left

**Built: nothing.**

- [ ] Confirm Phase 1 (PD scorecard) is complete — this section can start
  as soon as it is, without waiting for Phases 2–4.
- [ ] Confirm notebook location, following prior phases' resolved decision.
- [ ] Bucket table built and written to `ASSETS_TABLES`.
- [ ] AUC/Gini/KS/F1 computed and reconciled against the existing baseline
  CI.
- [ ] PSI computed on the fitted score (not just `int_rate`), with
  interpretation thresholds stated explicitly.
- [ ] Hosmer-Lemeshow and Brier score computed against the calibrated PD.
- [ ] SR 11-7 closing mapping written.
- [ ] LGD/EAD/ECL validation extensions (§6) explicitly logged as a planned
  follow-up, revisited once Phases 2–4 exist.
- [ ] Standard production-readiness audit before calling this section of
  Phase 5 done.
- [ ] Commit only the new notebook file, same git discipline as every prior
  phase.

---

## 9. Past → present → future — and the end of this chain

- **Past:** Phase 0's EDA already produced two of this phase's core
  numbers (baseline AUC CI, `int_rate` PSI) without knowing they'd later be
  reused as formal validation evidence. Phases 1–4 (once built) are what
  this phase tests.
- **Present:** this plan — the PD-validation section (§2–5) is fully
  specified and buildable now; the LGD/EAD/ECL extension (§6) is
  deliberately left as a flagged gap, not invented content.
- **Future — this is "the end" of the core chain the user asked for.**
  Once Phase 5's PD validation is built and its LGD/EAD/ECL extensions are
  filled in as Phases 2–4 land, the Lending Club PD/LGD/EAD/IFRS9-CECL
  modeling stack is complete end to end. What comes after that is
  explicitly **not** part of this five-phase chain, and should not be
  folded into it without a fresh decision:
  - **Regulatory capital & stress testing** (KB §18) and an **ML challenger
    model** (KB §16) are both "as needed alongside" material per the
    `credit-risk-curriculum` skill's own routing table — illustrative
    exercises once the core stack exists, not sequential phases.
  - **Expanding to the other six datasets** (Fannie Mae, Home Credit,
    Taiwan Credit Default, HMDA, Give Me Some Credit, German Credit) is a
    separate, larger undertaking — each would need its own Phase 0 before
    any of Phases 1–5 above apply to it, and is out of scope for "next
    phases" as used in this document chain.

---

## 10. References

- `docs/phase_0_report.md` through `docs/phase_4_build_plan.md` — every
  prior phase.
- `docs/Peaks2Tails_Knowledge_Base.md` §15 (Model Validation & Monitoring).
- `credit-risk-curriculum` skill, reference file
  `08-model-validation-and-monitoring.md` — full PD-validation bridge detail
  this document condenses. No equivalent reference file yet exists for
  LGD/EAD/ECL validation depth (§6) — build that analogously when the time
  comes, or ask for the skill to be extended with a new reference file per
  its own stated growth pattern (reference file 01 §1.4: "a new numbered
  reference file per newly-unlocked concept cluster").
