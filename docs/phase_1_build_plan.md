# Phase 1 Build Plan — PD Account-Level Scorecard (Lending Club)

**Status as of this writing: not started. Nothing in this document has been
built.** This is the plan, written after Phase 0 was audited and found ready
(`docs/phase_0_report.md`), then corrected once during pre-build live
verification (see §6's baseline note and the changelog at the bottom of this
file). Every checklist item below is unchecked because the notebook file
does not exist yet.

This document is written to be self-sufficient: an agent with no other
context should be able to read this file alone and know exactly what to
build, why, in what order, against which real data, and what "done" looks
like — without needing to re-derive anything from the KB or re-read Phase 0
from scratch.

---

## 1. What Phase 1 is, and why it's next

Phase 1 = building the first working PD (Probability of Default) model for
Lending Club: an **account-level, application scorecard**, trained on the
model-ready population Phase 0 produced. It is the first of four sequential
modeling phases planned for this dataset (Phase 1 PD → Phase 2 LGD → Phase 3
EAD → Phase 4 IFRS 9 ECL assembly), with Phase 5 (validation & monitoring)
running alongside/after all four.

**Why PD first, specifically:** LGD and EAD (Phases 2–3) both need PD-adjacent
concepts already established (segmentation via `grade`, the TTC/PIT
philosophy decision) to make sense of *when* a loss is being measured, and
the eventual IFRS 9 ECL assembly (Phase 4) is literally `PD × LGD × EAD` —
building PD first gives every later phase a working reference point.
This is also KB's own module ordering (§8 PD → §11–13 LGD/EAD → §14 IFRS9)
and the `credit-risk-curriculum` skill's own stated build order.

**Why now, not later:** Phase 0's audit (`docs/phase_0_report.md`, verdict
section) found zero blocking issues — a clean, evidence-backed, 31-column
model-ready table with a documented governance ledger. Nothing about Phase 1
requires re-opening Phase 0.

---

## 2. Where this lives — RESOLVED

**Confirmed location:** a new top-level `phase1_pd_modeling/` folder,
sibling to `phase0_data_platform/`, mirroring that folder's own
dataset-subfolder convention so later datasets/phases stay structurally
consistent:

```
phase1_pd_modeling/
  01_lendingclub/
    notebooks/
      01_pd_account_scorecard.ipynb   <- this notebook
    models/                            <- serialized fitted model objects (§8)
```

