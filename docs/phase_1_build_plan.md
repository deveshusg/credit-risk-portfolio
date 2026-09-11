# Phase 1 Build Plan — PD Account-Level Scorecard (Lending Club)

**Status as of this writing: not started. Nothing in this document has been
built.** This is v3 of this plan — rebuilt from scratch against 10 real
external sources chosen to mirror actual bank scorecard practice (§0), after
v2 fixed the location/baseline issues but was still missing three things
every one of these sources treats as core to a real bank build: vintage/
roll-rate analysis, reject inference as an in-scope step (not a deferred
follow-on), and scaling-to-points with adverse-action reason codes. All
three are now first-class sections below. The changelog at the bottom
tracks what changed between v1 → v2 → v3.

This document is written to be self-sufficient: an agent with no other
context should be able to read this file alone and know exactly what to
build, why, in what order, against which real data, and what "done" looks
like — without needing to re-derive anything from the KB, the external
sources, or Phase 0 from scratch.

---

## 0. The 10 sources this plan is built against

Requested explicitly: 10 well-regarded, independent sources covering the
combination of roll-rate/vintage analysis, WOE binning, logistic regression,
reject inference, and validation — the actual end-to-end shape of a bank
application scorecard build, not just the modeling core. Chosen for
diversity of source type (industry-standard text, vendor methodology,
vendor toolkit docs, academic/regulatory paper, practitioner blog, open
implementation) rather than 10 versions of the same tutorial.

| # | Source | Type | What it grounds in this plan |
|---|---|---|---|
| 1 | Naeem Siddiqi, *Credit Risk Scorecards: Developing and Implementing Intelligent Credit Scoring* (Wiley) — 2nd ed. retitled *Intelligent Credit Scoring* | Industry-standard book | The book virtually every other source below cites as the reference; underlies the fine/coarse-classing, WOE/IV, and KGB/KIGB vocabulary used throughout |
| 2 | SAS Institute, "Developing a Credit Risk Model Using SAS" (SAS Global Forum, Paper 3554-2019) | Vendor methodology paper | The 11-step KGB→KIGB acquisition-scorecard process (§5 onward); SPM window framing (§4); scaling parameters and reason codes (§16); 3-team governance framing (§19) |
| 3 | SAS Institute, "Reject Inference Techniques Implemented in Credit Scoring" (SAS Global Forum, Paper 305-2009) | Vendor methodology paper | Cross-check on reject-inference technique tradeoffs (§12) |
| 4 | MathWorks, "Case Study for a Credit Scorecard Analysis" (Risk Management Toolbox docs) | Vendor toolkit documentation | The concrete fit→scale→score→validate sequence (§9, §16, §17); confirms this project's own step order isn't idiosyncratic |
| 5 | MathWorks, "Use Reject Inference Techniques with Credit Scorecards" | Vendor toolkit documentation | Fuzzy augmentation vs. hard-cutoff mechanics (§12); the "score rejects with the accepts-only model, merge, refit" workflow shape |
| 6 | Huang & Scott (University of Edinburgh Credit Research Centre), "Credit Risk Scorecard Design, Validation and User Acceptance" | Academic/regulatory-oriented paper | Development-vs-OOT-vs-TTD population framing (§7); the finding that reject inference alone rarely explains OOT degradation — tempers how much weight this plan puts on reject inference "fixing" performance (§12) |
| 7 | YOU CANalytics, "Information Value (IV) & Weight of Evidence (WOE) – Banking Case Study" | Practitioner blog (banking-analytics) | The IV-strength table (§9) and the "broad-based model over one dominant variable" caution applied to the grade/int_rate decision (§10) |
| 8 | YOU CANalytics, "Reject Inference & Scorecards – Banking Case" (5-part series) | Practitioner blog (banking-analytics) | Parceling vs. fuzzy augmentation mechanics compared directly against this project's actual rejected-file field constraints (§12) |
| 9 | ListenData, "Credit Risk: Vintage Analysis" | Practitioner blog | Vintage-curve/MOB methodology (§6) |
| 10 | Tanuka Mandal, "Roll Rate Analysis and Vintage Analysis in IFRS 9" | Practitioner blog (IFRS 9-focused) | Roll-rate/DPD-transition-matrix definition (§6) — used here mainly to establish **why** this technique does **not** transfer to Lending Club's data, not to build one |

