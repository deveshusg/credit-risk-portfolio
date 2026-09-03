# Credit Risk Portfolio — Master Project Context

**Purpose of this document:** a complete, standalone record of everything covered
in the Cowork conversation that has been driving this repository — the
Peaks2Tails course background, what's being built and why, every standing rule
and style convention, the full notebook-by-notebook history (decisions, bugs
found and fixed, data findings), the review workflow, the git/branching setup,
and the open items still ahead. It exists so a new session — the VS Code Claude
Code extension, a future Cowork session, or a human collaborator — can pick up
this project with (as close as text allows to) the same context as the session
that built it. Nothing below is trimmed for brevity; where something is
genuinely voluminous (like the full Peaks2Tails knowledge base), this document
gives the complete synthesis and points to the companion file that holds the
exhaustive version.

**Companion files in this repo:**
- `CLAUDE.md` (repo root) — the short version of this document, auto-loaded by
  Claude Code at session start. This file is the long version; `CLAUDE.md`
  should stay a condensed pointer to it.
- `docs/Peaks2Tails_Knowledge_Base.md` — the full 16-section, ~660-line
  knowledge base compiled from all 60 files (slide decks, handwritten notes,
  regulatory documents, Excel case studies) in the user's Peaks2Tails credit
  risk modeling course folder. Section 2 below is a condensed synthesis of it;
  read the full file for exhaustive detail, worked examples, and the
  file-by-file source map.

---

## 1. Bird's-Eye View — What This Project Is, In One Page

Devesh completed a 60-deck credit risk modeling course called **Peaks2Tails**
("Integrated Credit Risk Modelling in Banks," instructor Karan Aggarwal),
covering the full lifecycle of bank credit risk modeling: scorecard/PD
development, model validation, calibration, LGD/EAD/CCF modeling, Basel
capital/RWA, IFRS 9 / CECL expected credit loss, stress testing, and the
statistical/ML toolkit underneath all of it.

**This repository is where that course material gets applied end-to-end
against a real, public dataset** — Lending Club's accepted-loans data
(2007–2018, ~2.26M rows, 151 raw columns) — to produce a **public-facing
portfolio project**: something to show employers and recruiters as evidence
of applied credit risk modeling skill, not just a private study exercise.

The project is explicitly phased:

- **Phase 0 (current, in progress):** `phase0_data_platform/01_lendingclub/` —
  a 16-notebook exploratory data analysis (EDA) and data-understanding suite,
  plus a data-cleaning/feature-prep notebook. This is the foundation: get to
  know the data exhaustively, understand every column, establish what's
  missing and why, flag quality issues, and produce a clean, well-justified,
  well-documented base for modeling. Nothing in Phase 0 fits or trains a
  model.
- **Later phases (not yet built, but the reason Phase 0's decisions need to
  stay compatible with them):** the actual modeling stack the Peaks2Tails
  course teaches — scorecard/PD modeling, validation, calibration, LGD/EAD,
  and IFRS 9 ECL computation, applied to this same dataset.

The working method for Phase 0, established over many rounds of this
conversation, is a **one-notebook-at-a-time manual review workflow**: Claude
proposes or revises a notebook, shows the user the full markdown + code +
output content in chat, the user comments, Claude iterates, and only once the
user explicitly says "go ahead" does the change get synced to disk and
(usually) locally committed to git — never pushed, since push credentials are
never available to the sandboxed side of this workflow.

Three rules have stood, unchanged, since early in the project and govern
every notebook in the suite (full detail in §4):

1. **Evidence-in-code** — every markdown factual/numeric claim must be
   demonstrated by actual code and printed output in the same notebook.
2. **Shared connection helper only** — every notebook uses
   `notebooks/_shared/nb_setup.py`'s `connect()` (read-only) or
   `create_fresh()` (ingestion notebook only).
3. **No premature column narrowing** — EDA notebooks don't drop columns or
   presuppose modeling outcomes; only `03_data_cleaning` narrows scope, and
   only with explicit justification.

On top of those three, a fourth principle was established mid-sweep and
applies retroactively to every notebook: **wherever a notable pattern shows up
(especially high missingness), the markdown must actually explain the
variable** — what it means, what kind of variable it is, whether its
missingness is itself signal, whether/how it should be used in modeling,
whether it needs further analysis, and how it would be treated. This is
treated as the actual point of doing EDA at all, not an optional nicety.

Style-wise, the whole suite was converted to an **"executive style"**:
bullets and tables over prose paragraphs, brief inline code comments
following code-writing best practice, forward-looking "**Answers:**" framing
in markdown instead of "**Expect:**" framing that states a numeric outcome
before the code that produces it has run. As of the most recent round, the
convention within the eyeball-preview tables was also refined: **no
`tabulate`, plain pandas default display** (via `.to_string()`), because it
renders better in GitHub's notebook viewer than a hand-formatted ASCII grid.

---

## 2. The Peaks2Tails Course — Condensed Synthesis

*(Full detail — all 16 sections, every worked example, the complete
glossary, and the file-by-file source map — lives in
`docs/Peaks2Tails_Knowledge_Base.md`. This section is the load-bearing
synthesis: enough to work from without opening that file, but the KB file is
authoritative when the two ever seem to disagree.)*

### 2.1 Course structure

The material follows an "Integrated Credit Risk Modelling in Banks"
curriculum:

| Module | Topic |
|---|---|
| 1 | Scorecard Building — PD via logistic regression, roll-rate & vintage analysis, scaling PD to scores, cutoff selection |
| 2 | TTC PD to Worst Case Default Rates |
| 3 | LGD Modelling, RWA & Capital Computation |
| 4 | Macro-economic modelling & scenario analysis |
| 5 | ECL Computation under IFRS 9 |
| 6 | Capital Planning & Stress Testing under ICAAP |
| 7 | RAROC computation |
| 8 | Special modelling situations (Low Default Portfolios, reject inference, behavioral variates) |
| 9 | Data designs and model designs |
| 10 | Final quiz and Excel case studies |

Two Excel workbooks (`1.Raw Data..xlsm`, plus `2.ST_Bucket0.xlsm` /
`5.ST_Bucket3.xlsm`) hold the underlying case-study data referenced
throughout the decks. A meaningful fraction of the source material is
handwritten notes or diagram-heavy slides that only became machine-readable
after a second, OCR/vision-based extraction pass — that pass is fully merged
into the KB file's topic sections already.

### 2.2 Foundational framing

Building a credit model is structurally the same problem as any other binary
classification task (e.g., predicting employee attrition): take historical
cases, their known attributes, and the outcome (defaulted / not), clean it,
fit a classifier. What makes credit risk modeling its own discipline is the
regulatory and definitional scaffolding layered on top — "what counts as
default," "how long is the performance window," "which population is even
eligible" — none of which is generic data-science knowledge.

**Segmentation is a prerequisite, not an afterthought.** A single model
across an entire loan book doesn't work; loans get segmented into
homogeneous pools first, each with its own scorecard.

- **Segmentation levels:** essential, business-driven, data/statistical.
- **Validity pre-requisites for a segment:** default rates differ
  meaningfully across segments; each segment has a material number of
  loans/bads; a segment's default rate has low correlation with the overall
  portfolio's.
- **Segmentation checklist:** heterogeneity, discriminatory power, rank
  ordering, concentration, stability.
- **How to judge whether segmentation actually helped:** the AUC of a
  segment *within* the segmented model should exceed that segment's AUC
  *inside* an unsegmented model; the weighted-average AUC of the segmented
  approach should beat the unsegmented model's AUC; for the same accept
  rate, the segmented approach should produce a lower bad rate.
- **Why decision trees are often used to *find* segments**, even though
  logistic regression can technically handle multiple segments directly:
  trees capture non-linear interactions, are highly interpretable (important
  for regulatory explainability), naturally split heterogeneous populations
  into more homogeneous sub-groups, and double as a variable-selection step
  before a regression is fit within each leaf.

### 2.3 Data design & preparation (its own discipline, not a preliminary step)

**Six pillars of data design:** data conceptualisation, data definitions,
snapshot data creation, data visualisation, data transformation, data
governance.

**Data definitions differ by model purpose** — one of the most-reused
reference tables in the whole course:

| Model | Default/data definition | Performance window |
|---|---|---|
| Scorecards | Roll-rate analysis | Vintage analysis |
| Basel PD | 90 DPD | 1 year |
| IFRS 9 PD | Roll-rate or 90 DPD | Lifetime, quarterly term structure (1-year performance window) |
| Stress Testing PD | 30 DPD (rebuttable) | 9- or 13-quarter forecast, quarterly term structure |
| LGD | Parameter stressed | Crystallisation / cooling-off period |
| CCF (Basel) | — | 1 year |
| CCF (IFRS) | — | Lifetime, quarterly term structure |

**Snapshot design by model:**
- PD — non-defaulted at snapshot; defaulted-or-not tracked in the
  performance window.
- LGD (defaulted accounts) — defaulted at snapshot, recoveries tracked
  post-default.
- LGD (non-defaulted accounts) — non-defaulted at snapshot, defaults +
  recoveries tracked in performance.
- EAD (Basel) — non-defaulted at snapshot, defaulted in performance.
- EAD (IFRS) — non-defaulted at snapshot, defaulted-or-not in performance.

**Data transformation by model type:**

| Model | Transform X | Transform Y |
|---|---|---|
| Scorecard — logistic regression | Weight of Evidence (WoE) or splines | Default status |
| Scorecard — decision tree | Raw X | Default status |
| Macro-economic model | Growth rates, lags | Default rate, log-odds, Vasicek Z |

**Cross-sectional vs. panel; overlapping vs. non-overlapping samples:**
- Cross-sectional = one borrower, one record. Panel = one borrower, multiple
  time-stamped records.
- Overlapping samples: more data points, more timely, allows frequent model
  refresh — but introduces autocorrelation (overstates apparent model
  performance), can reduce stability, and may fail regulatory independence
  requirements.
- Non-overlapping samples: temporal independence, lower overfitting risk,
  cleaner attribution of performance change — but fewer data points, slower
  to reflect recent trends, less frequent updates.
- **Snapshot math:** minimum observations for one snapshot = Observation
  Window (OW) + Performance Window (PW) + 1 (for goods); for bads, OW +
  months-per-bad-definition + 1. Extra snapshots = (Total observations −
  (OW+PW+1)) ÷ snapshot frequency, rounded down. For non-overlapping
  snapshots, N snapshots require N × (OW+PW+1) observations.
- **Origination/snapshot period selection rules:** represent the *future*
  loan book, not an anomalous period; needs enough defaults (rule of thumb:
  ~200 bads); can span a point-in-time window or a full economic cycle;
  cross-sectional or panel, monthly or quarterly.