This was an open question in an earlier draft of this document (proposing
`phase0_data_platform/01_lendingclub/notebooks/04_modeling/` instead,
matching the `credit-risk-curriculum` skill's own file paths) — Devesh
confirmed the top-level-folder approach in chat. The skill's reference files
(03, 04) still refer to `04_modeling/...`; treat that as the skill's own
staleness, not a reason to relocate this notebook.

---

## 3. Non-negotiables carried over from Phase 0 (with two corrections)

The same three standing rules apply, unchanged, plus one new standing rule
this notebook must follow that Phase 0's notebooks didn't need (Phase 0 had
no competing techniques to choose between — Phase 1 does, repeatedly):

1. **Evidence-in-code** — every markdown claim backed by a printed number in
   the same notebook, in the same cell block. This applies with extra force
   here: every IV/AUC/PSI number cited below **must be re-derived live**
   against `windowed`/the parquet inside the new notebook, never hard-coded
   from this document, from Phase 0, or from a skill reference file. **This
   rule caught a real error during this project's own pre-build check** —
   see §6's baseline note — so treat it as load-bearing, not a formality.
2. **Direct DuckDB connection — correcting the skill's reference files.**
   The `credit-risk-curriculum` skill's reference files (03, 04) say to use
   `notebooks/_shared/nb_setup.py`'s `connect()`. **This is stale** — Phase
   0's audit confirmed `nb_setup.py` is obsolete project-wide; the real
   standing rule (`CLAUDE.md`, and both Phase 0 notebooks' own actual code)
   is a direct inline `duckdb.connect(DUCKDB_FILE, read_only=True)` using the
   same `RAW_FILE`/`DUCKDB_FILE`/`ASSETS_TABLES`/`ASSETS_PLOTS` relative-path
   variables Phase 0 used.
3. **No premature narrowing outside `03_data_cleaning`** — this rule's
   *spirit* still applies to a modeling notebook: any feature considered and
   then dropped (e.g. deciding not to use `grade`/`int_rate`, see §6) needs an
   explicit, evidenced markdown decision cell, not a silent omission.
4. **Technique justification — new standing rule for Phase 1 onward.**
   Every place this notebook picks one modeling technique over a plausible
   alternative gets its own markdown cell answering "why this, not that,"
   evidenced where possible (a quick live comparison, a cited KB rule, or a
   named practical constraint) — not just asserted as a preference. This is
   broader than the two decision cells Phase 0-era planning already called
   out (grade/int_rate near-definitional choice, TTC vs. PIT). The full list
   of decisions that need one of these cells is in §6.

**Explain before building.** Per how every notebook in this project has been
built so far: this document is the plan. Actual notebook code is written
section by section, shown to Devesh, and only committed after he says
"go ahead" — this build plan does not authorize writing the notebook itself.

**Executive style, same conventions:** bullets/tables over prose, no
`tabulate` (pandas `.to_string()` for eyeball previews), the
markdown-before/code/markdown-**Result**-**Next**-after cell pattern, an
intro cell + cell-map table at the top, section closers at the end of each
logical block — identical to both Phase 0 notebooks.

---

## 4. Data inputs — exact tables/columns, and the one structural trap

- **Primary source:** `windowed` table in
  `phase0_data_platform/01_lendingclub/data/02_interim/lendingclub.duckdb`
  (1,195,879 rows, live-confirmed this session) — connect read-only, per §3.
  **Note:** every field in `windowed` is stored as `VARCHAR` (confirmed live
  via `DESCRIBE windowed`), including `int_rate`, `dti`, `fico_range_low`,
  `grade`. This notebook must explicitly `CAST` numeric fields before any
  modeling step — do not assume DuckDB's schema matches the parquet's typed
  columns.
- **Feature reference:** `data/03_processed/lendingclub_model_ready.parquet`
  (31 columns, re-verified in Phase 0's audit: 1,195,879 rows, 0 nulls, `id`
  unique, bad rate 20.5214%). Categorical fields are **unencoded strings** in
  this file by design — WOE-encoding them is this notebook's job.
- **`sub_grade` — confirmed present and fully populated in `windowed`**
  (live-checked this session: 1,195,879 non-null, 35 distinct values, A1–G5).
  It is **not** in the 31-column parquet — pull it fresh from `windowed` if
  the grade/int_rate decision (§6) leads toward wanting within-grade signal.
- **Full field-role dictionary, governance ledger, and the two carried-over
  Phase 0 items** (`revol_util`'s capping rule still open; `emp_length` kept
  categorical rather than numerically parsed) are documented in
  `docs/phase_0_report.md` §4–§5.

---

## 5. Data partition — train / validation / test / OOT

Live-verified `issue_year` distribution (derived from `issue_d` via
`strptime(issue_d, '%b-%Y')` — `windowed` has no pre-existing year column):

| `issue_year` | n | share |
|---|---|---|
| 2013 | 134,804 | 11.3% |
| 2014 | 223,103 | 18.7% |
| 2015 | 375,546 | 31.4% |
| 2016 | 293,105 | 24.5% |
| 2017 | 169,321 | 14.2% |
| **Total** | **1,195,879** | 100% |

**Recommended split — four groups, two different splitting logics:**

1. **OOT (Out-of-Time) = `issue_year = 2017`** — 169,321 rows (14.2%), held
   out **entirely**, never touched during fitting, binning, threshold
   selection, or any comparison between candidate specifications. This
   reuses the exact vintage boundary already implicated in the project's own
   `int_rate` PSI = 0.140 (2013 vs. 2017) drift finding — OOT performance on
   2017 is therefore a direct test of "does this scorecard hold up on the
   population we already know has drifted," not an arbitrary cutoff.
2. **Train / Validation / Test — random, stratified split of the remaining
   `issue_year` 2013–2016 pool (1,026,558 rows)**, stratified on `is_bad`
   (and consider also stratifying on `grade`, so segment proportions aren't
   accidentally skewed across the three splits):
   - **Train — 60%** (≈615,935 rows): fit WOE bin edges and the logistic
     regression coefficients. WOE bin edges are **fit on train only** and
     then **applied (not refit)** to validation, test, and OOT — fitting
     bins separately on each split would leak information and make the
     splits non-comparable.
   - **Validation — 20%** (≈205,312 rows): the set used for every "which
     option performed better" comparison — coarse-classing threshold
     choices, the grade/int_rate Option A/B comparison, the TTC/PIT
     comparison. Touched repeatedly during development, by design.
   - **Test — 20%** (≈205,311 rows): touched **exactly once**, after every
     modeling decision is locked using train/validation only. This is the
     in-time performance number reported alongside OOT.

**Why four groups, not the KB's plainer three (train/validation/OOT):** the
KB's own scorecard pipeline (§8.1) only names three because it doesn't
distinguish "the set you tune thresholds against" from "the set you report
your final in-time number from" — collapsing those into one set (as a
plain train/validation/OOT split would) risks a subtly optimistic final
metric, since the same data used to pick coarse-classing cutpoints would
also be the data used to report performance on. The fourth group (test)
exists specifically to keep that reported number honest.

**Simpler alternative, if this feels like more machinery than the project
needs:** merge validation and test into one set (train/validation/OOT,
matching the KB's plain three-way split) — defensible for a portfolio
project of this scope, since the coarse-classing thresholds here are
mostly rule-based (>2%-population, monotonicity) rather than the product of
heavy hyperparameter search, so the leakage risk the four-way split guards
against is smaller than in a typical ML tuning pipeline. **Recommendation:
keep the four-way split** — it costs one extra `train_test_split` call and
directly answers "did we overfit our own threshold choices," which is worth
having in a project meant to demonstrate rigor.

All four splits, and the exact row counts each notebook run actually
produces, must be printed live in the notebook's own partition cell — the
numbers above are this session's pre-build scouting, not something to
hard-code.

---

## 6. KB mapping — the full scorecard pipeline

Full depth in `docs/Peaks2Tails_Knowledge_Base.md` (§8, §9, §10, §17) and the
skill's reference files 03/04 — cited by section below, not reproduced.

| Stage | KB ref | What it means for this notebook |
|---|---|---|
| Data partition | §8.1 | See §5 above. |
| Fine classing | §8.1 | ~20 quantile/tree-driven bins per numeric candidate, fit on train only. |
| Coarse classing | §8.1 | Collapse to ≤8 classes; enforce monotonic bad-rate trend, >2% population/class, >50 bads/class (or 1% of all bads) as **live code asserts**. With ~245K bads in the population, the bads-floor is trivial to clear; the binding constraint in practice will be the >2%-population rule and monotonicity. |
| WOE / IV | §8.1 | `WoE = ln(%good/%bad)`, `IV = Σ(%good−%bad)×WoE`, computed **live** on train, applied to validation/test/OOT. |
| Grade/sub_grade as existing segmentation | §9 (ref. 04 §1) | This project is **auditing** an existing segmentation (LC's own A–G/1–5 grade), not building one from scratch. Concentration, monotonicity (A→G, and A1→A5 within grade), and AUC(grade-alone) vs AUC(full model) are the concrete checks. |
| TTC vs PIT | §10.1 (ref. 04 §2) | A decision cell: include `issue_year`/drift as a model feature → PIT-leaning; keep it monitoring-only → TTC-leaning. Cite the notebook's own live PSI number as evidence — needs a technique-justification cell per §3 rule 4. |
| Calibration | §10.3 (ref. 04 §3) | Target central tendency = the population's own realized bad rate (~20.5%, re-verify live). Recommended default: **pooled** calibration (fit once on all of train) with a per-vintage representativeness check as validation. Method 1 (log-odds linear regression) is the natural starting method — needs a technique-justification cell (why Method 1 over isotonic/Platt scaling). |
| Master Rating Scale validation | §10.2, §10.5 (ref. 04 §4) | LC's grade×sub_grade is already a 35-notch MRS — validate, don't replace, unless validation actually fails. |
| Reject inference | §8.2 (ref. 03 §3.4) | **Out of scope for this notebook** — a legitimate follow-on once the accepts-only scorecard is validated. Lending Club's `rejected_2007_to_2018Q4.csv.gz` is already sitting in `data/01_raw/`, untouched, for whenever that follow-on happens. Flag this explicitly in the notebook's closing markdown. |
| Scaling (PDO) | §8.1 | Optional final step once the base logistic model validates. |

**The one explicit modeling-design decision this notebook must state, not
silently resolve:** `grade` (IV 0.4806, live-verified this session, close to
the 0.47 the skill's reference file cites) and `int_rate` sit right at KB's
"≥0.5 = very strong/suspicious, re-check for leakage" boundary. They are
**not** outcome leakage in the technical sense — `grade` predates default,
it's LC's own underwriting output — but they are near-definitional. Two
legitimate options, either acceptable, **neither silent** (needs a
technique-justification cell per §3 rule 4):
- **Option A** — keep both, document why (predates default, legitimately
  informative, matches "build it the way it will be applied").
- **Option B** — engineer around them, forcing the model onto more
  mechanistic features (`dti` is the strongest candidate — its effect
  survives stratifying by both grade and income per Phase 0's own finding).

**Baseline to beat — CORRECTED, this is important.** An earlier draft of
this document cited "Phase 0's own baseline logistic regression bootstrap
95% AUC CI [0.695, 0.698]" as an existing, already-computed project result.
**That number does not reproduce and should not be treated as fact.** It
traced back to the `credit-risk-curriculum` skill's own reference file
(`03-pd-account-level-scorecard.md`), which itself says to re-derive it live
rather than import it — a step that was skipped when this document was first
written. Live re-derivation this session, several ways, all against the real
`windowed` table:

| Approach | AUC |
|---|---|
| grade (WOE) + int_rate, train 2013–2016 → OOT 2017 | 0.681 (OOT), bootstrap 95% CI [0.678, 0.684] |
| grade (WOE) + int_rate, in-sample on train | 0.688 |
| grade (one-hot) + int_rate, random 70/30 split | 0.687 |
| int_rate alone | 0.685 |
| grade alone | 0.681 |
| grade (one-hot) + int_rate, in-sample, full population | 0.688 |

Every variant lands at **0.68–0.69**, not 0.695–0.698. **There is no
verified prior baseline in this repo.** This notebook establishes the first
one, live, using the exact train/validation/test/OOT split in §5 — whatever
number the notebook's own §5-split, §6-pipeline logistic fit produces on
`test` and `OOT` *is* the project's baseline going forward, reported with a
bootstrap CI, and it is **not** expected to land at [0.695, 0.698]. A
properly-binned, WOE-transformed scorecard should be expected to land in a
broadly similar range to the numbers above (same underlying feature set),
not dramatically exceed them — a much higher number would itself be worth
investigating for a mistake before celebrating it.

---

## 7. Feature engineering vs. feature selection — scope, and why they're kept distinct

The earlier draft of this document blurred these two together inside "fine
classing → coarse classing → WOE/IV." They are different jobs and get their
own explicit points in the notebook:

**Feature engineering — deliberately minimal here, by design, not by
omission.** For a scorecard build, "feature engineering" is mostly *already
done*:
- Phase 0's cleaning notebook already applied the numeric transforms a
  scorecard needs upstream (log1p, p1/p99 capping) — this notebook does not
  redo those.
- The main engineering step genuinely local to this notebook is deriving
  `issue_year` (and optionally a coarser `vintage` cohort grouping) from
  `issue_d`, needed for §5's partition and the TTC/PIT decision.
- **WOE transformation itself is the feature engineering step for every
  categorical/binned-numeric candidate** — in scorecard modeling, WOE
  encoding *is* the engineered feature, not a preprocessing detail before
  "real" feature engineering. Say this explicitly in-notebook: it's a
  technique-justification point (§3 rule 4) — WOE over one-hot or target
  encoding, because WOE bins enforce monotonicity, handle missing/rare
  categories via a documented rule, and produce directly interpretable
  coefficients (each WOE-encoded feature's logistic coefficient is
  approximately its own weight of evidence), which one-hot/target encoding
  do not give as cleanly.
- Interaction terms or polynomial features are **out of scope** —
  scorecards are conventionally additive/linear on WOE inputs specifically
  for interpretability and regulatory explainability (KB §8.1's own
  framing); introducing interactions would need its own justification cell
  and isn't recommended for a first build.

**Feature selection — a real, separate step, after WOE/IV, before the final
fit:**
1. **IV threshold filter** — drop candidates below the conventional "not
   predictive" floor (IV < 0.02) after live-computing IV for every
   shortlisted field on train; keep the 0.02–0.5 band; flag (not
   automatically drop) anything ≥0.5 for the same leakage-review reasoning
   already applied to `grade`/`int_rate`.
2. **Multicollinearity check among WOE-transformed features** — a
   correlation matrix (or VIF) on train's WOE-encoded candidate set before
   the final logistic fit; document any pair/cluster above a stated
   threshold (e.g. |r| > 0.7) and how it was resolved (drop one, combine,
   or keep with a stated rationale).
3. **Stepwise/backward elimination — optional refinement**, not required for
   a first working model; flag as a follow-on if the direct IV-filtered set
   already produces a clean, monotonic, validated model.

Both feature engineering and feature selection get their own numbered
sections in §9's cell-by-cell plan — they are not folded into "WOE/IV."

---

## 8. Model persistence — saving the model itself, not just its output table

An earlier draft of this document only planned to write a **calibrated-PD-
by-grade lookup table** to `ASSETS_TABLES` — sufficient for a human reading
the notebook, but not sufficient for another notebook or agent to actually
*apply* the fitted model to new data (e.g. a future reject-inference
follow-on, or re-scoring). Both are needed:

- **For evidence-in-code / human readability (`ASSETS_TABLES`, as before):**
  the WOE bin-edge table, the IV table, the logistic regression coefficient
  table, and the calibrated-PD-by-grade table — all CSVs, all printed live.
- **For actual reuse (new, this correction): the fitted model object
  itself**, serialized via `joblib`, written to
  `phase1_pd_modeling/01_lendingclub/models/pd_scorecard_logit_v1.joblib`.
  Alongside it, a small model card (`pd_scorecard_logit_v1_card.json` or a
  markdown cell reproducing the same content) recording: exact feature list
  and WOE bin edges used, the train/validation/test/OOT split definition
  (§5) and random seed, library versions (`scikit-learn`, `pandas`, `numpy`
  — print `__version__` live), the fit date, and the test/OOT AUC achieved.
  This is what lets Phase 4 (or a reject-inference follow-on) actually score
  new rows instead of only reading a static lookup table.
- **Versioning convention:** suffix with `_v1`; a future re-fit (e.g. after
  reject inference) becomes `_v2`, never an overwrite — keeps the model
  history auditable the same way git keeps the notebook history auditable.

---

## 9. Notebook structure — cell-by-cell plan

Following this project's own per-step convention (intro → cell-map table →
repeated [markdown "why/how/**Answers:**" → code → markdown
"**Result**/**Next**"] → section closers). Updated from the earlier draft to
add the feature-engineering, feature-selection, and model-persistence
sections (§7, §8) as their own numbered steps, and to fold in the
technique-justification cells (§3 rule 4) at every step that needs one
(marked **[TJ]** below):

1. **Intro + scope** — title, status line, what this notebook covers, where
   it fits, explicit note that reject inference is out of scope.
2. **Cell-map table** — one row per numbered step below.
3. **Section: population & connection** — connect via direct
   `duckdb.connect(DUCKDB_FILE, read_only=True)`; restate and re-verify
   `windowed`'s row count and bad rate live; confirm `sub_grade` exists
   (already live-verified pre-build, re-verify in-notebook per evidence-in-
   code); cast `VARCHAR` numeric fields explicitly (§4).
4. **Section: feature shortlist & provenance** — restate the candidate
   feature set from the parquet's 31 columns plus the field dictionary;
   decide the `revol_util`/`emp_length` carry-overs from Phase 0.
5. **Section: feature engineering** — derive `issue_year`/vintage cohort
   from `issue_d`; state explicitly that transform-level engineering was
   done upstream in Phase 0 and WOE is this notebook's engineering step
   (§7) — **[TJ]** WOE vs. one-hot/target encoding.
6. **Section: train/validation/test/OOT split** — implement §5's split;
   print exact row counts/bad rates per split live — **[TJ]** four-way vs.
   three-way split (§5).
7. **Section: fine classing** — ~20 bins per numeric candidate, fit on train.
8. **Section: coarse classing** — collapse to ≤8 classes; monotonicity,
   >2%-population, >50-bads checks as live asserts — **[TJ]** manual
   rule-based coarse classing vs. an automated optimal-binning library
   (e.g. `optbinning`) — state why manual (transparency/auditability
   matches this project's evidence-in-code ethos) is the choice here.
9. **Section: WOE/IV** — WOE transform + IV table on train, applied
   (not refit) to validation/test/OOT; compared against the 0.4806
   grade-IV sanity check from pre-build scouting.
10. **Section: feature selection** — IV threshold filter, multicollinearity
    check among WOE features, optional stepwise note (§7).
11. **Section: grade/int_rate decision** — the explicit Option A/B
    **[TJ]** markdown decision cell from §6, citing live IV numbers.
12. **Section: MRS validation** — grade concentration, monotonicity (A→G,
    A1→A5 within grade), AUC(grade-alone) vs. AUC(full model).
13. **Section: TTC/PIT decision** — **[TJ]** explicit markdown cell, citing
    live PSI, deciding `issue_year`'s role (feature vs. monitoring-only).
14. **Section: scorecard fit** — logistic regression on the selected
    WOE-transformed feature set, fit on train — **[TJ]** logistic regression
    vs. a tree-based/GBM alternative (interpretability, WOE-linearity,
    and regulatory-explainability requirements per KB §8.1 are the reasons
    to stay with logistic regression for this build).
15. **Section: validation against baseline** — AUC/KS with a bootstrap CI on
    test **and** OOT separately, compared against each other (in-time vs.
    out-of-time gap is itself a finding) — no external baseline to compare
    against per §6's correction.
16. **Section: calibration** — **[TJ]** Method 1 (log-odds linear
    regression) vs. isotonic/Platt scaling, against the population's own
    live-computed bad rate; per-vintage representativeness check.
17. **Section (optional): PDO scaling** — only after step 15 validates.
18. **Section: model persistence** — save the fitted model object, WOE bin
    edges, and model card per §8; write the calibrated-PD-by-grade table to
    `ASSETS_TABLES`.
19. **Section: close-out** — explicit note that reject inference is the
    natural next follow-on, not part of this notebook; hand-off note for
    Phase 2 (LGD) on which fields it will need directly from `windowed`.

---

## 10. Checklist — what is built vs. what is left

**Built: nothing.** Every line below is a "to do," not a status report.

- [x] Confirm notebook location — §2, resolved (`phase1_pd_modeling/`).
- [x] Confirm `sub_grade`'s presence/completeness in `windowed` — §4,
  live-verified pre-build.
- [x] Re-derive the baseline AUC live and correct this document — §6,
  done pre-build; the corrected framing above is what the notebook itself
  must still reproduce in-notebook (pre-build scouting is not a substitute
  for the notebook's own evidence-in-code cells).
- [ ] Create the notebook file, following this plan's cell structure (§9),
  one section at a time, shown to Devesh before each is committed.
- [ ] Implement the train/validation/test/OOT split (§5) with printed,
  live row counts and bad rates per split.
- [ ] Resolve the `revol_util` capping and `emp_length` numeric-parsing
  carry-overs from Phase 0 (§9 step 4).
- [ ] Feature engineering section — derive `issue_year`/vintage (§7/§9 step 5).
- [ ] Feature selection section — IV filter + multicollinearity check
  (§7/§9 step 10).
- [ ] Make and document the grade/int_rate near-definitional decision
  (§6/§9 step 11), with its technique-justification cell.
- [ ] Make and document the TTC/PIT decision (§6/§9 step 13), with its
  technique-justification cell.
- [ ] Fit and validate the scorecard on test and OOT separately.
- [ ] Calibrate (pooled default, per-vintage check), with its
  technique-justification cell.
- [ ] Save the fitted model object + model card + calibrated-PD-by-grade
  table (§8/§9 step 18) — not just the lookup table.
- [ ] Explicitly flag reject inference as a follow-on, not done here.
- [ ] Run this project's standard production-readiness audit (0 errors,
  every markdown claim evidenced, unique cell ids, assets present on disk).
- [ ] Commit **only** the new notebook file (and its `models/` output) —
  verify staged files with `git diff --cached --name-only`, never
  `git add -A`, never push — and remember `docs/` itself is currently
  gitignored, so this build-plan file won't travel to GitHub until that's
  resolved separately.

---

## 11. Past → present → future

- **Past (input to this phase):** Phase 0 complete — ingestion, master EDA
  (151-field governance ledger), cleaning (31-column model-ready parquet,
  26 chosen fields, 66 deferred). Audited and confirmed ready
  (`docs/phase_0_report.md`).
- **Present (this document):** the corrected, self-sufficient plan for
  Phase 1. Location resolved, baseline corrected, and three real gaps closed
  from the earlier draft: feature engineering and feature selection now have
  their own explicit steps (§7/§9), every technique choice gets a
  justification cell (§3 rule 4), and the fitted model itself gets
  persisted, not just its output table (§8).
- **Future (what Phase 1 hands to Phase 2+):** a working, calibrated,
  *reusable* PD model (an actual saved model object, not only a lookup
  table) and a validated grade-based rating scale. Phase 2 (LGD, unsecured)
  will need direct access to `windowed`'s post-origination fields
  (`recoveries`, `total_pymnt`, etc.) that never entered the PD parquet by
  design. Reject inference remains an explicit, named open follow-on.

---

## 12. References

- `docs/phase_0_report.md` — full Phase 0 audit (field roles, ledger,
  carried-over open items).
- `docs/Peaks2Tails_Knowledge_Base.md` §8 (PD account-level), §9 (PD
  segment-level), §10 (calibration & rating philosophy), §17 (behavioral vs.
  application scorecards).
- `credit-risk-curriculum` skill, reference files `03-pd-account-level-
  scorecard.md` and `04-pd-calibration-and-rating-philosophy.md` — full
  bridge detail this document condenses; re-read both in full when actually
  building. **Note their known staleness**: stale `nb_setup.py` mandate
  (§3), stale `04_modeling/` file path (§2), and an unverified baseline AUC
  figure that does not reproduce (§6) — cross-check any number pulled from
  these files against this repo's own live output before trusting it.

---

## Changelog

- **v2 (this revision):** location resolved (§2); baseline AUC corrected
  after live re-derivation exposed it as unreproducible (§6); added data
  partition detail with a four-way train/validation/test/OOT split (§5);
  added feature engineering (§7) and feature selection (§7) as explicit,
  separate steps; added a standing technique-justification rule (§3 rule 4)
  applied throughout §6/§9; added model persistence — saving the fitted
  model object itself, not just its output table (§8). Cell-by-cell plan
  (§9) renumbered from 16 to 19 steps to fit these additions.
- **v1:** initial draft, written immediately after Phase 0's audit.