Every technique borrowed from these sources is re-verified against this
project's own live data before being written into a notebook cell, per the
evidence-in-code rule — a source establishing "this is how banks do it"
is not the same as this project's own number, and the two are never
conflated (§3, rule 1; this is exactly the mistake v1→v2 corrected for the
baseline AUC).

---

## 1. What Phase 1 is, and why it's structured as two notebooks now

Phase 1 = building the first working PD (Probability of Default) model for
Lending Club: an **account-level, application scorecard**. Every one of the
10 sources in §0 treats an application-scorecard build as ending with a
production scorecard that has had reject inference applied (the SAS paper's
own final deliverable is the **KIGB** model, not the accepts-only **KGB**
model) — not as a scorecard with reject inference bolted on later "if
there's time." v1/v2 of this plan deferred reject inference as a follow-on;
that undersells what "closely imitates actual bank working" means, per the
explicit brief this revision was written against.

**Structural consequence — a real decision, stated explicitly, not silent:**
building the KGB scorecard (1,195,879 accepted loans) and the reject-
inference/KIGB step (27,648,741 rejected applications, §4) in one notebook
would mix two very different data-scale, data-shape problems into one file,
against this project's own convention of one clear unit of work per
notebook (Phase 0's 14 EDA notebooks each covered one dimension). **Phase 1
is therefore two notebooks, both under the same `phase1_pd_modeling/`
folder:**

| Notebook | Covers |
|---|---|
| `01_pd_kgb_scorecard.ipynb` | §5–§11, §13–§18: accepts-only scorecard, from partition through persistence |
| `02_pd_reject_inference_kigb.ipynb` | §12: loads the rejected-applicant file, performs reject inference, builds and validates the KIGB scorecard against the KGB baseline |

This is a change from v2's single-notebook assumption — flagged here for
Devesh's sign-off before either notebook is created, same as any other
structural decision in this project.

**Why PD first, specifically, and why now:** unchanged from v2 — see the
prior version's §1 reasoning (LGD/EAD need PD-adjacent concepts;
`PD × LGD × EAD` is Phase 4's formula; Phase 0's audit found zero blocking
issues).

---

## 2. Where this lives

```
phase1_pd_modeling/
  01_lendingclub/
    notebooks/
      01_pd_kgb_scorecard.ipynb            <- §5-§11, §13-§18
      02_pd_reject_inference_kigb.ipynb    <- §12
    models/
      pd_scorecard_kgb_v1.joblib            <- §18
      pd_scorecard_kigb_v1.joblib           <- produced by notebook 02
```

Confirmed with Devesh (v2): a new top-level folder, mirroring
`phase0_data_platform/01_lendingclub/`'s own dataset-subfolder convention.

---

## 3. Non-negotiables (unchanged from v2, restated for self-sufficiency)

1. **Evidence-in-code** — every markdown claim backed by a printed number in
   the same notebook. Numbers cited in this document from the 10 external
   sources (§0) or from this session's own pre-build scouting (§4, §6, §11)
   are **not** substitutes for the notebook's own live computation — restate
   and re-derive, don't import as fact. This rule caught a real, previously
   undetected error in v1 of this document (an unreproducible baseline AUC)
   — treat it as load-bearing.
2. **Direct DuckDB connection** — `duckdb.connect(DUCKDB_FILE, read_only=True)`
   inline in each notebook, not the skill's stale `nb_setup.py` reference.
3. **No premature narrowing outside `03_data_cleaning`** — any feature
   considered and dropped needs an explicit, evidenced decision cell.
4. **Technique justification** — every point this notebook picks one
   technique over a plausible alternative (drawn from the tradeoffs the 10
   sources in §0 actually disagree on — e.g. fuzzy augmentation vs.
   parceling, pooled vs. per-vintage calibration) gets a markdown cell
   answering "why this, not that," marked **[TJ]** in the cell plans below.

**Explain before building; executive style; no `tabulate`** — unchanged
from v2.

---

## 4. Data inputs — both populations, and the constraint that matters most

**Accepted population (`windowed`):**
- 1,195,879 rows, live-confirmed. Every field `VARCHAR` in DuckDB — cast
  explicitly. `sub_grade` present and fully populated (35 distinct values).
  Full field dictionary in `docs/phase_0_report.md` §4.