- **Exclusion/waterfall analysis:** split into "Observation exclusions"
  (wrong product category, missing bureau hit — out of scope by definition)
  and "Performance exclusions" (thin file, inactive, fraud, deceased, closed
  within the performance window — would bias the performance definition). A
  worked course example: 129,811 total population → 114,033 excluded
  (87.85%) → 15,778 final candidates (12.15%).

### 2.4 PD modeling — scorecards

**Roll-rate and vintage analysis (defining "default" and the performance
window):**
- Delinquency buckets: 0 → 30 → 60 → 90 → 120 DPD.
- **Roll-rate analysis** answers "which DPD bucket should count as default?"
  — track loans bucket-by-bucket over time, convert to percentages, and
  identify percent rolling forward (worse), percent rolling backward
  (curing), percent staying put. The bucket with the highest roll-forward
  rate (lowest cure chance) is treated as the defaulting bucket — analogized
  in the course to "stage-4 cancer has the lowest chance of cure."
- **Vintage analysis** answers "how long should the performance window be?"
  — plot cumulative default rate against months-on-book; the point at which
  ~75% of eventual defaulters have already gone bad is the practical
  performance window. Too short underestimates the true default rate; too
  long wastes usable recent data.

**Logistic regression mechanics:**
- Y (default: 0/1) is categorical, so linear regression is inappropriate;
  logistic regression models log-odds directly:
  `log(π/(1−π)) = β1X1 + β2X2 + ...`
- Estimated by Maximum Likelihood (MLE), iteratively.
- **CATEGORICAL mnemonic** structures the whole validation workflow:
  **C**oefficient estimation via MLE, **A**ssumption checking
  (multicollinearity via VIF), **T**esting individual coefficients (Wald
  test) and overall model fit, and further steps covered in the KB's §4 in
  full.

**Segmentation-into-pools (Basel-flavored framing):** default per Basel is
90 DPD, 1-year performance window, "once bad, always bad" (no cure
recognized). Non-regulatory PD uses roll-rate/vintage-derived definitions
instead. Segmentation dimensions applied in order: product type → months on
book (seasoned vs. not) → new-to-bank vs. existing → thin-file vs.
thick-file → clean vs. dirty delinquency history.

### 2.5 Model validation & discriminatory power

- **Validating a Master Rating Scale (MRS):** assign a grade per borrower,
  then check discriminatory power (needs good/bad counts per grade), rank
  ordering, concentration (no single grade >~15% of exposure), heterogeneity
  (t-test confirming adjacent bins are statistically distinct), and stability
  over time (acknowledged as something that can't be perfectly optimized,
  since sub-portfolio composition shifts with the business cycle — requires
  an educated guess and long-term commitment to the chosen scale).
- **Document structure** used as an internal governance checklist:
  Introduction → Purpose & Scope → Overview of Model Risk Management → Model
  Development, Implementation & Use → Model Validation → Governance,
  Policies & Controls → Conclusion.
- **PIT vs. TTC vs. Hybrid PD models:** Point-in-Time models react to
  current conditions but swing capital requirements sharply across the
  cycle (destabilizing at scale — a trillion-pound mortgage book is the
  course's example). Hybrid models (recommended by the UK's PRA for mortgage
  portfolios) blend PIT and TTC; the PRA formalizes "cyclicality" as a metric
  of how PIT-like a model actually is.
- **Rank-ordering error:** occurs when calibrated-PD order disagrees with
  modelled-PD order for a pair of obligors ("discordant pairs"); quantified
  as the sum of absolute PD differences across discordant pairs, normalized
  to portfolio scale.

### 2.6 LGD, EAD & CCF modeling

- **EAD / CCF:** `EAD = Amount Outstanding + CCF × Headroom` (undrawn
  "open to buy"). The course's worked example compares an LDP (low-default
  portfolio) approach against an RP approach segmented by weeks-in-employment
  bands, with LDP/RP rates differing meaningfully band to band (e.g.
  7%/9% at the low end up to 32%/23% at the high end).
- **Collective / PD×LGD×EAD approach:** staging + parameters assessed on a
  collective basis by grouping exposures with shared risk characteristics —
  suited to retail/SME; typically implemented as 2-state models (Default vs.
  Non-default) using an account-level PIT scorecard on borrower attributes +
  macro variables.

### 2.7 IFRS 9 / ECL / CECL

Full detail in KB §9; the core framing: staging (Stage 1/2/3) drives whether
ECL is computed over a 12-month or lifetime horizon, PD/LGD/EAD parameters
under IFRS 9 differ from their Basel counterparts specifically in horizon and
point-in-time-ness (see §2.3's table above), and collective assessment
groups exposures by shared risk characteristics rather than modeling every
loan individually.

### 2.8 Statistical & ML toolkit used throughout

Six branches of statistics mapped to their ML analogue: descriptive
statistics → exploratory data analysis; inferential statistics → sampling
theory; predictive analytics → supervised learning; forecasting →
time-series modeling; cluster analytics → unsupervised learning;
prescriptive analytics → reinforcement learning. Example applications per
branch include: sales as a function of ad spend (supervised regression);
default rate as a function of macro variables (supervised); credit limit as
a function of past payment behavior (supervised); customer default-or-not,
cure-or-not (supervised classification); geographical/portfolio segmentation
(unsupervised clustering); algo trading (reinforcement learning).

### 2.9 Data typing and the DPMENTOS framework

This is the material most directly relevant to Phase 0's EDA work, and the
course's fullest treatment of data preparation (reconstructed via OCR of
20 pages of handwritten notes — see KB §13 for the complete framework).

- **Structured vs. unstructured data.** Structured splits further into
  **Time Series** (one unit over time), **Cross-Sectional** (many units, one
  point in time), and **Panel** (many units, many time points).
- **Variable types:** **Numerical** — Discrete (countable, e.g. loan age) vs.
  Continuous (e.g. loan amount); **Categorical** — 2-category (e.g.
  Default/No-Default) or Multiple-category, split into **Nominal** (no
  order — home-ownership Rent/Mortgaged/Own/None) vs. **Ordinal** (has
  order — Income Category Low/Medium/High, or Loan Grade A/B/C/D).
- **Worked field-type example** (directly echoed in this project's own
  numeric-vs-categorical work): Employment length → numerical discrete; Loan
  amount → numerical continuous; Home ownership → categorical nominal;
  Income category → categorical ordinal; Loan term → numerical discrete;
  Income amount → numerical continuous; Loan purpose → categorical nominal;
  Loan grade → categorical ordinal; Loan status (good/bad) → categorical,
  2-category; Loan interest rate → numerical continuous.
- **Supervised learning framing used throughout:** `Loan Status =
  fn(Employment length, Income, Home Ownership, Loan amount, Loan term, Loan
  purpose)` — Y is the response/target/dependent variable, the X's are
  features/independent/explanatory variables. If Y is available, it's
  supervised learning: Classification (Y is a class, e.g. good/bad) vs.
  Regression (Y is numeric, e.g. interest rate). The pipelines for the two
  are ~75% similar; classification has more downstream steps, but data
  preparation is a shared first step for both.
- **Missingness treatment, including the Missing Indicator Approach**
  (directly relevant to this project's `emp_length_was_missing` decision in
  notebook 2 — see §5 below): create a dummy variable flagging that a value
  was missing, then impute the underlying field. The course's worked example
  uses Job Status (Student/Businessman/Salaried) and Years of Employment
  (N/A for students and businessmen, real for salaried people) — because Job
  Status explains the missingness pattern in Years of Employment, this is
  **MAR** (Missing At Random), not MCAR or MNAR, and the correct treatment
  is: create (k−1) dummy variables for the k-class explanatory field, then
  impute the dependent field's missing values with 0 for the classes where
  the flags already carry the information.
