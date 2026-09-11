# Phase 1 Build Plan — PD Account-Level Scorecard (Lending Club)

**Status as of this writing: not started. Nothing in this document has been
built.** This is v4 of this plan. v3 rebuilt it from scratch against 10 real
external sources chosen to mirror actual bank scorecard practice (§0) and
added vintage/roll-rate analysis, in-scope reject inference, and
scaling-to-points with reason codes. **v4 enriches every one of those
sections with content read directly from the actual Peaks2Tails course
files this project's own curriculum is built on** — not the KB's summary of
them, the primary PDFs and Excel workbooks themselves (§0.1) — per Devesh's
explicit instruction to look at the source material, not the digest. This
surfaced exact mnemonics, formulas, and worked numeric examples the KB
summary had compressed away, and two genuine terminology inconsistencies
*within* the course material itself, both flagged rather than silently
resolved (§0.1, §9.1, §12.1, §6.1). The changelog at the bottom tracks what
changed between v1 → v2 → v3 → v4.

This document is written to be self-sufficient: an agent with no other
context should be able to read this file alone and know exactly what to
build, why, in what order, against which real data, and what "done" looks
like — without needing to re-derive anything from the KB, the external
sources, the course files, or Phase 0 from scratch.

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

### 0.1 Direct Peaks2Tails course-file citations (new in v4)

Devesh's instruction for this revision was explicit: *"look into the actual
course files not just the summary."* The KB (`docs/Peaks2Tails_Knowledge_Base.md`)
is itself a compressed distillation of 216 PDFs + 52 Excel workbooks (its
own §19 documents this). For the five PD-scorecard topics this plan covers,
this revision went back to the primary files directly — five parallel
research passes, one per topic, each reading the actual PDFs (including
visual reading of scanned/handwritten pages) and, for the vintage/roll-rate
topic, inspecting the structure of the actual Excel workbooks.

| Topic | Primary files read this session | What they added beyond the KB summary |
|---|---|---|
| WOE binning & variable selection | `9901-Binning.pdf`, `WOE binning.pdf`, `5345-Variable Selection.pdf`, `Marginal IV.pdf`, `3.1.4 Discriminatory Power - WOE,IV and Entropy.pdf` | The **SIMPLE** binning mnemonic with exact numeric thresholds, the master classing pipeline order, the exact Marginal IV formula, the **IMPORTANT** business-filter mnemonic, VARCLUS, exact penalty-term formulas, and a full numeric-threshold table (§8.1, §9.1) |
| Logistic regression & cutoff | `1423-Logistic Regression.pdf`, `1766-Introduction_Scorecard.pdf`, `7695-Cutoff.pdf`, `Types of scoring.pdf`, `creditrisk model building steps.pdf` | The exact PDO scaling formula with a fully worked numeric example, statistical vs. business cutoff mechanics, minimum-sample governance rule, and an 81-page end-to-end build sequence that independently corroborates this plan's own step order (§11.1, §16) |
| Reject inference | `5650-Reject inferencing.pdf`, `440475936-EXL-Acquisition-Scorecard-Reject-Inference-Methodologies.pdf` | The exact augmentation/parceling penalty-factor formula with a fully worked example, the course's own explicit reject-population checklist, two fully worked swap-set exercises, and a second, independent real-world source (EXL Decision Analytics, 2016) with its own 4-method comparison and an explicit conditional recommendation (§12, §12.1) |
| Vintage & roll-rate | `2360-Vintage & Roll rate analysis .pdf`, `Roll Rate.pdf`, plus structural inspection of `2.1.4 Roll rate_student copy.xlsx`, `2.1.4 Vintage_student copy.xlsx`, `Vintage_filled.xlsx` | The exact DPD bucket scheme, MOB-method vs. Snapshot-method terminology, "roll backward/roll forward" vocabulary, an absorbing-state identification rule, and — importantly — confirmation from the actual answer-key workbook that the course's own worked examples are not internally consistent with each other (§6.1) |
| Model validation & calibration | The `Python notes/3.1 Model Validation/` series (7 files), `6187-Calibration.pdf`, `5266-Model Validation.pdf`, `2703-Model Validation – Masterclass-1 PPT.pdf`, and (skimmed, supplementary) `Rating validation.pdf` | The full rank-correlation/goodness-of-fit formula set, an explicit gap (no PSI/CSI stability bands given anywhere in the course material), the Jeffrey's Prior low-default-portfolio test, and a genuinely rich calibration chapter (TTC/PIT hybrid formula, bias-adjustment worked examples, Margin of Conservatism, three named calibration methods) that the KB summary had compressed to a single line (§17.1, §17.2, §17.3) |

**Two genuine inconsistencies were found inside the course's own material**
(not introduced by this project) and are flagged explicitly rather than
silently picked one way, consistent with this plan's evidence-in-code
standing rule:

1. **WOE sign convention is not consistent across the course's own files.**
   `3.1.4 Discriminatory Power - WOE,IV and Entropy.pdf` defines WOE as
   `ln(%bad / %good)`, which is the *opposite* sign convention from the one
   used elsewhere in this course and in Siddiqi's book (`ln(%good / %bad)`,
   the convention this plan has used since v1). **This notebook must state,
   in one explicit markdown cell, which convention it uses and why** — do
   not let the two conventions silently coexist across cells.
2. **"Augmentation" means two different things** depending on which primary
   source is being read — the P2T course's own reject-inference deck
   (`5650-Reject inferencing.pdf`) and the EXL whitepaper
   (`440475936-EXL-...pdf`) use the same word for materially different
   procedures. §12.1 states both definitions side by side and names which
   one this notebook means every time the word is used.

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