- `loan_status` has exactly **3 values** in `windowed`: `Fully Paid`
  (950,468), `Charged Off` (245,378), `Default` (33) — this is the matured/
  final-disposition population by construction, **not** a delinquency-bucket
  snapshot. This fact directly shapes §6's scope decision.

**Rejected population (`rejected_2007_to_2018Q4.csv.gz`) — the file every
prior version of this plan named but never actually opened:**
- **27,648,741 rows**, live-counted this session — roughly **23× the size**
  of the accepted population. Confirms the real scale of Lending Club's
  through-the-door (TTD) population that KB §8.2 and every reject-inference
  source in §0 assume exists.
- **Only 9 columns**: `Amount Requested`, `Application Date`, `Loan Title`,
  `Risk_Score`, `Debt-To-Income Ratio`, `Zip Code`, `State`, `Employment
  Length`, `Policy Code`. **This is the single biggest practical constraint
  on §12** — `grade`, `int_rate`, `purpose`, `home_ownership`, and every
  other accepted-only field simply do not exist for rejects. Reject
  inference here can only use the fields that overlap: `Risk_Score` (a
  FICO-like proxy, not necessarily the same scale as `fico_range_low`),
  DTI, loan amount, state, and employment length.
- **`Policy Code` distribution** (live-counted): `0` → 27,559,694 (99.68%),
  `2` → 88,129 (0.32%), null → 918. Per KB §8.2's own rule ("policy
  rejects — No"), the code-`0` population are automatic policy rejects that
  never reached a score-based decision and should be **excluded** from
  reject inference, not merged in wholesale. **This leaves an unconfirmed,
  possibly very small, actually-usable reject population** — code `2`'s
  88,129 rows is the working hypothesis, but what code `2` specifically
  means for Lending Club must be confirmed via `Risk_Score`'s null rate and
  distribution within each code, live, before assuming it's the "scored but
  declined" population §12 needs. **Do not assume this mapping — verify it
  as the first cell of notebook 02.**
- **Vintage/timing fields for §6**: `issue_d` and `last_pymnt_d` both exist
  and are usable — live-checked: 243,734 / 245,378 (99.3%) of `Charged Off`
  loans have a non-null `last_pymnt_d`, giving `DATEDIFF('month', issue_d,
  last_pymnt_d)` as a workable months-on-book-at-last-activity proxy (sample
  values live-checked: 7, 13, 9, 12, 3, 4, 11 months).

---

## 5. Event & window definition — restate before modeling anything

Every source in §0 that gives a full process (SAS 3554-2019 step 1; Huang &
Scott) opens with this, and it has never been an explicit step in this
project's own plan before — it was implicitly inherited from Phase 0's
`windowed`/`matured` table construction without being restated here.

- **Bad definition**: `is_bad` (already built into `windowed`) — restate its
  exact construction rule live (which `loan_status` values map to bad;
  confirm `Default`'s 33 rows are included as bad, not silently dropped as
  a rounding error).