- **Outlier engineering/treatment** — two methods: **Trimming** (exclude
  outliers outright) and **Winsorizing/Capping** (cap and floor to a
  non-outlier value). Sigma-based capping ("Six Sigma," mean ± 3σ) is
  explicitly called out as a **bad technique in industry**, because σ itself
  is distorted by the very outliers being treated — circular. **Box-plot-based
  capping** (preferred): Upper Boundary = Q3 + 1.5×IQR, Lower Boundary = Q1 −
  1.5×IQR. A QQ plot is another detection technique; a common convention
  caps at the 99th percentile and floors at the 1st. Decision rule: if
  outliers are genuine (not measurement error) — don't trim; keep them,
  Winsorize only if the model needs a no-outlier assumption (e.g. linear
  regression). If outliers are noise (measurement/typing errors) — trim if
  enough data remains, or Winsorize if too little data can be spared. This
  is the exact reasoning this project's notebook 3 (`02_data_quality_
  integrity.ipynb`) already applies in its Cell 8 outlier-treatment decision
  table (IQR + z-score cross-check, naturally-bounded fields left alone,
  log-handled fields left alone, genuinely unbounded fields capped at
  1st/99th percentile) — see §5.3 below.

### 2.10 Survival analysis (time-to-default modeling) — condensed

Positioned in the course as an alternative to point-in-time PD models:
instead of predicting whether a borrower defaults within a fixed window,
survival analysis predicts **when** default occurs, and explicitly handles
**censoring** (loans still performing, or exited for another reason like
prepayment, at the time of analysis).

- **Core objects:** `T` = time to default. `f(t)` = density. `F(t) = P(T<t)`
  = cumulative probability of default. `S(t) = P(T>t) = 1 − F(t)` =
  **survival function**. **Hazard function**
  `h(t) = f(t)/S(t) = −(1/S(t))·dS(t)/dt`, and `S(t) = exp{−∫₀ᵗ h(u)du}`.
  Constant hazard implies an Exponential distribution for `T`; a hazard that
  varies with time needs a piecewise or Weibull form instead.
- **Kaplan-Meier (KM):** the non-parametric workhorse. In discrete time,
  conditional hazard = conditional probability = (defaults in the period) /
  (survivors at the start of the period). Cumulative survival
  `S(t) = Π(1 − hⱼ)` over all periods up to `t`. Right-censoring (a loan that
  exits the study for any non-default reason) is handled by removing it from
  the risk set from that point on, without counting it as a default.
- **Cox Proportional Hazard model:** `h(t,x) = h₀(t) × g(x)`, separating a
  time-dependent baseline hazard from a covariate-driven scaling factor
  (typically `g(x) = e^(βx)`). Its practical advantage: β can be estimated
  by maximizing a **partial likelihood** without ever needing to know the
  baseline hazard `h₀(t)` — in credit risk practice, the baseline is
  typically estimated via KM and β via Cox regression, then combined into
  `S(t,x)` to derive a covariate-adjusted PD.
- **Accelerated Failure Time (AFT) models:** instead of modeling hazard,
  AFT models regress a transform of `T` directly against covariates (e.g.
  `ln(t) = α + β·x + e`, with `e` typically Normal, Logistic, or an Extreme
  Value distribution depending on the assumed distribution of `T`).

This hasn't yet been applied anywhere in Phase 0 (it's a modeling-phase
technique, not an EDA one), but it's directly relevant background for
`02_eda/06_temporal_sequential_spatial.ipynb` and later phases, since
vintage curves and time-to-default framing share the same underlying
concepts.

### 2.11 Macro-economic / time-series modeling — condensed

Underpins the "term structure of PD," stress-testing PD, and scenario-based
ECL work the course covers in later modules.

- **Stationarity is the load-bearing concept.** A series with a
  **deterministic trend** (`Yt = b0 + b1·t + et`) can be fixed by detrending
  or differencing; a series with a **stochastic trend**
  (`Yt = b0 + b1·Yt-1 + et` with `b1=1`, a unit root / random walk) can only
  be fixed by differencing — detrending doesn't work on it. The
  **(Augmented) Dickey-Fuller test** is the standard way to test for a unit
  root, since an ordinary t-test on `b1=1` is invalid (the test statistic
  doesn't follow a t-distribution when the null itself implies
  non-stationarity).
- **ACF/PACF identify AR vs. MA order:** for an AR process, PACF cuts off
  sharply while ACF decays gradually; for MA, it's the reverse. Neither
  cuts off cleanly for a mixed ARMA process, so ARMA order has to be
  identified by likelihood-based model selection (AIC/BIC) rather than
  graphically.
- **AIC vs. BIC:** `AIC = T·ln(σ̂²) + 2K`, `BIC = T·ln(σ̂²) + K·ln(T)`. BIC
  penalizes additional parameters more heavily (especially once `T>8`) and
  is asymptotically consistent (picks the true model as `T→∞`); AIC is more
  permissive and can retain irrelevant variables that BIC would drop.
- **VAR (Vector Autoregressive models)** extend this to multiple
  interdependent series at once (e.g. modeling two correlated macro
  variables jointly rather than as separate univariate models), using
  **cross-correlation matrices** to detect lead-lag relationships between
  series.
- **Cointegration & VECM:** two individually non-stationary (`I(1)`) series
  can still have a *stationary* linear combination — meaning they share a
  common long-run stochastic trend and don't drift apart indefinitely, even
  though each one wanders on its own. The **Vector Error Correction Model**
  captures this by adding an error-correction term (the lagged deviation
  from the long-run relationship) to a VAR-in-differences, with a
  "speed-of-adjustment" coefficient controlling how fast the series pulls
  back toward equilibrium after a shock. The **Johansen test** is the
  standard sequential procedure for determining how many cointegrating
  relationships exist among a set of series. This matters for credit risk
  specifically because macro scenario variables (unemployment, GDP growth,
  house prices, etc.) used to drive stress-testing PD are themselves
  time series with exactly these properties, and a spurious (non-cointegrated)
  regression between a macro variable and a default rate can produce a
  misleadingly high R² with no real relationship behind it.

Full derivations (Yule-Walker equations, the Cholesky-style structural-form
decomposition of a VAR, the complete Johansen-test decision tree, and every
worked numeric example) are in KB §12 — this section is deliberately the
condensed version, since the math is dense enough that duplicating it in
full here would just be a second copy of the same file.

### 2.12 Full acronym glossary

| Acronym | Meaning |
|---|---|
| PD / LGD / EAD | Probability of Default / Loss Given Default / Exposure at Default |
| CCF | Credit Conversion Factor |
| TTC / PIT | Through-the-Cycle / Point-in-Time (rating philosophies) |
| WoE / IV | Weight of Evidence / Information Value |
| KS | Kolmogorov–Smirnov statistic (discriminatory power) |
| AUC / Gini | Area Under Curve / Gini coefficient (discriminatory power) |
| MoC | Margin of Conservatism |
| RWA / CAR | Risk-Weighted Assets / Capital Adequacy Ratio |
| CET1 / AT1 / T2 | Common Equity Tier 1 / Additional Tier 1 / Tier 2 capital |
| IRB | Internal Ratings-Based approach (vs. Standardised approach) |
| SICR | Significant Increase in Credit Risk (IFRS 9 staging trigger) |
| ECL / ALLL | Expected Credit Loss / Allowance for Loan and Lease Losses |
| CECL | Current Expected Credit Loss (US GAAP) |
| DPD | Days Past Due |
| OW / PW | Observation Window / Performance Window |
| MOB | Months on Book |
| RAROC | Risk-Adjusted Return on Capital |
| ICAAP / ILAAP | Internal Capital / Liquidity Adequacy Assessment Process |
| LDP | Low Default Portfolio |
| SR 11-7 | US Fed/OCC Supervisory Guidance on Model Risk Management |
| SS1/23 | PRA (UK) Model Risk Management Principles |
| MRM | Model Risk Management |
| LoD1/2/3 | First/Second/Third Line of Defense |
| MRS | Master Rating Scale |
| WCDR | Worst Case Default Rate |
| DLGD / ELGD | Downturn LGD / Expected (average) LGD |
| MENTOS / DPMENTOS | Mnemonic for the data-preparation pipeline: Data analysis, Partitioning, Missing-value imputation, Encoding, Normal transformation, Outlier treatment, Scaling |
| MCAR / MAR / MNAR | Missing Completely At Random / Missing At Random / Missing Not At Random |
| KM | Kaplan-Meier (survival estimator) |
| PH / AFT | Proportional Hazard model / Accelerated Failure Time model |
| ACF / PACF | Autocorrelation Function / Partial Autocorrelation Function |
| AR / MA / ARMA / ARIMA / SARIMA | AutoRegressive / Moving Average / ARMA / Integrated ARMA / Seasonal ARIMA |
| ADF | Augmented Dickey-Fuller (unit-root test) |
| AIC / BIC | Akaike / Bayesian Information Criterion |
| VAR / VECM | Vector Autoregressive model / Vector Error Correction Model |
| CCM | Cross-Correlation Matrix (multivariate time series) |
| LDA / SVM / KNN | Linear Discriminant Analysis / Support Vector Machine / K-Nearest Neighbours |
| ROC / TPR / FPR | Receiver Operating Characteristic / True & False Positive Rate |

### 2.13 Source material and the case-study workbooks

The KB was compiled from 60 files total: 57 PDFs (slide decks, handwritten
notes, regulatory documents) plus 3 Excel case-study workbooks
(`1.Raw Data..xlsm`, `2.ST_Bucket0.xlsm`, `5.ST_Bucket3.xlsm`) containing
live, formula-driven worked examples — the scorecard build, roll-rate/
vintage calculations, and calibration examples referenced throughout the
slides. All 57 PDFs were processed in two passes: native text extraction,
then a second OCR/vision-based pass specifically for the 29 image- and
handwriting-heavy files the first pass couldn't read. The 3 Excel workbooks
remain unprocessed as flat text by design — their value is in live formulas
and pivot structures, best explored directly in Excel rather than as a
static transcription.

---

## 3. What's Actually Being Built — Technical Architecture

### 3.1 Repository layout

```
credit-risk-portfolio/                       (GitHub: deveshusg/credit-risk-portfolio)
├── CLAUDE.md                                 -- short auto-loaded context for Claude Code
├── docs/
│   ├── Peaks2Tails_Knowledge_Base.md         -- full course knowledge base
│   └── PROJECT_MASTER_CONTEXT.md             -- this document
└── phase0_data_platform/
    └── 01_lendingclub/
        ├── data/
        │   ├── 01_raw/                       -- accepted_2007_to_2018Q4.csv.gz (public LC data)
        │   ├── 02_interim/                   -- lendingclub.duckdb (built by build_lendingclub.py)
        │   ├── 03_processed/                 -- lendingclub_model_ready.parquet
        │   └── 04_assets/
        │       ├── tables/                   -- every notebook's CSV outputs, per-notebook-prefixed
        │       └── plots/
        └── notebooks/
            ├── _shared/
            │   └── nb_setup.py               -- connect() / create_fresh() helper, used by every notebook
            ├── 01_ingestion/
            │   └── 01_raw_to_interim.ipynb
            ├── 02_eda/
            │   ├── 01_data_understanding_structural_profiling.ipynb
            │   ├── 02_data_quality_integrity.ipynb
            │   ├── 03_univariate_distributional_visual.ipynb
            │   ├── 04_bivariate_multivariate_relationships.ipynb
            │   ├── 05_pattern_anomaly_cluster_latent_structure.ipynb
            │   ├── 06_temporal_sequential_spatial.ipynb
            │   ├── 07_target_outcome_objective.ipynb
            │   ├── 08_statistical_validation_inference_robustness.ipynb
            │   ├── 09_transformation_feature_diagnostics_prep.ipynb
            │   ├── 10_dataset_comparison_population_drift.ipynb
            │   ├── 11_sampling_representativeness_population.ipynb
            │   ├── 12_text_categorical_highcardinality_multimedia.ipynb
            │   ├── 13_causal_quasicausal_mechanism.ipynb
            │   └── 14_eda_governance_synthesis_reporting.ipynb
            └── 03_data_cleaning/
                └── 01_cleaning_and_feature_prep.ipynb
```

All 16 notebooks already exist and were built as a complete first pass
(commit `2279159`, "MVP before review v2," plus two earlier MVP commits) —
what this conversation has been doing is a careful, one-at-a-time **manual
review and rework pass** on top of that first pass, not building from
scratch.

### 3.2 The data pipeline

- **Source:** Lending Club accepted loans, 2007–2018 (`accepted_2007_to_
  2018Q4.csv.gz`), publicly available.
- **Ingestion (`01_ingestion/01_raw_to_interim.ipynb`):** reads the raw CSV
  as **all-text** (`all_varchar=True` in DuckDB's `read_csv`) — deliberately,
  so nothing gets silently mis-cast or corrupted on load. Materializes into a
  fresh interim DuckDB file via `create_fresh()`.
- **Staged tables inside the interim DuckDB file**, built by a
  `build_lendingclub.py` script (referenced by the notebooks, confirmed by
  row-count checks in notebook 2):
  - `raw_mat` — all rows, all 151/152 raw columns, materialized as-is.
    2,260,701 rows.
  - `matured` — finished loans only. 1,348,099 rows.
  - `windowed` — matured loans further restricted to the 2013–2017
    origination vintage. 1,195,879 rows. **This is the population every EDA
    notebook actually profiles.**
- **Target variable:** `is_bad` — computed at some point in the pipeline
  (before the EDA suite; not something EDA notebooks derive) from
  `loan_status`. It is explicitly *not* a feature and should never be
  flagged as a miscategorized column when it shows up in a numeric-column
  scan (this exact confusion came up and was resolved in notebook 2 — see
  §5.2).
- **Column count:** 151 raw columns confirmed on `raw_mat` in notebook 1;
  elsewhere referred to as 152 (the `is_bad` target column brings the
  `windowed`/working count to 152). Both figures are correct depending on
  whether the target column is counted.

### 3.3 The shared connection helper — `notebooks/_shared/nb_setup.py`

Every single notebook, without exception, must go through this file rather
than opening its own DuckDB connection:

- `connect()` — **read-only**. Opens the existing interim DuckDB file,
  creates the `data/04_assets/tables/` and `data/04_assets/plots/` folders
  if they don't exist, and returns `(con, ASSETS_TABLES, ASSETS_PLOTS)`.
  Used by every EDA and cleaning notebook.
- `create_fresh()` — **ingestion only**. Deletes any existing interim DuckDB
  file and creates a new one. Used exclusively by
  `01_ingestion/01_raw_to_interim.ipynb`. No other notebook should ever call
  this — doing so would silently wipe the interim data every other notebook
  depends on.

### 3.4 Notebook internal conventions

Every notebook follows the same structural pattern (established and refined
over the course of this conversation):

- **Intro markdown cell** — title, status line, "What this notebook covers,"
  "Where this fits" (its place among the 16, and the boundary that EDA
  notebooks never clean/modify data).
- **Cell-map markdown table** — a `| # | What it does |` table listing every
  numbered logical step in the notebook, so a reader can see the whole
  notebook's shape before reading it cell by cell.