`1766-Introduction_Scorecard.pdf` (course primary source, new in v4) adds a
useful framing this plan didn't previously state explicitly: banks map
**product type to which of the three risk components a scorecard's design
should emphasize** — mortgage scorecards emphasize LGD, credit-card
scorecards emphasize EAD (revolving exposure), and **personal/installment
loan scorecards emphasize PD** — which is exactly Lending Club's product
shape. This is a small but real confirmation that a PD-first, account-level
application scorecard is the textbook-correct starting point for this
dataset, not just this project's own convenient choice.

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

This is a change from v2's single-notebook assumption — **confirmed with
Devesh**: build both notebooks, `01_pd_kgb_scorecard.ipynb` first
(§5–§11, §13–§18), then `02_pd_reject_inference_kigb.ipynb` (§12), and the
baseline AUC will be reassessed live rather than assumed, exactly as §11
already describes.

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
   sources (§0), the Peaks2Tails course files (§0.1), or from this session's
   own pre-build scouting (§4, §6, §11) are **not** substitutes for the
   notebook's own live computation — restate and re-derive, don't import as
   fact. This rule caught a real, previously undetected error in v1 of this
   document (an unreproducible baseline AUC) — treat it as load-bearing.
2. **Direct DuckDB connection** — `duckdb.connect(DUCKDB_FILE, read_only=True)`
   inline in each notebook, not the skill's stale `nb_setup.py` reference.
3. **No premature narrowing outside `03_data_cleaning`** — any feature
   considered and dropped needs an explicit, evidenced decision cell.
4. **Technique justification** — every point this notebook picks one
   technique over a plausible alternative (drawn from the tradeoffs the 10
   sources in §0 or the course files in §0.1 actually disagree on — e.g.
   fuzzy augmentation vs. parceling, pooled vs. per-vintage calibration,
   which WOE sign convention) gets a markdown cell answering "why this, not
   that," marked **[TJ]** in the cell plans below.

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
- **Minimum-sample governance rule (new in v4, `Types of scoring.pdf` —
  actually an FDIC examiner-manual excerpt within the course material):**
  a scorecard build is considered statistically supportable with roughly
  **≥1,000 goods, ≥1,000 bads, and ~750 usable rejects**. This project's
  accepted population (950,468 goods / 245,411 bads) clears this by a wide
  margin. The reject side does not automatically clear it — if live
  verification of `Policy Code = 2` (above) yields materially fewer than
  ~750 usable, scored-not-policy-rejected records, that is itself a finding
  to report in notebook 02 before proceeding with reject inference, not a
  detail to skip past.

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
    `creditrisk model building steps.pdf` (§0.1, new in v4) independently
    corroborates that the performance window should be set **from a vintage
    analysis** rather than picked arbitrarily — exactly what §6 does here.
  - *Measurement window*: the point at which `is_bad` is read off (i.e.
    `loan_status` at data-pull time) — already implicit in `windowed` but
    worth one restated sentence for a reader with no other context.

---

## 6. Vintage & cohort default-timing analysis — explicit scope boundary, now grounded in the course's own primary material

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

### 6.1 Peaks2Tails vintage & roll-rate mechanics, from the primary files (new in v4)

`2360-Vintage & Roll rate analysis .pdf` gives the course's own exact
vocabulary and mechanics, read directly rather than through the KB summary:

- **DPD bucket scheme**: `0 = Current`, `1 = 1-29 DPD`, `2 = 30-59 DPD`,
  `3 = 60-89 DPD`, `4 = 90+ DPD`.
- **Performance window (course definition)**: the MOB at which the
  *marginal* default rate peaks for a cohort — this is the same operational
  definition §5 already restates from SAS 3554-2019, now corroborated by an
  independent primary source.
- **Vintage method**: a 3-step build via a pivot table plus a `MATCH`-style
  lookup for each loan's first-default month — mechanically identical to
  what §6's MOB-curve approach above already plans to do in SQL/pandas
  rather than spreadsheet formulas.
- **Two named roll-rate computation methods**: **Snapshot-Method** (compare
  bucket at time *t* vs. bucket at time *t+1* across the whole live book)
  and **MOB-Method** (compare bucket at MOB *m* vs. MOB *m+1* within a single
  vintage cohort) — both require the monthly panel this dataset does not
  have (confirming, from the primary source itself, the scope boundary
  already stated above).
- **Directional vocabulary**: "**roll backward**" = a loan curing to a
  lower delinquency bucket; "**roll forward**" = a loan deteriorating to a
  higher bucket. **Absorbing-state identification rule**: a bucket is
  treated as the terminal/absorbing state once its **roll-backward rate
  shows a sharp dip** relative to earlier buckets (i.e. loans essentially
  stop curing past that point) — this is the course's own criterion for
  where a transition matrix's terminal state should be drawn, useful
  context even though this project cannot build the matrix itself.

**A second, different meaning of "roll rate" exists in this same course's
own material — flagged, not merged:** `Roll Rate.pdf` (a separate file,
folder `Credit Risk by P2T2`) uses "roll rate" for an **IFRS 9
simplified-approach loss-rate estimation method**: a **cumulative product of
ageing-bucket roll rates** (worked example in the file: `67% × 80% × 75% ×
17% × 100% = 7%` loss rate), with an additional macroeconomic-variable (MEV)
adjustment factor layered on top. This is a provisioning/ECL computation,
not the transition-matrix/vintage-curve sense of "roll rate" used everywhere
else in this section. **If this project's PD work is ever cross-referenced
against an IFRS 9/CECL provisioning phase, state explicitly which of the two
meanings is intended** — the course itself uses one word for two distinct
techniques.

**Excel-workbook structural inspection (new in v4) corroborates the scope
decision above, and surfaces a third finding — the course's own worked
answer key is internally inconsistent:**
- `2.1.4 Roll rate_student copy.xlsx` (198,433-row Fannie-Mae-style monthly
  panel) defines its absorbing state with `Bucket = IF(Delinquency >= 6, 6,
  Delinquency)` — i.e. **month 6** is treated as terminal.