- **SPM windows** (Sample / Performance / Measurement, per SAS 3554-2019):
  - *Sample window*: the `issue_d` range loans were originated in
    (2013–2017, per §5-of-v2's live-checked `issue_year` table).
  - *Performance window*: however long Phase 0's `matured`/`windowed`
    construction waited before calling a loan's outcome final — **this must
    be restated from Phase 0's ingestion notebook's own logic**, not
    assumed, since §6's vintage curve needs to know whether every vintage in
    scope has actually had enough time to mature or whether later vintages
    (2016, 2017) are systematically under-observed relative to 2013–2014.
  - *Measurement window*: the point at which `is_bad` is read off (i.e.
    `loan_status` at data-pull time) — already implicit in `windowed` but
    worth one restated sentence for a reader with no other context.

---

## 6. Vintage & cohort default-timing analysis — new section, and an explicit scope boundary

**What the 10 sources call this, and why it doesn't fully transfer:**
Tanuka Mandal's IFRS 9 roll-rate methodology (source 10) describes a
**monthly DPD-bucket transition matrix** (Current → 1-30 → 31-60 → 61-90 →
90+), built from repeated monthly snapshots of the same loan. **Lending
Club's public accepted-loan file is a single snapshot per loan, not a
monthly panel** — `windowed`'s `loan_status` has exactly 3 terminal values
(§4), confirming there is no intermediate delinquency-bucket history to
build a transition matrix from. **A literal roll-rate/DPD-transition-matrix
analysis is not buildable from this data — say so explicitly in the
notebook rather than force a proxy that misrepresents what a real bank's
roll-rate analysis actually is.** This is the same honesty standard already
applied to EAD/CCF (Phase 3 plan) and the DPD-based SICR proxy (Phase 4
plan) — don't invent a fictitious version of a technique this dataset can't
support.

**What *is* buildable, and is genuinely useful — ListenData's vintage-curve
methodology (source 9):**
- For each `issue_year` cohort, compute the distribution of
  months-on-book-at-charge-off (`DATEDIFF('month', issue_d, last_pymnt_d)`
  for `loan_status = 'Charged Off'`, §4) and plot the cumulative bad rate
  against MOB, one curve per cohort.
- **Direct use for this project**: validates whether the earlier vintages
  (2013–2014) have actually stabilized (curve flattens) while confirming
  whether 2016–2017 cohorts are still "developing" — i.e. whether Phase 0's
  `windowed`/`matured` definition already accounts for immaturity bias, or
  whether it doesn't and the 2017 OOT slice (§7) is systematically
  under-counting bad loans that simply haven't had time to charge off yet.
  **This is a real risk to the OOT split's validity that no prior version
  of this plan checked for.**
- **Secondary use**: a vintage curve comparing 2013 vs. 2017 cohort shape is
  a second, independent lens on the same drift `int_rate` PSI (0.140,
  Phase 0) already flagged — if 2017's default-timing curve is
  systematically faster or slower than 2013's, that's corroborating (or
  contradicting) evidence for the TTC/PIT decision (§14).

This section is **diagnostic, not a modeling input** — its output is a
markdown finding (does `windowed` already handle immaturity correctly?) and
a plot, not a feature. Its finding is a **[TJ]**-flagged input to §7 (does
the 2017 OOT slice need adjustment?) and §14 (TTC/PIT).

---

## 7. Data partition — train / validation / test / OOT (unchanged from v2, restated)

| Group | Definition | Rows (live-checked) |
|---|---|---|
| OOT | `issue_year = 2017`, held out entirely | 169,321 (14.2%) |
| Train | Random, stratified on `is_bad`, from `issue_year` 2013–2016, 60% | ≈615,935 |
| Validation | Same pool, 20% — every "which option wins" comparison | ≈205,312 |
| Test | Same pool, 20% — touched once, after all decisions locked | ≈205,311 |

Re-verify against §6's finding before finalizing: if 2017 turns out to be
materially immature (undercounting bads), state that explicitly as a caveat
on the OOT metric in §11/§17 rather than silently reporting it as
comparable to test.

WOE bin edges (§9) are fit on train only, applied unchanged to
validation/test/OOT — unchanged from v2.

---

## 8. Feature engineering vs. feature selection (unchanged from v2, restated)

- **Engineering**: minimal by design — `issue_year`/vintage derivation from
  `issue_d` (also feeds §6); WOE transformation *is* the engineering step
  for categorical/binned-numeric candidates (**[TJ]**: WOE vs. one-hot/
  target encoding — monotonicity, missing/rare-category handling,
  interpretable coefficients).
- **Selection**: IV-threshold filter (table below, source 7), applied on
  train; multicollinearity check on WOE-transformed candidates; stepwise
  elimination flagged optional.

| IV range | Classification (source 7 / Siddiqi convention) |
|---|---|
| < 0.02 | Useless |
| 0.02–0.1 | Weak |
| 0.1–0.3 | Medium |
| 0.3–0.5 | Strong |
| > 0.5 | Suspicious — review for leakage/near-definitional risk |

---

## 9. Fine classing, coarse classing, WOE/IV

Unchanged methodology from v2 (~20 bins fine, ≤8 coarse, >2%-population,
>50-bads, monotonic WoE, all as live asserts) — **[TJ]** manual rule-based
classing vs. an automated optimal-binning library (`optbinning`): manual
chosen for auditability, consistent with this project's evidence-in-code
ethos (source 4's MathWorks toolkit auto-bins first, then requires manual
review for the same reason — automated binning is a starting point, not a
substitute for a reviewed, monotonic result).

`grade` IV = 0.4806 (live-verified this session, train 2013–2016) — close
to source 7/KB's own convention-based 0.47; treat as the sanity-check
target for the notebook's own re-derivation, not a value to hard-code.

---

## 10. Grade/int_rate near-definitional decision (unchanged from v2)

Option A (keep both, document why) vs. Option B (engineer around them,
`dti` as the leading mechanistic alternative) — **[TJ]** cell, citing live
IV. Source 7's caution against "over-dependence on one dominant variable"
is the additional citation for why this decision matters, not just KB's own
IV-suspicion threshold.

---

## 11. KGB scorecard fit & baseline validation (`01_pd_kgb_scorecard.ipynb`, close-out of the accepts-only build)

- Logistic regression on the WOE-transformed, selected feature set (§8),
  fit on train — **[TJ]** logistic regression vs. tree/GBM (interpretability
  + WOE-linearity + regulatory explainability, per KB §8.1 and every source
  in §0 that states a technique preference at all).
- **Baseline — corrected in v2, restated here:** no verified prior baseline
  exists in this repo. Live re-derivation this session (multiple
  feature/split variants) consistently landed at **0.68–0.69 AUC**, not the
  fabricated [0.695, 0.698] a v1 draft cited from a skill reference file
  without re-deriving it. Whatever this notebook's own train/test/OOT split
  produces *is* the project's real baseline — report with a bootstrap CI on
  **both** test and OOT, and treat a large in-time/OOT gap as a finding
  (possibly connected to §6's immaturity check), not noise to average away.

---

## 12. Reject inference — `02_pd_reject_inference_kigb.ipynb` (new: brought into Phase 1's actual scope)

Every source in §0 that covers reject inference (1, 2, 3, 5, 6, 8) treats it
as a real step with real limitations, not a checkbox. This section is
written accordingly — including the parts where the honest answer is "this
dataset makes that harder than the textbook version."

**Step-by-step (SAS 3554-2019's KGB→KIGB shape, source 2, adapted to this
project's actual field constraints, §4):**

1. **Load the rejected file** (27,648,741 rows) via DuckDB's CSV reader
   (not pandas — the earlier live OOM-kill of a full-file pandas load this
   session is itself evidence for why: cite it as a live technical note).
2. **Exclude policy rejects** — filter to `Policy Code = 2` (88,129 rows,
   live-counted) as the working "scored, not policy-rejected" population,
   **after confirming live** (via `Risk_Score`'s completeness/distribution
   within each code) that code `2` is actually the scored population and
   not something else — do not assume the mapping from this document.
3. **Map overlapping fields only**: `Risk_Score` (proxy for
   `fico_range_low`/`fico_range_high` — state explicitly that this is a
   proxy, not confirmed to be on the same scale, and check its range/
   distribution against `fico_range_low`'s known range as a sanity check),
   `Debt-To-Income Ratio` → `dti`, `Amount Requested` → `loan_amnt`
   (proxy — requested, not funded), `State` → `addr_state`, `Employment
   Length` → `emp_length`. **`grade`, `int_rate`, `sub_grade`, `purpose`,
   `home_ownership` have no reject-file equivalent — any KGB model term
   built on them cannot be scored on rejects at all.** This is the
   practical reason the grade/int_rate decision (§10) matters twice: if
   Option A (keep grade/int_rate) is chosen for the main KGB model, a
   **separate, overlap-only sub-model** (fit on train using only the fields
   §4 confirms exist on both populations) is what actually scores the
   rejects — state this explicitly, it is not optional plumbing.
4. **Score rejects with the overlap-only sub-model.**
5. **Reject-inference technique — [TJ] fuzzy augmentation, chosen over
   parceling and hard-cutoff** (sources 3, 5, 8 all describe these three;
   source 8's own conclusion — fuzzy augmentation is "believed superior"
   because it weights rather than randomly assigns — is the cited
   rationale): each scored reject becomes two weighted synthetic
   observations (good/bad) per its predicted probability, rather than one
   randomly-labeled record (parceling) or a single hard label (cutoff).
6. **Assemble the KIGB dataset**: accepts (§7's train split) + weighted
   synthetic reject records.
7. **Re-derive WOE/IV on KIGB** using the **same bin edges fit on the KGB
   train set** (source 5's MathWorks workflow: "apply identical binning
   rules from the base model to ensure consistency") — do not refit bins on
   the combined population.
8. **Refit logistic regression on KIGB** (overlap-only feature set, per
   step 3's constraint).
9. **Validate reject inference itself before trusting the KIGB model**
   (KB §8.2's own checks, echoed by source 6's skepticism): inferred bad
   rate among rejects should be **higher** than the KGB population's bad
   rate and **monotonically declining** by score band — if it isn't, the
   inference is broken and should not be used, not silently accepted.
10. **Compare KGB vs. KIGB** on the **overlap-only feature set for both**
    (an apples-to-apples comparison — comparing a full-feature KGB against
    an overlap-only KIGB would confound "reject inference helped" with
    "fewer features hurt"): AUC/KS/Gini on test and OOT, a swap-set-style
    comparison of which loans each model would approve differently (source
    6's technique), per KB §8.2's own validation rule (post-RI variable
    strength should increase, not decrease).
11. **Honest expectation-setting, cited directly from source 6**: Huang &
    Scott's own empirical finding is that reject inference is often **not**
    the main driver of scorecard performance changes — this section should
    report whatever the comparison in step 10 actually shows, including a
    negative or negligible result, rather than assuming reject inference
    must improve the model because the textbook says it addresses a real
    bias.

**What this notebook does NOT attempt**: the credit-bureau reject-inference
method (source 8) — this project has no external bureau data on rejected
applicants — and augmentation using `grade`/`int_rate`-dependent terms,
per step 3's field-overlap constraint.

---

## 13. Master Rating Scale validation

Unchanged from v2 — grade concentration, monotonicity (A→G, A1→A5),
AUC(grade-alone) vs. AUC(full model). **New decision needed**: run this
against the KGB model, the KIGB model, or both — state the choice
explicitly once §12 is complete; if §12 §11's comparison shows KIGB
materially different, MRS validation should use whichever model is
designated the production candidate, not both by default.

---

## 14. TTC/PIT decision

Unchanged mechanics from v2 (does `issue_year`/drift enter as a feature vs.
monitoring-only) — **now also informed by §6's vintage-curve finding**, not
just the `int_rate` PSI number alone. **[TJ]** cell citing both.

---

## 15. Calibration

Unchanged from v2 — Method 1 (log-odds regression) to the live bad rate
(~20.5%, re-verify), pooled default with per-vintage check — **[TJ]** Method
1 vs. isotonic/Platt scaling.

---

## 16. Scaling to points, and adverse-action reason codes — new section

No prior version of this plan had this step at all, despite it being a
named, concrete step in three of the ten sources (2, 4, and implicitly the
KB's own PDO mention) — and despite adverse-action reason codes being a
genuine US lending regulatory requirement (ECOA), not an optional
nice-to-have, for any scorecard framed as decisioning real applicants:

- **PDO scaling** (Points to Double the Odds): `Score = Offset + Factor ×
  ln(Odds)`. Source 2's own illustrative parameters (base score 200, base
  odds 50:1, PDO 20) are **an example, not a value to copy** — pick and
  document this project's own base score/base odds/PDO choice in a
  **[TJ]** cell (a common alternative convention is base score 600 at
  odds 50:1, PDO 20 — either is defensible; state the choice and why).
- **Reason codes**: for each scored loan, identify which WOE-binned
  characteristics contributed most negatively to the score (the standard
  "top N adverse factors" logic every source in this section describes) —
  implement as a live-computed table for a sample of declined-range scores,
  not just asserted as a feature the model "could" support.
- This section only runs once §11 (or §12, if KIGB is the production
  choice) has a validated, calibrated model — it is presentation of an
  already-fit model, not new modeling.

---

## 17. Validation suite — first-pass here, formal treatment in Phase 5

**Division of labor, stated explicitly to avoid duplication drift between
this notebook and the dedicated Phase 5 validation notebook:**

| Here (Phase 1, in-notebook) | Phase 5 (dedicated validation notebook) |
|---|---|
| AUC/KS/Gini on test and OOT, bootstrap CI, immediately after fitting — proves the model this notebook just built actually works, per evidence-in-code | Full discriminatory-power suite (CAP, rank correlations), re-derived independently |
| A single PSI check reusing `int_rate`'s known drift pattern, applied to the fitted score (development vs. OOT) | Full PSI/CSI stability suite, SR 11-7 framing, ongoing-monitoring cadence |
| Hosmer-Lemeshow/Brier only if calibration (§15) needs a pass/fail check to proceed | Full calibration-testing section |

This notebook's validation exists to justify moving on to §16/§18 — it is
not a substitute for Phase 5's dedicated pass.

---

## 18. Model persistence (unchanged from v2, restated)

- `ASSETS_TABLES`: WOE bin-edge table, IV table, coefficient table,
  reason-code table (§16), calibrated-PD-by-grade table.
- **Fitted model objects** (both, if §12 produces a genuinely different
  KIGB model): `models/pd_scorecard_kgb_v1.joblib`,
  `models/pd_scorecard_kigb_v1.joblib`, each with a model card (features,
  WOE bins, split definition, library versions, fit date, test/OOT AUC).
  Versioned `_v1`/`_v2`, never overwritten.

---

## 19. Governance note (new, brief — context, not a project deliverable)

Source 2's own closing section describes a 3-team model lifecycle (Model
Development / Model Validation / Model Risk Management) governing any real
bank scorecard's ongoing life. **State this in the notebook's closing
markdown as context, not as a structure this solo portfolio project
implements** — exactly the same treatment Phase 5's plan already gives
SR 11-7's three lines of defense. Worth one paragraph so a reader
understands what "production" would additionally require beyond this
notebook's own scope.

---

## 20. Close-out / hand-off to Phase 2

Unchanged from v2: explicit note on which fields Phase 2 (LGD) needs
directly from `windowed`, not the parquet; reject inference's actual
outcome (§12) is now resolved rather than a named future gap, so this
section states what was actually found, not what's still deferred.

---

## Checklist — what is built vs. what is left

**Built: nothing.**

- [x] 10 external sources identified, fetched, and cited against specific
  sections (§0).
- [x] Rejected file live-profiled: 27,648,741 rows, 9 columns, Policy Code
  distribution, field-overlap constraint identified (§4).
- [x] Vintage-curve data availability confirmed live (`last_pymnt_d`
  coverage 99.3% on charged-off loans) (§4, §6).
- [x] Two-notebook structure decided and stated explicitly (§1) — **pending
  Devesh's sign-off**, since it changes v2's single-notebook assumption.
- [ ] Confirm `Policy Code = 2`'s actual meaning live (§4, §12 step 2)
  before building any reject-inference logic on top of that assumption.
- [ ] Build `01_pd_kgb_scorecard.ipynb` per §5–§11, §13–§18, section by
  section, shown to Devesh before each is committed.
- [ ] Build `02_pd_reject_inference_kigb.ipynb` per §12, including the
  overlap-only sub-model and the honest KGB-vs-KIGB comparison.
- [ ] Vintage/cohort curve built and its finding fed into §7's OOT-validity
  check and §14's TTC/PIT decision.
- [ ] Reason codes and PDO scaling implemented (§16) — not previously
  planned at all before this revision.
- [ ] Every **[TJ]**-marked decision has its markdown cell, evidenced.
- [ ] Standard production-readiness audit on both notebooks before calling
  Phase 1 done.
- [ ] Commit only the new notebook/model files — same git discipline as
  every prior phase (force-add needed while `docs/`/new folders remain
  outside whatever `.gitignore` currently allows — verify per-folder before
  committing, don't assume).

---

## References

- `docs/phase_0_report.md`, `docs/Peaks2Tails_Knowledge_Base.md` §8–§10,
  §17 — unchanged from v2.
- `credit-risk-curriculum` skill, reference files 03/04 — unchanged from
  v2, same staleness caveats apply.
- §0's 10 external sources — the new grounding for this revision;
  re-consult the original source, not this summary, before implementing any
  technique this document only sketches.

---

## Changelog

- **v3 (this revision)**: rebuilt against 10 external real-world sources
  (§0) chosen to mirror actual bank practice. Added: event/window
  restatement (§5); vintage/cohort default-timing analysis with an explicit,
  evidenced scope boundary against full roll-rate transition matrices (§6);
  reject inference brought into Phase 1's actual scope as its own notebook,
  including live profiling of the 27.6M-row rejected file and its severe
  field-overlap constraint (§12); scaling-to-points and adverse-action
  reason codes (§16); explicit division of labor between this notebook's
  validation and Phase 5's (§17); a governance-context note (§19). Notebook
  structure changed from one notebook to two (§1) as a direct consequence
  of bringing reject inference in-scope — flagged for sign-off.
- **v2**: location resolved; unreproducible baseline AUC corrected after
  live re-derivation; added data-partition detail (train/validation/test/
  OOT); added feature engineering/selection as explicit steps; added
  technique-justification standing rule; added model persistence (fitted
  object, not just output table).
- **v1**: initial draft, written immediately after Phase 0's audit.