- **Per-step pattern, repeated for every logical step:** one markdown cell
  before the code (what/why/how, and an **Answers:** line framing the
  question the code is about to answer — never an **Expect:** line stating
  the numeric outcome in advance) → one code cell (short `#` inline comments
  describing what the block does, not what it doesn't do; writes any derived
  table to `ASSETS_TABLES` as CSV) → one markdown cell after the code
  ("**Result**" — bullets/tables summarizing the actual printed output, plus
  a "**Next:**" line pointing to what comes next).
- **Executive style throughout** — bullets and tables, minimal prose,
  short/direct language. This was an explicit, global, retroactive directive
  applied across the whole suite, not just new material.
- **No claim without a printed number next to it** — this is Rule 1 (§4.1)
  applied at the sentence level: if a markdown cell states a fact or figure,
  the adjacent code cell's output must contain that number.

---

## 4. The Three Standing Rules — Full Detail

These were established early in the project and have not changed. Every
notebook, past and future, is expected to comply with all three.

### 4.1 Rule 1 — Evidence-in-code

Every markdown factual or numeric claim must be demonstrated by actual code
and printed output in the same notebook — never from outside knowledge, an
inferred fact, or something "everyone knows" about the Lending Club dataset.
If a markdown cell says "80 of 152 columns are fully populated," there must
be a code cell, in that same notebook, whose printed output shows that
number being computed. This rule is the reason every notebook writes so much
of its intermediate output to CSV in `ASSETS_TABLES` — it's not just for
later phases, it's the audit trail proving the claim.