- `Vintage_filled.xlsx` (the course's own answer key, 761,404-row panel)
  defines a related but different field with `Delinq Status = IF(Bucket > 3,
  4, Bucket)` — i.e. **month 4** is treated as terminal for vintage-curve
  purposes in that workbook.
- These are not necessarily wrong in isolation (a roll-rate transition
  matrix and a vintage-curve aggregation can legitimately use different
  truncation points), but the course provides no stated reconciliation
  between them. **This project should pick and justify its own single
  answer** (already effectively resolved: charge-off, not a fixed DPD
  bucket, is this dataset's terminal state — §4) rather than import either
  of the course's two numbers uncritically.

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

### 8.1 The IMPORTANT business-filter mnemonic, VARCLUS, and a full numeric-threshold table (new in v4, `5345-Variable Selection.pdf`)

The course primary source lays out a **4-tier variable-selection taxonomy**
(Basic → Statistical → Wrapper → Embedded filters) that this plan's own
IV-threshold + multicollinearity approach above already sits inside (IV is
a Statistical filter; the stepwise option is a Wrapper filter). Two pieces
of this taxonomy are new to this plan and worth adding explicitly:

- **The IMPORTANT mnemonic** — a *business/qualitative* filter applied
  before or alongside the statistical filters, for judging whether a
  candidate variable is fit to use in a real lending decision at all, not
  just statistically predictive: **I**mplementable, **M**anipulative
  (can the applicant game it?), **P**olicy (does using it violate lending
  policy or fair-lending law?), **O**bjective, **R**ecognisable
  (interpretable to a business user), **T**ransparency, **A**vailable (at
  the point of decision — critically relevant to the `grade`/`int_rate`
  decision in §10, since neither exists at application time in a real
  deployment, only after underwriting), **N**ecessary, **T**ailored. This
  project's `grade`/`int_rate` near-definitional problem (§10) is, in
  IMPORTANT terms, an **Availability** failure as much as a statistical
  leakage concern — worth stating in the §10 **[TJ]** cell using this
  vocabulary, since it makes the "why not just keep it" tradeoff concrete
  in deployment terms, not just IV-suspicion terms.
- **PROC VARCLUS** (a SAS clustering-based method mentioned in the same
  file): groups correlated candidate variables into clusters and picks one
  representative per cluster — an alternative to this plan's own pairwise
  correlation/VIF check (below) for handling multicollinearity among the
  WOE-transformed candidates. Flagged as an alternative worth a **[TJ]**
  mention (why a simpler pairwise/VIF check is used here instead of a full
  clustering approach — proportionate to this project's much smaller
  candidate-variable count than a typical bank build).
- **Exact regularization penalty formulas** given in the same file, useful
  if this notebook's optional stepwise/embedded selection step uses a
  penalized regression instead of plain stepwise logistic regression:
  Lasso `= λ Σ|β|`, Ridge `= λ Σβ²`, Elastic Net `= λ₁Σ|β| + λ₂Σβ²` (two
  separate penalty weights, not one blended term).
- **A full numeric-threshold table** the course gives for judging
  variables and the final model (values to re-derive and compare against
  live, per the evidence-in-code rule — not to hard-code as pass/fail
  gates without restating them in the notebook):

| Check | Course threshold |
|---|---|
| CSI (Characteristic Stability Index, per-variable) | < 0.1 |
| Variable-level Gini | > 0.1 |
| Information Value | > 0.02 |
| Pairwise correlation (WOE-transformed candidates) | < 0.5 |
| VIF | < 2–3 |
| Model AUC | > 0.7 |
| Model Gini | > 0.4–0.5 |
| Model PSI | < 0.1 |

This table is a useful independent cross-check for §11's baseline (live
re-derivation landed at 0.68–0.69 AUC, §11 — below this table's ">0.7"
convention, worth stating as an honest gap rather than smoothing over it)
and for §17's stability checks.

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

### 9.1 The SIMPLE binning mnemonic, Marginal IV, and the master classing pipeline (new in v4, `9901-Binning.pdf`, `Marginal IV.pdf`)

The course's binning deck gives a **named, checkable acceptance test for
any candidate bin structure** — this project's existing binning rules above
(≤8 coarse bins, >2% population, >50 bads, monotonic WOE) are, it turns out,
already most of this mnemonic; stating it explicitly gives the notebook a
single markdown cell that checks all of it at once rather than four
separate ad hoc rules:

**SIMPLE** — **S**: |ΔWOE| between adjacent bins > 0.2 (bins too similar to
justify being separate otherwise); **I**: IV drop from fine to coarse
classing ≤ 30% (coarsening shouldn't destroy most of the variable's
predictive power); **M**: Monotonic WOE across bins; **P**: each bin's
population *and* bad count > 5% of the total (this project's existing
>2%-population / >50-bads rules are a close variant — restate against the
course's 5% convention explicitly and pick one, don't run both silently);
**L**: 3–10 bins total; **E**: no bin with zero goods or zero bads (a WOE of
±∞).

**Master pipeline** (`9901-Binning.pdf`, worked with real bureau-score/MOB/
vintage-year examples in the source): fine classing → drop low-IV
candidates → coarse classing → drop any bin structure failing SIMPLE →
compute CSI per bin → drop high-CSI (unstable) bins → final variable
selection by **Highest IV**, **Marginal IV**, **Marginal Chi-square**, or
**Marginal KS** (four alternative final-cut criteria the course presents as
options, not a single mandated one — **[TJ]** which one this notebook uses
and why, most likely Marginal IV given the formula below is already
available).

**Marginal IV formula** (`Marginal IV.pdf`): for a candidate variable
already in a working model, `miv = miv_g − miv_b`, where
`delta = WoE_observed − WoE_expected` per bin (WoE recomputed with the
candidate variable added vs. without it), aggregated to goods (`miv_g`) and
bads (`miv_b`) separately. Course threshold: **miv ≈ 0.02** as the bar for
"adding this variable still contributes meaningfully" — the same numeric
threshold as plain IV's "useless" cutoff (§8 table), applied incrementally
rather than standalone.

**WOE sign-convention flag (restated from §0.1):** this pipeline and
`9901-Binning.pdf` use `WOE = ln(%good / %good_total ÷ %bad / %bad_total)`
i.e. `ln(%good/%bad)` — consistent with this plan's convention since v1.
`3.1.4 Discriminatory Power - WOE,IV and Entropy.pdf` (also read this
session, part of the model-validation research pass) defines WOE with the
*opposite* sign, `ln(%bad/%good)`. **State the convention this notebook
uses in one explicit cell** (§3, rule 4) — this is not a hypothetical risk,
it is a documented inconsistency inside the very course this project draws
on.

The same file's **entropy-based alternative discriminatory-power measures**
(Entropy, Unconditional Entropy, Conditional Entropy, KL Divergence, and a
combined CIER statistic) are noted here for completeness but **the course
gives no threshold for CIER** — if this notebook computes it as a secondary
diagnostic, report it as descriptive only, not as a pass/fail gate (an
honest gap, same treatment as PSI/CSI's missing bands, §17.1).

---

## 10. Grade/int_rate near-definitional decision (unchanged from v2)

Option A (keep both, document why) vs. Option B (engineer around them,
`dti` as the leading mechanistic alternative) — **[TJ]** cell, citing live
IV. Source 7's caution against "over-dependence on one dominant variable"
is the additional citation for why this decision matters, not just KB's own
IV-suspicion threshold. Per §8.1's IMPORTANT mnemonic, frame part of this
decision explicitly in **Availability** terms — a real deployment scores
applicants before either `grade` or `int_rate` exists — not only in
statistical-leakage terms.

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
  Note against §8.1's table: the course's own ">0.7 AUC" convention is a
  general rule of thumb from a richer-feature-set bank context, not a
  target to force this project's number to match by adding leakage-prone
  fields.

### 11.1 Logistic-regression appropriateness checks and cutoff mechanics, from the primary files (new in v4)

`1423-Logistic Regression.pdf` gives a full derivation (MLE, Wald test,
likelihood-ratio test, score test) plus a **named mnemonic (CATEGORICAL)**
for pre-modeling appropriateness checks on the target/feature setup. The
research pass that read this file confirmed the mnemonic exists and covers
this kind of checklist, but did not capture a verified letter-by-letter
breakdown reliable enough to restate here without risking a fabricated
mapping — **the notebook's own **[TJ]** cell should open the source PDF
directly and quote the mnemonic verbatim**, rather than trust a paraphrase,
consistent with this plan's own evidence-in-code rule (§3, rule 1). The same
file's fully worked example (AUC = 0.9238, KS = 0.6769) is a useful sanity
reference for what a strong, richly-featured bank scorecard looks like — not
a target for this notebook's own number, which uses far fewer fields.

The same file also gives a **7-step Hosmer-Lemeshow goodness-of-fit
recipe**, which §17.1 restates in the validation context; and
`creditrisk model building steps.pdf` (81pp, an independently useful
end-to-end sequence: Objective → Exclusions → Observation window →
Performance window via Vintage Analysis → Bad definition via roll-rate
analysis with an indeterminate-population cap under 20% → Segmentation →
a 7-stage variable-selection sequence → `PROC LOGISTIC` stepwise fitting →
validation with **KS < 20 (or < 15 in stricter conventions) as a red-flag
threshold** and a restated PSI formula → recalibration) independently
corroborates that this plan's own step order (§5 → §6 → §7 → §8/§9 → §10 →
§11 → §13-17 → §18) matches real bank practice, section for section, not
just at the level of individual technique names.

`7695-Cutoff.pdf` gives the mechanics that belong in §16 (scaling) and in
this notebook's decisioning step:
- **Statistical cutoff frameworks**: Bayes, Minimax, and Neyman-Pearson —
  three named decision-theoretic approaches to picking a score cutoff from
  the model's predicted probabilities, distinct from a purely
  business-driven cutoff.
- **Business cutoff**, via an explicit profit formula: `Net Profit = (Goods
  approved × average profit per good) − (Bads approved × average loss per
  bad)`. This project has no real unit-economics inputs (no charged-off
  loss-given-default figure until Phase 2, no funding-cost figure) — state
  this explicitly as the reason a business cutoff is illustrative only in
  this notebook, not a production recommendation.
- **Hard cutoff vs. soft/3-zone cutoff** (approve / refer-for-review /
  decline) — worth one **[TJ]** sentence on which this notebook demonstrates,
  most likely a hard cutoff for simplicity given the illustrative nature of
  the profit inputs above.

---

## 12. Reject inference — `02_pd_reject_inference_kigb.ipynb` (brought into Phase 1's actual scope in v3; v4 grounds every step in the course's own primary formulas)

Every source in §0 that covers reject inference (1, 2, 3, 5, 6, 8) treats it
as a real step with real limitations, not a checkbox. This section is
written accordingly — including the parts where the honest answer is "this
dataset makes that harder than the textbook version."

**The course's own reject-population checklist** (`5650-Reject
inferencing.pdf`, read directly this session) states explicitly which
reject sub-populations should feed reject inference: **Policy rejects → No.
Low-score (scored, declined) rejects → Yes. Indeterminates → Yes. Non-take-
ups (approved but didn't fund) → Yes.** This project's data only supports
the first two categories — Lending Club's rejected-file schema (§4) has no
way to identify indeterminates or non-take-ups (no loan-outcome field
exists on the reject side at all, only application-level fields) — state
this as an explicit, evidenced scope limit in notebook 02's opening cell,
not an implicit omission.

**Step-by-step (SAS 3554-2019's KGB→KIGB shape, source 2, adapted to this
project's actual field constraints, §4, and to the course's own exact
mechanics below):**

1. **Load the rejected file** (27,648,741 rows) via DuckDB's CSV reader
   (not pandas — the earlier live OOM-kill of a full-file pandas load this
   session is itself evidence for why: cite it as a live technical note).
2. **Exclude policy rejects** — filter to `Policy Code = 2` (88,129 rows,
   live-counted) as the working "scored, not policy-rejected" population,
   **after confirming live** (via `Risk_Score`'s completeness/distribution
   within each code) that code `2` is actually the scored population and
   not something else — do not assume the mapping from this document. Cross-
   check against §4's minimum-sample rule (~750 usable rejects) once this
   is confirmed.
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
   randomly-labeled record (parceling) or a single hard label (cutoff). The
   course's own primary source gives the **exact mechanics and a fully
   worked numeric example** for both augmentation and parceling — see the
   worked Penalty Factor example immediately below; restate it verbatim in
   the notebook's **[TJ]** cell rather than paraphrase, since this is the
   one part of the technique where getting the exact weighting formula
   right matters for reproducibility.
6. **Assemble the KIGB dataset**: accepts (§7's train split) + weighted
   synthetic reject records.
7. **Re-derive WOE/IV on KIGB** using the **same bin edges fit on the KGB
   train set** (source 5's MathWorks workflow: "apply identical binning
   rules from the base model to ensure consistency") — do not refit bins on
   the combined population.
8. **Refit logistic regression on KIGB** (overlap-only feature set, per
   step 3's constraint).
9. **Validate reject inference itself before trusting the KIGB model** —
   the course's own primary source states this as **two named, mandatory
   checks**, not general good practice: the inferred bad rate among
   rejects must be **"Conservative"** (higher than the KGB/booked
   population's bad rate — rejects should look riskier than accepts, since
   they were declined) and **"Monotonic"** (the inferred bad rate must
   decrease as score rises, exactly as it does in the KGB population) — if
   either check fails, the inference is broken and should not be used, not
   silently accepted. (KB §8.2 already stated a version of this; §0.1's
   direct read confirms this is the course's own exact named terminology,
   not a KB paraphrase.)
10. **Compare KGB vs. KIGB** on the **overlap-only feature set for both**
    (an apples-to-apples comparison — comparing a full-feature KGB against
    an overlap-only KIGB would confound "reject inference helped" with
    "fewer features hurt"): AUC/KS/Gini on test and OOT, plus a **swap-set
    analysis** — the course's primary source works through this mechanic
    with two full numeric exercises: cross-tabulate which loans each model
    would approve/decline at a shared cutoff, and examine the "swap-in"
    (KIGB approves, KGB would have declined) and "swap-out" (KIGB declines,
    KGB would have approved) cells specifically for their realized/inferred
    bad rates — a materially bad swap-in cell is itself a red flag on the
    inference, independent of the aggregate AUC/KS/Gini comparison.
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

### 12.1 Worked penalty-factor example, and the EXL paper's 4-method comparison (new in v4)

**Worked augmentation/parceling example** (`5650-Reject inferencing.pdf`):
the course walks through a fully worked numeric example computing a
**Penalizing Factor = 6.618**, used to reweight each score band's accepted
population up to represent the band's share of the *combined* (accept +
reject) through-the-door population before the synthetic reject records are
added — i.e. the penalty factor corrects for the fact that low scoring bands
are under-represented in the accepts-only population precisely because they
were disproportionately rejected. **Restate this exact mechanic and re-derive
this project's own penalty factor live** (it will not be 6.618 — that
number is specific to the course's own worked dataset) — this is exactly
the evidence-in-code rule applied to a course-internal number, the same
treatment already given to the external sources' baseline-AUC-style
figures.

**A second, independent real-world source on reject inference** — the EXL
Decision Analytics whitepaper (`440475936-EXL-Acquisition-Scorecard-Reject-
Inference-Methodologies.pdf`, 2016, found in the same course folder but a
genuine external vendor publication, not a P2T-authored teaching file) gives
a **4-method comparison with a worked Gini/KS/AUC table**:

| Method | Mechanic (EXL's definition) |
|---|---|
| Hard Cutoff | Rejects below a chosen score are simply labeled bad; no probabilistic weighting |
| Single Weighted | Rejects are reweighted once, using a single set of weights derived from the accept/reject score-band ratio |
| Double Weighted | Rejects are reweighted twice — once for accept/reject sampling bias, once for the scored-probability-to-label assignment — a refinement of Single Weighted |
| Augmentation | **EXL's own definition, and this is the second flagged inconsistency from §0.1**: EXL uses "Augmentation" for a reweighting scheme closer to what the P2T course itself calls "parceling" (label assignment by probability band, not the P2T course's own fuzzy-duplication procedure in step 5 above). **The two source materials in this same folder use the identical word for different procedures.** |

**EXL's own explicit conditional recommendation** (worth restating verbatim
in the notebook, not softened into "it depends"): use **Double Weighted**
when the business objective is *growing the approval rate without hurting
portfolio quality*; use **Hard Cutoff** when the objective is instead
*identifying additional bads within an already-high-approval-rate
through-the-door population*. This project's own objective (§1 — building a
representative, generalizable PD scorecard, not optimizing a specific
approval-rate target) sits closer to the Double Weighted framing, but
**state this as a [TJ] decision explicitly**, don't inherit EXL's
recommendation silently — EXL's context (a live approval-rate-optimization
engagement) is not identical to this project's context (a portfolio
research build).

**Given the terminology collision, this notebook's own [TJ] cell in step 5
above must state plainly**: "this notebook's 'augmentation' means
[fuzzy-duplication / EXL's probability-band reweighting] — see §12.1 for why
the same word means something different in the EXL paper read alongside
this course's own material."

---

## 13. Master Rating Scale validation

Unchanged from v2 — grade concentration, monotonicity (A→G, A1→A5),
AUC(grade-alone) vs. AUC(full model). **New decision needed**: run this
against the KGB model, the KIGB model, or both — state the choice
explicitly once §12 is complete; if §12's comparison shows KIGB
materially different, MRS validation should use whichever model is
designated the production candidate, not both by default.

---

## 14. TTC/PIT decision

Unchanged mechanics from v2 (does `issue_year`/drift enter as a feature vs.
monitoring-only) — **now also informed by §6's vintage-curve finding**, not
just the `int_rate` PSI number alone, **and by §17.2's TTC/PIT hybrid
formula** (read directly from `6187-Calibration.pdf`, new in v4) — this
decision and the calibration-hybrid-weighting decision in §17.2 are the same
underlying question asked twice (does this model/PD estimate track the
cycle or not) and should cite each other rather than being answered
independently. **[TJ]** cell citing both.

---

## 15. Calibration

Unchanged from v2 — Method 1 (log-odds regression) to the live bad rate
(~20.5%, re-verify), pooled default with per-vintage check — **[TJ]** Method
1 vs. isotonic/Platt scaling vs. the two additional named methods from the
course's calibration chapter (Tasche Binormal, Tasche QMM — §17.2).

---

## 16. Scaling to points, and adverse-action reason codes

No prior version of this plan had this step at all before v3, despite it
being a named, concrete step in three of the ten sources (2, 4, and
implicitly the KB's own PDO mention) and a genuine US lending regulatory
requirement (ECOA), not an optional nice-to-have, for any scorecard framed
as decisioning real applicants:

- **PDO scaling** (Points to Double the Odds): `Score = Offset + Factor ×
  ln(Odds)`, where `Factor = PDO / ln(2)` and `Offset = Score −
  Factor × ln(Odds)` (both formulas confirmed directly from `7695-
  Cutoff.pdf`, new in v4 — previously this plan only had the first
  equation). **Fully worked example from the same source, useful as a
  worked-arithmetic sanity check for this notebook's own implementation
  (not this project's actual parameters):** target Score = 600 at Odds =
  20:1, PDO = 50 → `Factor = 50 / ln(2) ≈ 72.13`, `Offset = 600 − 72.13 ×
  ln(20) ≈ 383.90`. Source 2's own illustrative parameters (base score 200,
  base odds 50:1, PDO 20) remain a second valid example — **pick and
  document this project's own base score/base odds/PDO choice in a [TJ]
  cell**; either the 600/20:1/50 or 200/50:1/20 convention is defensible,
  state the choice and why.
- **Per-bin points formula** (standard scorecard-scaling algebra, confirmed
  consistent with `7695-Cutoff.pdf`'s treatment): for a WOE-transformed bin
  with coefficient `β_i` and `n` total variables in the model, that bin's
  point contribution is `Points_i = −(WOE_i × β_i + α/n) × Factor`, with the
  base `Offset` distributed evenly across variables (`Offset/n` per
  variable) so that all bins' points sum correctly to the target base score
  at the reference odds. Implement as a live-computed table per variable
  per bin, not just described.
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
not a substitute for Phase 5's dedicated pass. §17.1–§17.3 below record what
this session's direct reading of the course's validation and calibration
primary sources added — most of the *richest* material (the full formula
set, the calibration deep-dive, the governance detail) belongs to Phase 5's
fuller treatment, not this notebook's first pass, and is recorded here so it
is not lost between now and Phase 5.

### 17.1 Full discriminatory-power and goodness-of-fit formula set (new in v4, `Python notes/3.1 Model Validation/` series)

Read directly (7 files: ROC/Goods-vs-Bads, KS/CAP, Confusion Matrix,
Gamma/Somers'D/Kendall Tau, PSI/CSI, K-score/HL/Brier, plus
`5266-Model Validation.pdf`):

- **Rank-correlation family** (beyond AUC/Gini, already planned): **Gamma**,
  **Somers' D**, and **Kendall's Tau-b** — three related concordance-based
  statistics the course presents as a family alongside AUC. Worth computing
  as a small additional table in Phase 5's fuller pass (not required for
  this notebook's first-pass check) since they're already implemented in
  most stats libraries once concordant/discordant pairs are being computed
  for AUC anyway.
- **PSI/CSI — an explicit, stated gap**: the course's own PSI/CSI material
  gives the formula but **no stability bands (thresholds) anywhere in the
  material read this session** — i.e. the course does not commit to a
  "PSI < 0.1 stable / 0.1–0.25 watch / > 0.25 unstable" convention the way
  many industry references do. **This project must state its own chosen
  convention explicitly** rather than imply it came from the course — the
  0.1/0.25 convention already used informally elsewhere in this project's
  Phase 0 work is a reasonable industry-standard default to cite instead,
  attributed to general practice, not to Peaks2Tails.
- **K*-Score**: three named variants are described in the course material
  (an alternative rank-based discriminatory-power measure to AUC/KS) — noted
  for Phase 5's fuller suite; not load-bearing for this notebook's
  first-pass check.
- **Hosmer-Lemeshow** — the 7-step recipe already noted in §11.1
  (`1423-Logistic Regression.pdf`), corroborated by the validation-focused
  files as a standard goodness-of-fit check for the fitted probabilities,
  not just the ranking.
- **Brier score** — standard mean-squared-error-of-probabilities
  calibration check, alongside Hosmer-Lemeshow.
- **Jeffrey's Prior low-default-portfolio (LDP) test** (`5266-Model
  Validation.pdf`): `Posterior ~ Beta(0.5 + d, 0.5 + n − d)`, where `d` =
  observed defaults and `n` = number of accounts in a rating grade/segment
  — a Bayesian test specifically designed for segments with very few or
  zero observed defaults, where a standard binomial test has no power. The
  course's own worked example uses `n = 6, d = 0`. **Directly relevant to
  this project's own grade G segment** (8,410 loans but a comparatively
  small absolute bad count relative to A-C) — worth a **[TJ]** note on
  whether grade-level validation for the smallest/lowest-default segments
  should use this test instead of a plain binomial/normal-approximation
  test, in Phase 5's fuller pass.
- **Bayesian theoretical error-rate formula** (same source): `Error =
  %Good × FPR + %Bad × FNR` — a simple decomposition worth including
  alongside the confusion-matrix-derived metrics.
- **A correctness flag, not a technique to adopt**: the confusion-matrix
  file in this series uses a `.iloc`-based indexing convention for reading
  off TP/FP/TN/FN that is non-standard and easy to get backwards — if this
  notebook's own confusion-matrix code is modeled on that file's approach
  at all, cross-check the result against `sklearn.metrics.confusion_matrix`
  output directly rather than trusting positional indexing alone.

### 17.2 Calibration — the richest primary source read this session (new in v4, `6187-Calibration.pdf`, 35pp)

The KB's existing calibration summary (§15) compresses this file to
essentially one line (log-odds regression to a target bad rate). Reading
the primary source directly surfaced substantially more:

- **Data-representativeness pass criterion**: the development sample used
  for calibration should represent at least **85%** of the population the
  calibrated model will actually be applied to (a stated numeric bar, not
  just a qualitative "make sure it's representative").
- **TTC/PIT hybrid formula**, with a **30% cyclicality cap**: rather than a
  binary TTC-vs-PIT choice (§14), the course gives a blended formula that
  caps how much of the point-in-time (cyclical) component is allowed to
  move the final calibrated PD away from the through-the-cycle anchor —
  the course's own worked example computes a blended result of **11.19%**.
  Restate the exact formula in the notebook (from the source directly, per
  the evidence-in-code rule) rather than this paraphrase, if this
  hybrid approach is adopted in §14 instead of a pure TTC or pure PIT
  choice.
- **Bias-adjustment worked examples** for four named effects: **seasonality**
  (calendar-month effects on observed default rates), **seasoning**
  (MOB-dependent risk that isn't yet captured because a cohort hasn't aged
  enough — directly relevant to §6's immaturity finding for the 2016/2017
  vintages), **recency bias** (over-weighting the most recent, possibly
  unrepresentative, performance data), and a **short-term-exit** adjustment
  (loans that exit the portfolio quickly, e.g. via early payoff, before
  their true risk would have manifested). Each has a worked numeric
  adjustment example in the source — directly relevant scope for Phase 5's
  fuller calibration pass given this project's own 2013–2017 vintage span
  already shows uneven cohort maturity (§6).
- **Margin of Conservatism (MoC)** — three named categories (**A**, **B**,
  **C**, roughly increasing in severity/data-quality concern) that
  determine how much conservative buffer to add to a calibrated PD
  estimate. Not previously in any version of this plan at all.
- **Three named calibration methods**, only one of which (#1) this plan
  previously listed: **(1) Log-Odds Regression** (already §15's Method 1),
  **(2) Tasche Binormal**, and **(3) Tasche QMM** (quasi-moment-matching) —
  both attributed to Dirk Tasche's published calibration work. The research
  pass that read this file confirmed both methods are presented with full
  formulas and worked parameters in the source, but — consistent with
  §11.1's treatment of the CATEGORICAL mnemonic — **the exact formulas
  should be pulled directly from `6187-Calibration.pdf` at notebook-build
  time** rather than restated secondhand here, since a calibration formula
  is exactly the kind of thing this plan's own evidence-in-code rule exists
  to protect against transcription error on.

### 17.3 Governance detail, for cross-reference with §19 (new in v4, `2703-Model Validation – Masterclass-1 PPT.pdf`, and supplementary `Rating validation.pdf`)

- Confirms the **3 Lines of Defense** structure already referenced in §19
  (Phase 5's plan already gives SR 11-7's three-lines framing the same
  "context, not implemented" treatment) — this course file is the direct
  MRM-training-deck source for that same structure, not a new framework to
  add.
- A **validation-type competency matrix** using four named validation
  categories abbreviated **IV / PV / AR / OPA** in the source slides — the
  research pass that read this file did not capture confirmed full-word
  expansions reliable enough to restate here; **confirm the expansions
  directly from the source slide at Phase 5 build time** rather than guess,
  same treatment as the CATEGORICAL mnemonic and the Tasche formulas above.
- **Validation-lifecycle timing differs for regulatory vs. non-regulatory
  models** (e.g. differing revalidation cadences) — relevant context for
  Phase 5's own validation-cadence section, not this notebook.
- **Supplementary, skimmed only**: `Rating validation.pdf` (a Bank of Japan
  paper, more corporate/general-ratings-oriented than retail-scorecard-
  specific) adds two cross-check concepts worth carrying into Phase 5: the
  **ex-ante vs. ex-post validation** distinction (validating a rating
  system's design assumptions before use, vs. validating its realized
  performance after use), and **rating-migration-matrix validation** as a
  supplementary check alongside discriminatory-power and calibration
  testing — both standard in general ratings validation literature, useful
  as additional Phase 5 scope, not required reading for this notebook.

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

## 19. Governance note (brief — context, not a project deliverable)

Source 2's own closing section describes a 3-team model lifecycle (Model
Development / Model Validation / Model Risk Management) governing any real
bank scorecard's ongoing life — corroborated directly by §17.3's reading of
the course's own MRM masterclass deck. **State this in the notebook's
closing markdown as context, not as a structure this solo portfolio project
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
- [x] Two-notebook structure decided, stated explicitly, and **confirmed
  by Devesh** (§1) — build order is `01_pd_kgb_scorecard.ipynb` first,
  then `02_pd_reject_inference_kigb.ipynb`.
- [x] Direct primary-source read of the Peaks2Tails course files for all
  five PD-scorecard topics (WOE binning/variable selection, logistic
  regression/scorecard/cutoff, reject inference, vintage/roll-rate, model
  validation/calibration) — not just the KB summary — with two genuine
  cross-file inconsistencies in the course's own material flagged rather
  than silently resolved (§0.1, §9.1, §12.1, §6.1).
- [ ] Confirm `Policy Code = 2`'s actual meaning live (§4, §12 step 2)
  before building any reject-inference logic on top of that assumption, and
  check the resulting usable-reject count against the ~750-record minimum-
  sample rule (§4).
- [ ] Build `01_pd_kgb_scorecard.ipynb` per §5–§11, §13–§18, section by
  section, shown to Devesh before each is committed.
- [ ] Build `02_pd_reject_inference_kigb.ipynb` per §12/§12.1, including the
  overlap-only sub-model, the live-re-derived penalty factor, the two
  named Conservative/Monotonic validation checks, the swap-set analysis,
  and the honest KGB-vs-KIGB comparison.
- [ ] Vintage/cohort curve built and its finding fed into §7's OOT-validity
  check and §14's TTC/PIT decision.
- [ ] Reason codes and PDO scaling implemented (§16), including a **[TJ]**
  choice of base score/odds/PDO convention.
- [ ] Every **[TJ]**-marked decision has its markdown cell, evidenced —
  including, new in v4: the WOE sign-convention choice (§9.1), the
  "augmentation" terminology choice (§12.1), and the CATEGORICAL mnemonic
  and Tasche calibration formulas pulled directly from source at build
  time rather than paraphrased from this document (§11.1, §17.2).
- [ ] Standard production-readiness audit on both notebooks before calling
  Phase 1 done.
- [ ] Commit only the new notebook/model files — same git discipline as
  every prior phase (force-add needed while `docs/`/new folders remain
  outside whatever `.gitignore` currently allows — verify per-folder before
  committing, don't assume).

---

## References

- `docs/phase_0_report.md`, `docs/Peaks2Tails_Knowledge_Base.md` §8–§10,
  §17, §19 — unchanged from v2/v3; §19 is the KB's own file-by-file source
  map that made the direct primary-source reads in §0.1 possible.
- `credit-risk-curriculum` skill, reference files 03/04 — unchanged from
  v2/v3, same staleness caveats apply.
- §0's 10 external sources — unchanged from v3.
- §0.1's Peaks2Tails primary-source files — new in v4; re-consult these
  files directly, not this document's paraphrase of them, before
  implementing the CATEGORICAL mnemonic, the Tasche calibration formulas,
  or the IV/PV/AR/OPA validation-matrix expansions, all three of which this
  document explicitly declined to restate secondhand.

---

## Changelog

- **v4 (this revision)**: enriched every section against the actual
  Peaks2Tails course primary-source files (PDFs and Excel workbooks), not
  the KB's summary of them, per Devesh's explicit instruction — new §0.1
  (source citation table); new §6.1 (exact vintage/roll-rate mechanics,
  DPD buckets, MOB-vs-Snapshot method, roll-backward/forward terminology,
  and a discovered internal inconsistency between two of the course's own
  worked-example Excel workbooks); new §8.1 (IMPORTANT business-filter
  mnemonic, VARCLUS, regularization formulas, full numeric-threshold
  table); new §9.1 (SIMPLE binning mnemonic, master classing pipeline,
  Marginal IV formula, and a flagged WOE sign-convention inconsistency
  within the course's own material); new §11.1 (logistic-regression
  appropriateness-check context, Hosmer-Lemeshow recipe, statistical/
  business cutoff mechanics); expanded §12 and new §12.1 (exact augmentation/
  parceling penalty-factor worked example, the course's explicit reject-
  population checklist, swap-set analysis mechanics, and a second
  independent source — the EXL whitepaper — with its own 4-method
  comparison, explicit conditional recommendation, and a flagged
  terminology collision on the word "Augmentation" between the two
  sources); reworked §16 with the exact PDO scaling formula plus a fully
  worked numeric example and the per-bin points formula; new §17.1–§17.3
  (full rank-correlation/goodness-of-fit formula set with an explicit
  PSI/CSI stability-band gap, the Jeffrey's Prior low-default-portfolio
  test, a substantially richer calibration section from the course's own
  35-page calibration chapter — TTC/PIT hybrid formula, bias-adjustment
  worked examples, Margin of Conservatism, three named calibration methods
  — and governance/validation-competency detail for cross-reference with
  Phase 5). Two genuine cross-file inconsistencies inside the course's own
  material are flagged for explicit, stated resolution in the notebooks
  rather than silently picked one way: the WOE sign convention, and the
  word "Augmentation." Three items are explicitly *not* restated secondhand
  in this document, on the same evidence-in-code grounds as everything
  else here, and must be pulled directly from source at build time: the
  CATEGORICAL mnemonic's exact letter mapping, the Tasche Binormal/QMM
  calibration formulas, and the IV/PV/AR/OPA validation-matrix expansions.
- **v3**: rebuilt against 10 external real-world sources (§0) chosen to
  mirror actual bank practice. Added: event/window restatement (§5);
  vintage/cohort default-timing analysis with an explicit, evidenced scope
  boundary against full roll-rate transition matrices (§6); reject
  inference brought into Phase 1's actual scope as its own notebook,
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