Practical corollary that came up repeatedly: forward-looking markdown must
be phrased as a question the code will answer ("**Answers:** does missingness
on this column correlate with the target?"), never as a stated expectation
with a number in it ("**Expect:** ~7% gap"). The latter reads as though the
result is already known before the reader sees the code run, which
undermines the entire evidence-in-code premise. This was flagged explicitly
on notebook 1 ("expectations should not have numbers or seem like the
results are known before running the code cell") and has since been
identified as a residual problem in notebook 3, which still uses "Expect:"
framing with specific presupposed numbers in five of its markdown cells (see
§6 — this is an open item, not yet fixed).

### 4.2 Rule 2 — Shared connection helper only

Covered in full in §3.3. No notebook may open its own ad-hoc `duckdb.
connect(...)` call. This keeps every notebook pointed at the same interim
file, guarantees read-only safety for every notebook except ingestion, and
means the asset folders are created consistently.

### 4.3 Rule 3 — No premature column narrowing outside `03_data_cleaning`

EDA notebooks (02 through 14) must never narrow column scope **based on an
earlier notebook's test result** — only `03_data_cleaning` may actually drop
columns, and only with an explicit, written justification for each drop.

**Important nuance, discovered while reviewing notebook 3:** this rule
governs *data-driven* narrowing (dropping a column because an earlier
notebook's statistical test said to), not the existence of a **fixed
candidate shortlist chosen by domain judgment before any diagnostic
notebook ran**. Notebook 3's Cell 2 markdown makes this distinction
explicit: starting from notebook 2 (`02_data_quality_integrity.ipynb`)
onward through notebook 14, every EDA notebook works from the same
fixed ~30-column candidate shortlist (see §6.2 for the exact list and its
composition) — chosen by domain judgment, not computed from any prior
notebook's output — while notebook 1
(`01_data_understanding_structural_profiling.ipynb`) still profiles the
complete, unnarrowed 151/152-column raw schema. The final, audited,
data-driven narrowing happens only in `03_data_cleaning/01_cleaning_and_
feature_prep.ipynb`, which is explicitly cross-referenced from notebook 3
(e.g. "`avg_cur_bal` was on an earlier version of this list and was dropped
after notebook 09's VIF check found it redundant with `tot_cur_bal`").

This was flagged to the user as a structural decision worth seeing
explicitly (in the notebook-3 review round) rather than being silently
accepted, precisely because it's the kind of design choice Rule 3 exists to
guard against sliding through unreviewed. **As of the most recent message in
this conversation, the user has not yet given an explicit verdict on whether
to keep this fixed-shortlist design as-is** — this is an open item (§8).

### 4.4 The retroactive fourth principle — explain the variable, not just profile it

Stated by the user in the context of notebook 2's hardship/settlement
columns, then generalized explicitly as a standing, project-wide rule: *"in
cell 10 markdown tell about the group columns with high missingness like
hardship - what they mean what kind of variables they are does missingness
is signal, should they be used in modelling, do they need further analysis
if so which and when, how they would be treated if they are to be used and
other details about them. - this is the purpose of eda excercise isn't it?
... this should be done for all analysis in all notebooks wherever
required."*

In practice, this means: whenever a notebook surfaces a notable pattern
(especially a group of high-missingness columns, but the principle isn't
limited to missingness), the markdown response can't just report the number
— it has to interpret it the way a domain expert building toward a
production model would. Notebook 2's hardship/settlement analysis (§5.4
below) and notebook 3's `emp_length` missingness-is-signal finding (§6.1) are
the two places this has actually been applied so far; it needs to be kept in
mind for every notebook still ahead.

---

## 5. Notebook 1 — Ingestion (`01_ingestion/01_raw_to_interim.ipynb`)

**Status:** rewritten in executive style, evidence-first framing. 21 cells.
Re-executed with zero errors. Committed on `main` at `a289ba4` ("Rewrite
ingestion notebook in executive style, evidence-first framing"). **Not yet
pushed to GitHub** (push must always be done by the user — see §9).

### 5.1 What changed in the rewrite

- Added a brief "About the dataset" intro section (public-availability
  context) and a "Files in `data/01_raw/`" table, per the user's request
  that the ingestion notebook specifically carry this context (other
  notebooks don't need to repeat it).
- Converted all "Expect:"-with-numbers framing to "Answers:" framing.
- Converted narrative prose into bullets/tables per the executive-style
  directive.
- Added brief `#` inline code comments describing each code block.

### 5.2 Key code — connect and materialize (Cell 2)

```python
import sys, os, duckdb
sys.path.insert(0, os.path.abspath("../_shared"))
from nb_setup import create_fresh

RAW_FILE = "../../data/01_raw/accepted_2007_to_2018Q4.csv.gz"
con, ASSETS_TABLES, ASSETS_PLOTS = create_fresh()  # fresh interim DuckDB file, deletes any old one

# read raw CSV as all-text (no type inference) -- avoids silently dropping/
# corrupting messy numeric columns
con.sql(f"""CREATE OR REPLACE VIEW raw AS SELECT * FROM read_csv(
    '{RAW_FILE}', header=True, delim=',', ignore_errors=True, all_varchar=True
)""")
con.sql("CREATE OR REPLACE TABLE raw_mat AS SELECT * FROM raw")
n_raw = con.sql("SELECT count(*) FROM raw_mat").fetchone()[0]
print(f"raw file: {n_raw:,} rows")
```

### 5.3 Verified outputs / evidence produced

CSV assets committed alongside this notebook: `ing01_by_year.csv`,
`ing01_status_breakdown.csv`, `ing01_null_status_rows.csv`.

---

## 6. Notebook 2 — Data Understanding & Structural Profiling
### (`02_eda/01_data_understanding_structural_profiling.ipynb`)

**Status:** the most heavily worked notebook in the project so far. Current
state on disk (device) is a 23-cell version, **committed on the new
`devesh_development` branch** at `d0045be` (see §9.2 for the branch story).
An earlier 20-cell version was committed on `main` at `e727a2e`.

### 6.1 Evolution, round by round

1. **v1 (11 cells):** initial executive-style pass, "Answers:" framing.
2. **v2 (20 cells), committed `e727a2e` on `main`:** added Cell 3 (eyeball
   full column lists — print full numeric/categorical lists), Cell 4 (flag
   ambiguous columns, seeded via `AMBIGUOUS_OVERRIDES = [("id", "..."),
   ("policy_code", "...")]`), removed the phrase "~27 columns eventually
   retained for modeling" (and checked for similar phrasing elsewhere — this
   phrase presupposes a modeling outcome EDA shouldn't know yet), printed
   the full 152-row null% listing ordered descending (not just the top 12),
   and added a rich hardship/settlement signal-check narrative (the
   fourth-principle application described in §4.4), backed by real,
   verified DuckDB evidence:

   ```python
   hardship_signal = con.sql("""
       SELECT (hardship_type IS NULL) AS hardship_type_is_null,
              count(*) AS n, round(avg(is_bad), 3) AS bad_rate
       FROM windowed GROUP BY 1 ORDER BY 1
   """).df()
   settlement_signal = con.sql("""
       SELECT debt_settlement_flag, count(*) AS n, round(avg(is_bad), 3) AS bad_rate
       FROM windowed GROUP BY 1 ORDER BY 1
   """).df()
   hardship_flag_vals = con.sql("SELECT DISTINCT hardship_flag FROM windowed").df()
   ```

   Verified results: `hardship_type` not-null → n=5,726, bad_rate=70.5%, vs.
   null → n=1,190,153, bad_rate=20.3%. `debt_settlement_flag` = Y → n=32,337,
   bad_rate=100.0%, vs. N → n=1,163,542, bad_rate=18.3%. `hardship_flag` is
   always `'N'` in the `windowed` population.

   This surfaced a genuine data-understanding insight, not just a mechanical
   number: `hardship_flag` is misleadingly always `N` for matured loans in
   this population — it reflects "currently in an active hardship plan," a
   point-in-time indicator that has decayed to a constant for loans that
   have already finished, not historical hardship status. `hardship_type IS
   NULL` is the field that actually reflects whether a loan ever had a
   hardship event at all. Separately, `debt_settlement_flag = Y` sitting at
   essentially 100% bad rate flags it as close to definitionally tied to the
   "bad" outcome — worth treating carefully in feature design later,
   potential leakage territory.

   After this cell was built, the user gave the feedback "again executive
   style narative" — the resulting narrative had drifted back into
   paragraphs-under-bold-headers prose, and was converted into bullets and
   tables to match the rest of the suite.

   The user then said "good. update the notebook" for this version, which
   was synced to disk and committed as `e727a2e`.

3. **v3 (23 cells, current, on `devesh_development` at `d0045be`):**
   a substantial redesign of the "eyeball columns" step, described in full
   in §6.2–§6.4 below.

### 6.2 The "eyeball columns" redesign — full specification

The user's request, given in detail before any changes were made (and
explicitly asked to be shown a plan first, which was done): two DataFrames,
one for numeric columns and one for categorical columns. Column 1 = the
column name. Columns 2–5 = four values of that column chosen at random (no
seed — different sample each run). Column 6 = `is_ambiguous`, defaulting to
"No". All rows (all 114 numeric, all 38 categorical) and all 6 columns must
be fully visible in the output — no truncation. A separate, later cell
should let the user flag a column ambiguous by giving its **row number**
(not by retyping the full column name), plus a comment, so the flag can be
picked up by the cleaning stage.

Refinements added over several follow-up rounds:
- **Unique random sample** — the four sampled values per column must be
  distinct from each other (not the same value repeated), achieved by
  sampling from a `DISTINCT` subquery rather than the raw column.
- **Solid-border table look** — the user initially asked for the dataframe
  to visually resemble a markdown table with solid borders, which is what
  originally motivated introducing the `tabulate` library (`tablefmt=
  "grid"`). **This has since been reversed** (see §6.5) — the user's most
  recent instruction was to drop `tabulate` entirely and go back to plain
  pandas default display, because it renders better on GitHub's notebook
  viewer. The `tabulate`-based grid formatting is no longer part of this
  notebook.
- **Column-width discipline** — long free-text fields like `url` and `desc`
  were distorting the shape of the sample-value columns, so a `clip()`
  helper truncates any sampled value to 35 characters (appending `...`) for
  display purposes only — it doesn't affect the underlying data or the
  `n_distinct` computation.
- **`sec_app_earliest_cr_line` should get the `date` domain tag**, same
  treatment as `earliest_cr_line` — a co-borrower credit-history start date,
  raised by the user directly while reviewing the design and incorporated
  into the `DATE_LIKE` list.

### 6.3 The final "eyeball" mechanism — code and design reasoning

**Cell 9 (numeric/categorical eyeball preview), current form:**

```python
# full column lists, one bucket at a time
numeric_cols = sorted(type_df.loc[type_df["inferred_type"] == "numeric", "column"])
categorical_cols = sorted(type_df.loc[type_df["inferred_type"] == "categorical/text", "column"])

def sample_values(col, k=4, width=35):
    # unique (DISTINCT), unseeded -- different sample each run; padded with "" if the
    # column has fewer than k distinct non-null values (itself a useful signal)
    vals = con.sql(f'''
        SELECT val FROM (SELECT DISTINCT "{col}" AS val FROM windowed WHERE "{col}" IS NOT NULL)
        USING SAMPLE {k} ROWS
    ''').df()["val"].tolist()
    vals = vals + [""] * (k - len(vals))
    def clip(v):
        s = str(v)
        return s if len(s) <= width else s[:width - 3] + "..."
    return [clip(v) for v in vals]

def build_preview(col_list):
    records = []
    for c in col_list:
        n_distinct = con.sql(f'SELECT count(DISTINCT "{c}") FROM windowed').fetchone()[0]
        records.append((c, *sample_values(c), n_distinct, "No"))
    return pd.DataFrame(records, columns=["column", "sample_1", "sample_2", "sample_3", "sample_4", "n_distinct", "is_ambiguous"])

numeric_preview_df = build_preview(numeric_cols)
categorical_preview_df = build_preview(categorical_cols)

print(f"numeric columns ({len(numeric_preview_df)}):")
print(numeric_preview_df.to_string())
print()
print(f"categorical columns ({len(categorical_preview_df)}):")
print(categorical_preview_df.to_string())
```

Note: `.to_string()` on a pandas DataFrame does **not** truncate rows or
columns regardless of the `pd.options.display` settings, unlike the default
`print(df)` / notebook auto-render path — this is why no
`pd.set_option("display.max_rows", ...)` call is needed anywhere in this
notebook even though `numeric_preview_df` has 114 rows and the full
null%-profile table (Cell 18) has 152. This matches the pattern already used
in Cell 18's `summ_sorted.to_string(index=False)` before the eyeball cells
were ever touched, so the redesigned cells are actually consistent with a
convention that already existed elsewhere in the same notebook.

**Cell 12 (date/time_period tagging)** layers a `domain_type` column onto
`categorical_preview_df` — `"date"` for `earliest_cr_line`, `issue_d`,
`last_credit_pull_d`, `last_pymnt_d`, `sec_app_earliest_cr_line`;
`"time_period"` for `emp_length`, `term`; `"categorical"` for everything
else — printed as raw sample values first (proving the format), then the
updated table.

**Cell 15 (row-number-based ambiguous flagging):**

```python
# flag ambiguous columns by row number from the tables printed in cell 3:
# (source table, row number, comment)
FLAGGED_ROWS = [
    ("numeric", 25, "loan identifier, not a numeric feature -- exclude from modeling despite passing the cast-rate test"),
    ("numeric", 77, "single-valued category code in this population, not a measured quantity -- treat as categorical"),
]

source_map = {"numeric": numeric_preview_df, "categorical": categorical_preview_df}
overrides = []
for source, row, note in FLAGGED_ROWS:
    col_name = source_map[source].loc[row, "column"]
    source_map[source].loc[row, "is_ambiguous"] = "Yes"
    overrides.append((col_name, note))

overrides_df = pd.DataFrame(overrides, columns=["column", "note"])
overrides_df.to_csv(os.path.join(ASSETS_TABLES, "eda01_ambiguous_overrides.csv"), index=False)
```

The `source` tag on each `FLAGGED_ROWS` entry exists specifically because
the numeric and categorical preview tables each have their own independent
0-based row index — a merged single index across both tables was
considered and rejected as more error-prone, since the row numbers a human
reads off the printed table wouldn't match a merged lookup index without
extra mental translation.

### 6.4 Additive-layering pattern

This is the general design principle behind the whole eyeball/tagging
mechanism, worth restating on its own since it's meant to be reused in later
notebooks:

- `inferred_type` (numeric / categorical, computed once from the
  cast-success-rate test in Cell 2) is **never overwritten**.
- `domain_type` (date / time_period / categorical) and
  `is_ambiguous`/override notes are **separate, additive columns** layered
  on top of the mechanical result — each one backed by its own printed
  evidence in the same cell, never silently replacing what the mechanical
  test found.

This distinguishes "genuinely miscategorized" columns (`id` — an identifier
that happens to cast to `DOUBLE`; `policy_code` — a single-valued code in
this population) from "legitimate low-cardinality numeric columns" (rare-
event counts like `num_tl_30dpd`, `inq_last_6mths`, `acc_now_delinq`, and
hardship-only fields like `deferral_term`/`hardship_length`) — the
distinction is made using real `n_distinct` evidence across all 114 numeric
columns, not cardinality intuition alone. It also explicitly calls out
`is_bad` as the modeling target — not a miscategorized feature — when it
shows up in the numeric-columns scan, to prevent it being mistaken for
something needing a fix.

### 6.5 Most recent change — dropping `tabulate`

The user's most recent instruction on this notebook: **"do not use
tabulate — keep it at default display — it looks good in github."** This
directly reverses the earlier "make the df look more like the markdown
table with solid borders" request. Cells 9 and 12 were rewritten to use
plain `print(df.to_string())` instead of `tabulate(df, headers="keys",
tablefmt="grid", showindex=True, disable_numparse=True)`. The notebook was
re-executed end-to-end with zero errors after the change, and the
row-number-based flagging in Cell 15 was verified to still correctly
resolve to `id` (row 25) and `policy_code` (row 77) — the sorted column
order that determines row position is unaffected by how the table is
rendered, only by the (unseeded) sample *values*, so this was a safe,
display-only change.

### 6.6 Cast-rate typing results (Cell 6/7, unchanged since v1/v2)

Every column in `windowed` checked for `TRY_CAST(... AS DOUBLE)` success
rate: 114 columns numeric, 38 categorical/text, **zero** landing in a "mixed"
ambiguous bucket by the cast-rate test alone — the ambiguity that does exist
(`id`, `policy_code`) only shows up once real sample values and cardinality
are eyeballed, which is exactly why Cell 3/9's eyeball step exists as a
separate, human-in-the-loop check on top of the mechanical split.

### 6.7 Full null%/cardinality profile (Cell 17/18)

Uses DuckDB's `SUMMARIZE windowed` in one pass, printed in full (all 152
columns, via `.to_string(index=False)`, sorted by null% descending) —
**not** just the top 12, per the user's explicit instruction that this must
show every column, not a truncated headline list. Result: 2 columns 100%
null (`member_id` — scrubbed by Lending Club pre-publication, dead weight
not signal; `next_pymnt_d`), 80 of 152 columns fully populated, the top of
the missing-rate ranking dominated by hardship/settlement fields (structural
— most loans never enter hardship — not a data quality defect).

---

## 7. Notebook 3 — Data Quality & Integrity (`02_eda/02_data_quality_integrity.ipynb`)

**Status:** reviewed in this conversation (full cell-by-cell content shown
to the user in chat), but **no changes have been made to it yet** — the
review surfaced issues that are still awaiting the user's direction. This
section captures that review in full so it doesn't need to be redone.

### 7.1 What's in the notebook (27 cells)

| # | What it does |
|---|---|
| 1 | Connect; missingness ranked on the retained + borderline-dropped columns |
| 2 | Formal test: is missingness on those columns informative of `is_bad`? |
| 3 | IQR-based outlier counts, all 20 retained numeric features |
| 4 | Z-score outlier counts (cross-check against IQR) |
| 5 | Explicit plausibility rules for implausible values |
| 6 | Duplicate / uniqueness check — `id` uniqueness and full-row duplicates, at every pipeline stage *(added later, in a "gap-closure addendum")* |
| 7 | Leakage drop-list validation — re-scan all 151 raw columns' correlation with `is_bad`, independent of the original ingestion-time drop decision *(gap-closure)* |
| 8 | Outlier treatment decision — turns the cell-3/4 outlier *counts* into an actual per-feature recommendation *(gap-closure)* |

Cells 6–8 were added after "an audit found this notebook's original 5 cells
didn't cover row-level integrity or independently re-validate the
leakage-column drop list against the full raw schema" — stated directly in
the notebook's own "Gap-closure addendum" markdown cell.

### 7.2 The fixed candidate shortlist (Cell 2) — the Rule 3 nuance in practice

This is where the ~30-column fixed candidate shortlist described in §4.3
first appears. Its exact composition, per the notebook's own markdown:

- **Loan terms:** `loan_amnt`, `int_rate`, `term`, `grade`
- **Borrower risk signals:** `fico_range_low`, `delinq_2yrs`,
  `inq_last_6mths`, `pub_rec`, `pub_rec_bankruptcies`
- **Balance-sheet fields:** `annual_inc`, `dti`, `revol_bal`, `revol_util`,
  `tot_cur_bal`, `mort_acc`, `open_acc`, `total_acc`, `bc_open_to_buy`,
  `acc_open_past_24mths`, `mo_sin_old_rev_tl_op`, `num_actv_rev_tl`
- **Categorical context:** `emp_length`, `home_ownership`,
  `verification_status`, `purpose`, `addr_state`
- **Three borderline fields**, kept specifically to double-check whether
  they belong: `mths_since_last_delinq`, `tot_hi_cred_lim`, `bc_util`

The notebook's own markdown is explicit that this is **not** derived from
notebook 2's (or any) computation — it's a domain-judgment starter list,
picked before any of the diagnostic notebooks ran, and it names itself the
**candidate** set, deferring the actual, audited, data-driven narrowing to
`03_data_cleaning/01_cleaning_and_feature_prep.ipynb`. It also documents a
concrete example of that later narrowing: `avg_cur_bal` was on an earlier
version of the candidate list and was dropped after notebook 9's VIF check
found it redundant with `tot_cur_bal`.

The notebook also states plainly that documenting the list's origin at its
first point of use is itself a fix — "earlier drafts of this notebook used
this exact list without ever saying where it came from."

### 7.3 Findings from the notebook's own analysis (all evidence-backed)

- **Missingness (Cell 1/3):** 8 of the 30 checked columns have any
  missingness at all. Topped by `mths_since_last_delinq` (49.4%), then
  `emp_length` (5.9%), `bc_util` (1.1%), `bc_open_to_buy` (1.0%),
  `revol_util`/`dti`/`avg_cur_bal`/`inq_last_6mths` near-zero.
- **Is missingness informative? (Cell 2/6):** restricting to columns with
  ≥1,000 missing rows (to avoid noise from tiny samples), the real finding
  is `emp_length` — 27.4% bad rate when missing vs. 20.1% when populated (a
  7.3-point gap) on 70,579 rows. The largest *raw* gap
  (`inq_last_6mths`, −20.5 points) is correctly dismissed as noise because
  it sits on only 1 missing row. Recommendation: carry an
  `emp_length_was_missing` indicator into cleaning rather than imputing
  silently — directly the Missing Indicator Approach from KB §2.9/§13.
- **IQR outlier sweep (Cell 3/9):** full table across all 20 numeric
  features. `delinq_2yrs` highest at 20.0% flagged, `pub_rec` 18.0%,
  `pub_rec_bankruptcies` 13.0%, down to `revol_util` at 0.0%. Correctly
  interprets the top of the ranking as a mix of genuinely skewed continuous
  fields and a known IQR-method artifact on sparse count fields (most values
  sitting at exactly 0).
- **Z-score cross-check (Cell 4/12):** `delinq_2yrs` drops from 20.0% (IQR)
  to 1.4% (z-score) — read correctly as confirming a genuine heavy tail
  (which moves the standard deviation enough to shrink the z-score band)
  rather than a handful of isolated extreme rows.
- **Plausibility checks (Cell 5/15):** `dti < 0`: 2 rows. `annual_inc = 0`:
  213 rows. `revol_util < 0`: 0. `revol_util > 100`: 4,571 (correctly noted
  as plausible in real life — an over-limit account — not necessarily an
  error). FICO out of [300,850]: 0. `loan_amnt <= 0`: 0.
- **Duplicate/uniqueness check (Cell 6/19):** zero duplicate `id`s at every
  pipeline stage (`raw_mat` 2,260,701 rows / `matured` 1,348,099 /
  `windowed` 1,195,879, all fully unique), zero fully-duplicated rows (152
  columns identical) in `windowed`. Confirms the one-row-per-loan assumption
  every other notebook relies on, rather than just assuming it.
- **Leakage drop-list re-validation (Cell 7/22):** scans all 121 dropped
  raw columns (91 numeric-castable) for `corr(col, is_bad)`, independent of
  the original ingestion-time drop decision. Top correlations —
  `last_fico_range_high` (−0.68), `last_fico_range_low` (−0.58),
  `recoveries` (0.51), `collection_recovery_fee` (0.50), `total_rec_prncp`
  (−0.45) — are all clearly post-origination fields, confirming those drops
  were correct rather than merely plausible. 43 columns land in a "worth a
  second look" band (0.05 < |corr| < 0.5); auto-triaged by name pattern into
  redundant-with-retained (6), co-borrower/`sec_app_*` fields (10,
  structurally missing for solo loans, not leakage), post-origination
  outcome fields (12, same leakage family as the top-correlation group, just
  weaker), and 15 genuinely unexplained columns flagged as legitimate
  **Phase 1 feature candidates** (not leakage, not something to fold into
  Phase 0 cleaning): `orig_projected_additional_accrued_interest`,
  `num_tl_op_past_12m`, `all_util`, `open_rv_24m`, `emp_title`,
  `num_rev_tl_bal_gt_0`, `open_rv_12m`, `percent_bc_gt_75`, `open_acc_6m`,
  `bc_util`, `mo_sin_rcnt_tl`, `mths_since_recent_inq`,
  `mo_sin_rcnt_rev_tl_op`, `mths_since_recent_bc`, `open_il_12m`.
- **Outlier treatment decision (Cell 8/25):** turns the raw outlier counts
  from cells 3/4 into an actual per-feature decision — cap at 1st/99th
  percentile (8 features: `loan_amnt`, `dti`, `open_acc`, `revol_bal`,
  `tot_cur_bal`, `bc_open_to_buy`, `acc_open_past_24mths`,
  `num_actv_rev_tl`), leave as-is because log-handled (per notebook 9's
  validated log-transform set), leave as-is because naturally bounded
  (`int_rate`, `revol_util`, `fico_range_low`), leave as-is because the IQR
  signal is a known method artifact on sparse count data (`delinq_2yrs`,
  `pub_rec`, `pub_rec_bankruptcies`), or n/a because dropped entirely in the
  cleaning rebuild (`avg_cur_bal`, for multicollinearity per notebook 9's
  VIF check).

### 7.4 Issues found during review — not yet fixed

Two categories of issue were identified and communicated to the user; both
are still open (§8):

1. **"Expect:" framing with presupposed numeric outcomes**, in direct
   violation of the convention established on notebook 1 — present in five
   markdown cells: Cell 2 ("most retained columns near 0% missing;
   `mort_acc`, `bc_open_to_buy`, `pub_rec_bankruptcies`-style fields showing
   measurable missingness"), Cell 8 ("the most right-skewed fields... show
   the highest outlier counts"), Cell 11 ("rough agreement... but z-score
   should flag fewer rows than IQR"), Cell 14 ("most rules return zero or
   near-zero violations; `revol_util` over 100% is genuinely possible"), and
   Cell 24 ("most features need no additional treatment... a small number...
   are the real candidates for capping"). Fix: rewrite all five into
   "Answers:" framing, matching notebooks 1 and 2.
2. **Not yet converted to executive style** — several markdown cells,
   especially the "gap-closure addendum" section (cells 17, 18, 21) and the
   "what output shows" blocks in cells 23/26, are dense prose paragraphs
   that also currently repeat the *entire* raw printed table before their
   bullet takeaway, rather than the terser bullets/tables convention used
   elsewhere.

The user has not yet responded to these two flagged issues, nor to the
open question about the fixed-candidate-shortlist design and the "notebook
09 says X" forward-references (both raised in the same review round). **No
edits have been made to this notebook file.**

---

## 8. Open Items / Pending Tasks

In priority/sequence order:

1. **Notebook 3 fixes awaiting the user's direction** (§7.4): fix the five
   "Expect:"-framing cells, tighten the prose-heavy markdown into
   bullets/tables, and get an explicit verdict on the fixed-candidate-
   shortlist design and the forward-references to notebook 9's findings.
2. **Continue the one-by-one review workflow** for notebooks 4 through 14
   (`02_eda/03_univariate_distributional_visual.ipynb` onward) and finally
   `03_data_cleaning/01_cleaning_and_feature_prep.ipynb` — same standard:
   evidence-in-code, executive style, "Answers:" not "Expect:", the
   fourth-principle domain explanation wherever a notable pattern shows up,
   no `tabulate`.
3. **Notebook 2's `devesh_development`-branch commit (`d0045be`) needs to
   eventually be merged into `main`** (or the user may choose to keep
   iterating on `devesh_development` for a while longer before merging —
   this hasn't been decided).
4. **The user still needs to run `git push origin main`** (and now also
   `git push origin devesh_development` / open a PR, depending on how they
   want to land the branch) **themselves** — push is categorically
   unavailable from the Cowork sandbox side (see §9.3), though the VS Code
   Claude Code extension, running natively on the user's machine, *can* push
   with the user's real credentials if asked to.
5. **Housekeeping:** a large number of CSV asset files under
   `data/04_assets/tables/` show up as locally modified but unstaged/
   uncommitted on the user's machine (from `eda02_*` through `eda14_*` and
   `clean01_*` — see git status output referenced in §9.2). These weren't
   touched by anything in this conversation; they're presumably the result
   of some earlier notebook re-execution. They haven't been investigated,
   staged, or committed — worth asking the user whether these are expected
   or need attention before continuing the sweep.

---

## 9. Git & Environment Setup

### 9.1 Identity and constraints

- Local git identity configured (non-global, this repo only):
  `user.name = deveshusg`, `user.email = deveshusg@gmail.com`.
- **Pushing to GitHub is categorically impossible from the Cowork sandbox
  side of this workflow.** The sandboxed shell used for local commits has no
  reachable credential store — `git push` fails with `fatal: could not read
  Username for 'https://github.com': No such device or address`. This isn't
  a one-off bug to fix; it's a permanent constraint, and it's also correct
  behavior from a security standpoint — credentials should never flow
  through an assistant. **The user must always run `git push` themselves**
  after any round of local commits, from whatever environment does have
  real GitHub credentials (their own terminal, or the VS Code Claude Code
  extension running natively on their machine).
- A recurring operational snag: a stale `.git/index.lock` file has appeared
  more than once and blocked `git add`/`git commit`. The device-bridge shell
  cannot delete files by default (`rm` fails with "Operation not
  permitted"); the fix each time has been to call the delete-permission
  request tool for the repo folder (which the user approves via a prompt on
  their device), then `rm -f .git/index.lock` succeeds.

### 9.2 Branch history

- `main` — the primary branch. Commits so far: `0f5ec89` → `31dc632` (MVP
  before review v1) → `2279159` (MVP before review v2, the full first-pass
  16-notebook suite) → `a289ba4` (notebook 1 rewrite) → `e727a2e` (notebook
  2 rewrite, v2/20-cell version).
- **`devesh_development`** — created in this conversation at the user's
  explicit request ("make a new branch 'devesh_development' and any changes
  commited now will be in that only"), branched from the tip of `main`
  (i.e. includes everything through `e727a2e`). **All commits from this
  point in the conversation forward go on this branch, not `main`, until the
  user says otherwise.** First commit on this branch: `d0045be`, "Add
  project context docs; drop tabulate for default pandas display in
  eda01" — bundles three things: `CLAUDE.md` (new), `docs/Peaks2Tails_
  Knowledge_Base.md` (new), and the notebook 2 tabulate-removal rewrite
  described in §6.5.

### 9.3 Two working environments for this repo, and how they relate

1. **This Cowork session**, working through the `mcp__remote-devices__*`
   device-bridge tools: a shell on the user's own machine
   (`device_bash`), scoped to the connected folders
   (`E:\Claude Folder\credit-risk-portfolio`, plus a couple of sibling
   folders including the raw Peaks2Tails course material and datasets). This
   is where every commit described above actually happened — directly on
   the user's machine's real repo, not a copy. Files are also separately
   staged/committed to the user's machine via `SendUserFile` +
   `mcp__remote-devices__device_commit_files` when a file is produced inside
   Claude's own cloud workspace rather than edited in place on the device.
   Notebook re-execution (to regenerate outputs after an edit) happens via
   `nbclient`/`nbformat`, which had to be `pip install --user`'d onto the
   device's Python 3.10 environment in this session (along with
   `ipykernel`) since neither was present by default.
2. **The VS Code Claude Code extension**, running natively on the user's
   own machine with the repo folder open as its workspace. This is a
   **separate, independent Claude session** with no automatic memory
   transfer from this Cowork session — different system prompt, different
   toolset (native file/bash tools instead of the device-bridge/
   AskUserQuestion/SendUserFile tools this session uses), but it **does**
   have the user's real git credentials, so unlike this session, it can
   actually `git push` (and the user has been told to always review before
   letting it do so). `CLAUDE.md` at the repo root is auto-loaded by Claude
   Code at session start, which is the entire reason `CLAUDE.md` and this
   document exist — they're the bridge that lets a VS Code Claude Code
   session start with real context instead of nothing.

---

## 10. Style & Preference Reference — Quick Lookup

A condensed, scannable version of every style rule mentioned above, for fast
lookup while working on a notebook:

| Rule | Detail |
|---|---|
| Framing | "Answers:" (question the code will answer), never "Expect:" with a specific number |
| Prose density | Bullets and tables; minimal narrative paragraphs ("executive style") |
| Code comments | Short `#` comments describing what a block does; never describe what it doesn't do |
| Claims | Every markdown fact/number must trace to printed code output in the same notebook |
| Connection | Always `nb_setup.connect()` (read-only) or `nb_setup.create_fresh()` (ingestion only) — never ad-hoc `duckdb.connect()` |
| Column scope | EDA notebooks never data-drive column drops; only `03_data_cleaning` drops, with justification. A domain-judgment fixed candidate shortlist (not data-driven) is the one accepted exception, used from notebook 2 onward |
| Missingness/pattern write-ups | Explain the variable — meaning, whether missingness is signal, modeling treatment, further-analysis needs — not just the number |
| Table rendering | Plain pandas default display via `.to_string()` — **no `tabulate`**, it renders better on GitHub |
| Long text fields | Clip sample values to a fixed width (35 chars) so fields like `url`/`desc` don't distort table shape |
| Random sampling | Unseeded, but drawn `DISTINCT` so the 4 sample values per column are unique from each other |
| Ambiguous-column flagging | By row number + source table tag (`"numeric"`/`"categorical"`), not by retyping column names |
| Type layering | `inferred_type` (mechanical) is never overwritten; `domain_type`/`is_ambiguous` are additive columns on top, each evidenced |
| Workflow | One notebook at a time: propose/revise → show full content in chat → user comments → iterate → user says "go ahead" → sync to disk (+ usually commit, never push) |
| Git | Local commits only from this session; user always pushes; commits currently go to `devesh_development`, not `main`, until told otherwise |

---

## 11. Data Findings Established So Far — Reference Sheet

A running list of genuine, evidence-backed findings about this dataset,
worth keeping in mind for every later notebook so they don't get
re-discovered or accidentally contradicted:

- `member_id` — 100% null across `windowed`; scrubbed by Lending Club before
  publication. Dead weight, not signal.
- `id` — passes the numeric cast-rate test but is a loan identifier, not a
  measured quantity. Flagged ambiguous.
- `policy_code` — passes the numeric cast-rate test but is single-valued
  (constant) in this population; a category code, not a real quantity.
  Flagged ambiguous.
- `is_bad` — the modeling target column. Appears in the numeric-columns
  scan by construction (it's 0/1) but is not a feature and should never be
  treated as miscategorized.
- `hardship_flag` — always `'N'` in the `windowed` (matured-loan)
  population; it's a point-in-time "currently in an active hardship plan"
  indicator that has decayed to constant for finished loans. **`hardship_
  type IS NULL` is the field that actually reflects whether a loan ever had
  a hardship event.** Verified: `hardship_type` not-null → bad rate 70.5%
  (n=5,726) vs. null → bad rate 20.3% (n=1,190,153).
- `debt_settlement_flag` — Y → bad rate 100.0% (n=32,337) vs. N → bad rate
  18.3% (n=1,163,542). Close to definitionally tied to "bad" — worth
  treating as a potential leakage/definitional risk in later feature design,
  not a straightforward feature.
- `sec_app_earliest_cr_line` — should carry the `date` domain tag (it's the
  co-borrower's credit-history start date), same treatment as
  `earliest_cr_line`.
- `emp_length` — missingness is informative: 27.4% bad rate when missing vs.
  20.1% when populated (7.3-point gap, n=70,579 missing rows) — large enough
  and on enough rows to be real, not noise. Recommendation: carry an
  `emp_length_was_missing` indicator into cleaning rather than silently
  imputing.
- Row-level integrity — verified, not assumed: zero duplicate `id`s at
  every pipeline stage (`raw_mat`, `matured`, `windowed`), zero
  fully-duplicated rows (all 152 columns identical) in `windowed`.
- Leakage drop-list — independently re-validated against the full raw
  schema by correlation with `is_bad`; the original ~40-column drop list
  holds up (highest-correlation dropped columns are unambiguously
  post-origination payment/recovery/hardship fields). 15 dropped columns
  identified as legitimate Phase 1 feature candidates (not leakage, not
  errors in the original drop list, just not used in this first pass) — see
  the full list in §7.3.
- Outlier treatment decisions for the 20 retained numeric features are
  fully worked out in notebook 3 Cell 8/25 (§7.3) — 8 features slated for
  1st/99th-percentile capping, the rest either naturally bounded,
  log-handled (per notebook 9), a known IQR artifact on sparse count data,
  or dropped entirely (`avg_cur_bal`, for multicollinearity).

---

## 12. Technical Gotchas & Lessons Learned

Bugs and environment quirks hit during this project's build, with root cause
and fix — worth knowing so they don't get rediscovered the hard way.

### 12.1 `tabulate` silently reformats numeric-looking columns

Notebook 2's eyeball-preview table briefly used `tabulate(df, tablefmt=
"grid", ...)` to render solid-border tables. With no extra argument, it
auto-detects columns that look numeric and applies a *shared* float format
across the whole column — so `id` sample values (which mix an 8-digit loan
ID against much smaller numbers elsewhere in the same rendering pass)
printed as `6.85157e+07` instead of the actual integer `68546903`. Diagnosed
by isolating a single-row test (rendered fine) against the full ~114-row
table (broke) — confirmed it was a column-wide formatting decision, not a
per-cell bug. Fix at the time was `disable_numparse=True`. As of the most
recent round, `tabulate` has been dropped from the project entirely in favor
of plain pandas `.to_string()` display (§6.5) — this bug is now moot for
this codebase, but the underlying lesson (any table-formatting library that
"helps" by reformatting numeric-looking values needs to be told not to, or
avoided) is worth remembering if a similar library ever gets reached for
again.

### 12.2 `USING SAMPLE` + `DISTINCT` is flaky when combined directly

An early version of the eyeball-sampling code combined `DISTINCT` and
`USING SAMPLE` directly on a column (e.g. `SELECT DISTINCT col FROM
windowed USING SAMPLE k ROWS`). On `sec_app_earliest_cr_line` (11,548
non-null rows), this returned an **empty result once**, despite the column
genuinely having data — a flakiness specific to that combination, not a
real absence of data. Fixed by sampling from a `DISTINCT` subquery instead:

```sql
SELECT val FROM (SELECT DISTINCT "{col}" AS val FROM windowed WHERE "{col}" IS NOT NULL)
USING SAMPLE {k} ROWS
```

Retested across multiple columns including low-cardinality ones (`term`,
`hardship_type`) and a fully-null one (`member_id`, which correctly returned
empty) — confirmed reliable. This is the pattern used in the current
`sample_values()` helper in notebook 2 (§6.3).

### 12.3 Padding missing sample slots with `None` produces literal `"nan"` in output

When a column has fewer than `k=4` distinct non-null values (e.g.
`policy_code` with only 1, or `member_id` with 0), the remaining sample
slots need padding. Padding with `None` caused pandas to coerce the mixed
column and print the literal string `"nan"` in the output table — confusing,
since it looks like real data rather than "nothing to show here." Fixed by
padding with `""` (empty string) instead, verified to render as clean blank
cells.

### 12.4 Git push is categorically unavailable from the Cowork sandbox

Covered in full in §9.1 — not a bug, but worth restating here as a lesson:
don't try to work around it (e.g. by embedding a token or trying alternate
auth flows). It's a deliberate boundary, not a solvable problem from this
side of the workflow.

### 12.5 Stale `.git/index.lock` blocks commits, and `device_bash` can't delete by default

Hit more than once. Confirmed via `ps aux` that no git process was actually
running (so the lock was genuinely stale, not an active conflicting
operation), but `device_bash`'s `rm -f .git/index.lock` failed with
"Operation not permitted" — file deletion is disabled by default on the
device bridge as a safety measure. Fix each time: call the delete-permission
request tool for the specific folder (the user approves via a prompt on
their device), which enables deletion for that folder's subtree for the
rest of the session, then the `rm -f` succeeds.

### 12.6 `nbformat`/`nbclient`/`ipykernel` are not preinstalled on the user's machine

The device-bridge shell's Python 3.10 environment didn't have `nbformat`,
`nbclient`, or `ipykernel` available by default — needed to programmatically
edit and headlessly re-execute notebooks directly on the user's machine
(rather than editing a copy and shipping it back and forth). All three
installed cleanly via `pip3 install --user nbformat nbclient ipykernel`
(network egress from the device shell does reach PyPI), followed by
`python3 -m ipykernel install --user --name python3` to register the kernel
`NotebookClient(nb, timeout=280, kernel_name='python3')` needs to find. This
only had to be done once per session — worth checking whether it's still
installed before repeating the install step in a future session.

### 12.7 `AskUserQuestion` requires at least 2 options

Attempted at one point to confirm a single assumed default (git commit
identity) via `AskUserQuestion` with only one option — rejected outright
(`InputValidationError`, minimum 2 options, with explicit instruction not to
retry or invent a filler option). Fix: when there's genuinely only one
reasonable answer, just state the assumption directly in chat and proceed,
rather than forcing a tool call that doesn't fit the situation.

### 12.8 Nested f-strings with the same quote style don't parse in this Python version

While building notebook 3's leakage re-validation cell, an attempt to nest
an f-string using double quotes inside another f-string using double quotes
(inside a lambda used to build the "what output shows" markdown) failed to
parse. Fixed by precomputing the interpretive sentences as plain strings
*before* handing them to the lambda/markdown-generation step, rather than
trying to build them inline at the point of use. Visible in notebook 3's
Cell 22 code as the `top_corr_note` / `band_note` / `tail_note` variables
being fully assembled well before they're used.

## 13. Verbatim Key User Instructions — Chronological Log

The exact wording of every major direction-setting instruction given over
the course of this project, in order. Kept verbatim rather than paraphrased
because some of these are standing rules whose precise phrasing matters (the
"Answers: not Expect:" rule and the "explain the variable" rule especially
are quoted exactly elsewhere in this document, but having the full
chronological log in one place is useful for resolving any future ambiguity
about intent).

1. *"let's do one notebook at a time manual check. give me one by one
   notebook here with all markdown and code and output cells and I'll give
   my comments here"* — established the core review workflow.
2. *"this looks good. expectations should not have numbers or seem like the
   results are known before running the code cell."* — the "Answers: not
   Expect:" rule, given on notebook 1.
3. *"make changes in the notebook 1 as stated and push it to github. show me
   changed notebook 2 (not committed & pushed yet) then I'll give comments
   update it then show me notebook 2 then when i give go ahead commit it and
   push then do the same for next notebooks one by one."* — established the
   full propose → review → iterate → go-ahead → commit sequencing, and (at
   the time) the expectation of pushing, later corrected to "user always
   pushes, Claude never can" once the sandbox's credential limitation became
   clear.
4. *"let's make it a more executive style using more of bullets, tables &
   visual flows as required and less text. and keep short comments of what
   the below block of code does in the code cells following the best
   practice of code writing- for all notebooks. do not repeat what it
   doesn't do. in the ingestion notebook give a very brief intro of the
   dataset's publicly available info & files inside the raw folder."* — the
   global executive-style directive.
5. On notebook 2's structure: a request to add an "eyeball columns" step and
   an "ambiguous column flagging" step before the null% profile cell, remove
   any text presupposing modeling outcomes (specifically the phrase "~27
   columns eventually retained for modeling"), and print null% for **all**
   columns ordered descending, not just a truncated top-12.
6. *"in cell 10 markdown tell about the group columns with high missingness
   like hardship - what they mean what kind of variables they are does
   missingness is signal, should they be used in modelling, do they need
   further analysis if so which and when, how they would be treated if they
   are to be used and other details about them. - this is the purpose of eda
   excercise isn't it? ... this should be done for all analysis in all
   notebooks wherever required."* — the fourth, retroactive, project-wide
   principle (§4.4).
7. *"again executive style narative"* — a correction after the
   hardship/settlement narrative drifted back into prose.
8. *"in 'Eyeball the full column lists' code cell: 1- show the column names
   in a dataframe (one for numeric & one for categorical) where the 1st
   column is the name of the column and the 2nd to 5th column shows 4 values
   of that columns chosen at random (no seed), and in 6th column it should
   say is ambiguous as No. all 114 & 38 column names must be visible and all
   6 columns of the df must be visible. and in the next code cell it should
   only ask for the row numbers of the column to be put in ambiguous
   category with comments. first show me how this will be done here before
   making any changes in the notebook."* — the full eyeball-redesign spec
   (§6.2), explicitly requiring a plan-first approach before edits.
9. *"this looks good. aditionally make sure to pick a unique random sample
   in the eyeballing code, also can we make the df look more like the
   markdown table with solid borders? also fic the breadth of sample columns
   so that fields like url & desc dont distort the shape of the df?"* — the
   refinements that led to (at the time) adopting `tabulate`, plus the
   unique-sample and column-width-clipping fixes that are still in place.
10. *"`sec_app_earliest_cr_line` should get the `date` tag also there are
    many fields that are numerical in nature like 1 & 0 or 1,2 &3 but are
    actually category- how to handle them? and should they be handelled
    here? and what about flagging ambiguous with row number?"* — led to the
    final `DATE_LIKE`/`TIME_PERIOD_LIKE` tagging design and the row-number
    flagging mechanism.
11. *"dont commit but update the notebook on my system."* — an explicit,
    one-time instruction to sync to disk without committing; not a
    standing rule, but establishes that "update the notebook" and "commit
    it" are not automatically the same instruction unless stated together.
12. *"make a new branch 'devesh_development' and any changes commited now
    will be in that only."* — the current branching instruction (§9.2),
    standing until the user says otherwise.
13. *"do not use tabulate- keep it at default display- it looks good in
    github."* — reverses instruction #9's "solid borders" request; the
    current, correct state of the project (§6.5).
14. *"give a ~50 page (or more if required) summary doc of the conversation
    we've had to put into the vs code extention of claude code as context-
    it must have all the peaks 2 tails course details & context, what I am
    building, why, how, my style, building style format, rules, preferences,
    what i want in terms of how the whole project will be built, the birds
    eye view of everything we've talked about & a microscopic view &
    everything in the middle. do not leave out anything."* — the instruction
    that produced this document.

## 14. Appendix — Full Source of `notebooks/_shared/nb_setup.py`

Reproduced in full since every single notebook in the suite depends on it
and it's short enough to be worth having verbatim rather than paraphrased.
Note its own docstring is itself a good example of the project's preferred
documentation voice — direct, explains *why* the module exists (repeating
six lines across 16 notebooks means 16 places to fix), and is explicit about
what it deliberately does *not* do (import pandas/numpy on the caller's
behalf, since which of those a given notebook needs varies).

```python
"""
Shared setup used by every notebook in notebooks/01_ingestion/, notebooks/02_eda/,
and notebooks/03_data_cleaning/.

Why this exists: almost every notebook in this project started with the same
six lines -- connect to the interim DuckDB file, and make sure the two asset
folders (04_assets/tables, 04_assets/plots) exist before anything tries to
save a chart or a CSV into them. Repeating that in 16 places means 16 places
to fix if the path ever changes. This module gives every notebook one call
for it instead.

How to use it, from any notebook that lives two folders under notebooks/
(e.g. notebooks/02_eda/03_....ipynb):

    import sys, os
    sys.path.insert(0, os.path.abspath("../_shared"))
    from nb_setup import connect

    con, ASSETS_TABLES, ASSETS_PLOTS = connect()
    # -> read-only connection, both asset folders created if missing.
    # Every EDA notebook should call it exactly like this: EDA notebooks
    # never write to data/02_interim/.

The one notebook that's different is `01_ingestion/01_raw_to_interim.ipynb`
-- it doesn't connect to an existing interim file, it *builds* one from
scratch (deleting any old copy first). That's a different enough job that it
gets its own function, `create_fresh()`, below -- but it's still one call
from this same shared module, not its own inline copy of the setup logic.

This module does NOT import pandas/numpy for you -- keep those explicit
imports in each notebook, since which of them a given notebook actually
needs varies.
"""
import os
import duckdb

DEFAULT_DUCKDB_FILE = "../../data/02_interim/lendingclub.duckdb"
DEFAULT_ASSETS_TABLES = "../../data/04_assets/tables"
DEFAULT_ASSETS_PLOTS = "../../data/04_assets/plots"


def connect(duckdb_file=DEFAULT_DUCKDB_FILE, read_only=True,
            assets_tables=DEFAULT_ASSETS_TABLES, assets_plots=DEFAULT_ASSETS_PLOTS):
    """Connect to the interim DuckDB file and make sure the asset folders exist.

    Returns (con, ASSETS_TABLES, ASSETS_PLOTS) -- the same three names every
    notebook already used, so swapping the old inline lines for this call
    doesn't require renaming anything else in the notebook.
    """
    os.makedirs(assets_tables, exist_ok=True)
    os.makedirs(assets_plots, exist_ok=True)
    con = duckdb.connect(duckdb_file, read_only=read_only)
    return con, assets_tables, assets_plots


def create_fresh(duckdb_file=DEFAULT_DUCKDB_FILE,
                  assets_tables=DEFAULT_ASSETS_TABLES, assets_plots=DEFAULT_ASSETS_PLOTS):
    """Only for the ingestion notebook: delete any existing interim DuckDB
    file and open a brand-new one, so re-running ingestion always starts
    from a clean slate rather than appending to stale tables.

    Returns (con, ASSETS_TABLES, ASSETS_PLOTS), same as connect().
    """
    os.makedirs(assets_tables, exist_ok=True)
    os.makedirs(assets_plots, exist_ok=True)
    os.makedirs(os.path.dirname(duckdb_file), exist_ok=True)
    if os.path.exists(duckdb_file):
        os.remove(duckdb_file)
    con = duckdb.connect(duckdb_file)
    return con, assets_tables, assets_plots
```

## 15. How to Resume Work From This Document

If you're a new Claude Code session (or a human) picking this up cold:

1. Read `CLAUDE.md` first (auto-loaded already, if you're Claude Code) —
   it's the short version of everything in this file.
2. If deeper context is needed, read this file in full, and read
   `docs/Peaks2Tails_Knowledge_Base.md` before doing any modeling-adjacent
   work (PD, LGD, EAD, IFRS 9, segmentation, validation).
3. Confirm which branch you're on — work should continue on
   `devesh_development` unless the user has said to merge or switch back to
   `main`.
4. The next concrete task is §8, item 1: get the user's direction on
   notebook 3's open issues (the five "Expect:"-framing cells, the
   prose-density cleanup, and a verdict on the fixed-candidate-shortlist
   design), fix accordingly, show the result, and proceed to notebook 4 once
   the user says "go ahead."
5. Never push to GitHub. Never assume "commit" means "push." Always ask, or
   simply do the local commit and tell the user it's ready for them to push.
6. Never introduce `tabulate`, or presuppose an outcome in an "Expect:"
   line, or narrow EDA column scope outside `03_data_cleaning`, or open an
   ad-hoc DuckDB connection outside `nb_setup.py`. These four are the
   easiest ways to accidentally undo something this project has been
   deliberate about.
