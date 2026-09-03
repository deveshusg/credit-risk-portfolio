# Peaks2Tails — Credit Risk Modeling Knowledge Base

*Compiled from all files in the "Peaks 2 tails" folder (60 training decks, handwritten notes, regulatory documents, and Excel case-study workbooks on credit risk modeling, IFRS 9/CECL, Basel capital, and model validation). Organized by topic rather than by file, so related ideas across different decks sit together. Built in two passes: an initial native-text extraction, followed by an OCR/vision-based re-processing of the 29 handwritten/diagram-heavy PDFs that the first pass could not read — their content is now fully merged into the relevant topic sections (see §14 for the file-by-file map).*

---

## 1. Course Map / How the Material Fits Together

The material follows the structure of an "Integrated Credit Risk Modelling in Banks" curriculum (instructor: Karan Aggarwal, Risk Management Consultant, credit/market/operational/treasury risk, ICAAP/ILAAP/IRRBB, Basel, IFRS 9, Stress Testing):

1. **Module 1 – Scorecard Building**: PD via logistic regression, roll-rate & vintage analysis, scaling PD to scores, cutoff selection.
2. **Module 2 – TTC PD to Worst Case Default Rates.**
3. **Module 3 – LGD Modelling, RWA & Capital Computation.**
4. **Module 4 – Macro-economic modelling & scenario analysis.**
5. **Module 5 – ECL Computation under IFRS 9.**
6. **Module 6 – Capital Planning & Stress Testing under ICAAP.**
7. **Module 7 – RAROC computation.**
8. **Module 8 – Special modelling situations** (Low Default Portfolios, reject inference, behavioral variates, etc.)
9. **Module 9 – Data designs and model designs.**
10. **Module 10 – Final quiz and Excel case studies.**

Two Excel workbooks (`1.Raw Data..xlsm`, `2.ST_Bucket0.xlsm`, `5.ST_Bucket3.xlsm`) hold the underlying case-study data and worked examples referenced by the slide decks. Several PDFs are handwritten notes or image-heavy slide decks (mind maps, flowcharts) where little machine-readable text exists — these are noted below so you know to open the PDF directly for that content.

---

## 2. Foundations: Why Credit Risk Modeling Works the Way It Does

- **The core analogy** (from *Data Science & Credit Risk*): building a credit model is structurally identical to any classification problem (e.g., predicting employee attrition) — take historical data of past cases (borrowers), the attributes that were known about them, and the outcome (defaulted / not defaulted), clean it, and fit a classifier. But domain expertise matters: you cannot simply transplant generic data-science skill into credit risk without understanding the regulatory and definitional scaffolding around "default," "performance window," etc.
- **Segmentation is a prerequisite, not an afterthought**: "one size fits all" doesn't work in a bank. Loans must be segmented into portfolios and a separate scorecard built per segment.
  - **Segmentation levels**: (1) Essential, (2) Business-driven, (3) Data/statistical.
  - **Pre-requisites for a valid segment**: default rates must differ meaningfully across segments; each segment needs a material number/amount of loans and bads; segment default rate should have low correlation with the overall portfolio default rate.
  - **Segmentation checklist**: heterogeneity, discriminatory power, rank ordering, concentration, stability.
  - **How to judge if segmentation helped**: AUC of a segment within the segmented model should exceed AUC of that same segment inside an unsegmented model; the weighted-average AUC of the segmented model should exceed the unsegmented model's AUC; and for the same number of accepts, the segmented approach should produce a lower bad rate.
  - **Why decision trees are often used to *find* segments** even though logistic regression can technically handle multiple segments: trees capture non-linear interactions, are highly interpretable (important for regulatory explainability), handle heterogeneous populations by splitting them into more homogeneous sub-groups, and double as a variable-selection/reduction technique before a regression is fit within each leaf.

---

## 3. Data Design & Preparation

This is treated as its own discipline, not a preliminary step.

**Five (six) pillars of data design** (from *Data Designs*):
1. Data conceptualisation
2. Data definitions
3. Snapshot data creation
4. Data visualisation
5. Data transformation
6. Data governance

**Data definitions differ by model purpose** — this table recurs across multiple decks and is one of the most reused reference points in the whole folder:

| Model | Default/data definition | Performance window |
|---|---|---|
| Scorecards | Roll-rate analysis | Vintage analysis |
| Basel PD | 90 DPD | 1 year |
| IFRS 9 PD | Roll-rate or 90 DPD | Lifetime with quarterly term structure (1-year performance window) |
| Stress Testing PD | 30 DPD (rebuttable) | 9- or 13-quarter forecast, quarterly term structure |
| LGD | Parameter stressed | Crystallisation / cooling-off period |
| CCF (Basel) | — | 1 year |
| CCF (IFRS) | — | Lifetime, quarterly term structure |

**Snapshot design by model**:
- PD: non-defaulted at snapshot; defaulted-or-not in the performance window.
- LGD (defaulted accounts): defaulted at snapshot, recoveries tracked post-default.
- LGD (non-defaulted accounts): non-defaulted at snapshot, defaults + recoveries tracked in performance.
- EAD (Basel): non-defaulted at snapshot, defaulted in performance.
- EAD (IFRS): non-defaulted at snapshot, defaulted or non-defaulted in performance.

**Data transformation by model type**:

| Model | Transform X | Transform Y |
|---|---|---|
| Scorecard – logistic regression | Weight of Evidence (WoE) or splines | Default status |
| Scorecard – decision tree | (raw X) | Default status |
| Macro-economic model | Growth rates, lags | Default rate, log-odds, Vasicek Z |

**Cross-sectional vs. panel data, overlapping vs. non-overlapping snapshots** (from *Data Preparation*):
- Cross-sectional = one borrower, one record. Panel = one borrower, multiple records (monthly/quarterly snapshots).
- **Overlapping samples** — pros: more data points, more timely, allows frequent model refresh. Cons: introduces autocorrelation (overstates model performance), can reduce stability, and may fail regulatory independence requirements.
- **Non-overlapping samples** — pros: temporal independence, lower overfitting risk, cleaner attribution of performance changes. Cons: fewer data points, slower to reflect recent trends, less frequent updates.
- **The "snapshot math"**: minimum observations needed for 1 snapshot = Observation Window (OW) + Performance Window (PW) + 1 (for goods); for bads, OW + months-per-bad-definition + 1. Extra snapshots = (Total observations − (OW+PW+1)) ÷ snapshot frequency (1 for monthly, 3 for quarterly, etc.), rounded down. For non-overlapping snapshots: N snapshots require N × (OW+PW+1) observations.
- **Origination/snapshot period selection rules**: the period should represent the *future* loan book (not an anomalous business period); it needs enough defaults (rule of thumb cited: ~200 bads); can be a point-in-time window or span a full economic cycle; data can be cross-sectional or panel, monthly or quarterly.
- **Exclusion / waterfall analysis**: exclusions are split into "Observation exclusions" (e.g., wrong product category, missing FICO, no bureau hit — out of scope by definition) and "Performance exclusions" (e.g., thin file, inactive, lost card, fraud, deceased, closed within performance window — would bias the performance definition). A worked example: 129,811 total population → 114,033 excluded (87.85%) → 15,778 final candidates (12.15%).

---

## 4. PD Modeling — Scorecards

### 4.1 Roll-Rate and Vintage Analysis (defining "default" and the performance window)
- Delinquency buckets: 0 DPD → 30 DPD → 60 DPD → 90 DPD → 120 DPD.
- **Roll-rate analysis** answers "which DPD bucket should count as default?" — track loans bucket-by-bucket over time (e.g., state at month x vs. state at month x+6), convert to percentages, and identify: % rolling forward (downgrading), % rolling backward (curing), % staying in the same bucket. The bucket with the *highest* roll-forward rate (lowest cure chance) is the defaulting bucket — analogized to "stage-4 cancer has the lowest chance of cure."
- **Vintage analysis** answers "how long should the performance window be?" — plot cumulative default rate against months-on-book (MOB); the point at which ~75% of eventual defaulters have already gone bad is the practical performance window. Too short a window underestimates the true default rate; too long wastes data (recent originations can't be used).

### 4.2 Logistic Regression Mechanics
- Y (default: 0/1) is categorical, so linear regression is inappropriate — logistic regression models log-odds, not probability directly: log(π/(1−π)) = β1X1 + β2X2 + ...
- **Estimation is by Maximum Likelihood (MLE)**, iteratively: start with seed coefficients, compute fitted probabilities, refine.
- **CATEGORICAL mnemonic used to structure the whole logistic-regression validation workflow**:
  - **C**oefficient estimation via MLE
  - **A**ssumption checking (multicollinearity via VIF — logistic regression doesn't need to check heteroskedasticity/autocorrelation the way OLS does)
  - **T**esting individual coefficients (Wald test, vs. t-test in OLS) and overall model
  - **E**xhaustive variable selection (forward/backward/stepwise)
  - **G**eneralisation (K-fold cross-validation)
  - **O**bserved vs. predicted PD error (Pearson/deviance residuals, vs. MSE/RMSE/MAE in OLS)
  - **R**-square (McFadden's, Cox & Snell's, Nagelkerke's — pseudo-R² analogues since OLS R² doesn't apply)
  - **I**nformation criteria (AIC, BIC vs. Adjusted R² in OLS)
  - **C**umulative bads vs. cumulative goods → KS statistic
  - **A**rea under the curve (discriminatory power)
  - **L**emeshow test (calibration / goodness-of-fit test — chi-square based)
- **Linear vs. logistic regression, side by side** (a recurring comparison table across several decks): coefficient estimation, assumption checks, hypothesis tests, variable selection, generalisation, error measures, R², information criteria, and calibration tests all have direct analogues but different underlying statistics.

### 4.3 Binning (Weight of Evidence / Coarse Classing)
- Binning partitions a continuous or categorical predictor into mutually exclusive, collectively exhaustive groups ("characteristics" once binned) — statistically equivalent to creating dummy/indicator variables.
- **Why bin**: captures non-linear relationships between predictor and target; tames outliers while still retaining their information; improves interpretability; lets business/domain judgment override pure statistics where sensible.
- **Fine binning → coarse binning**: fine binning creates many narrow bins (captures pattern *and* noise); coarse binning merges fine bins into fewer, wider bins that satisfy monotonicity/materiality constraints, reducing overfit. Coarse bins are used for actual scorecard training, not fine bins. Coarse bins are reversible/adjustable without touching the underlying fine bins, but changing fine bins invalidates the coarse binning built on top.

### 4.4 Variable Selection
- **Two-stage funnel**: feature preparation/processing (feature engineering: ratio creation — DTI, LTV, utilization; interaction terms; lag/growth transforms; WoE discretization) → feature selection (basic filters → statistical filters → wrapper methods → embedded methods).
  - **Basic filters**: remove constants, quasi-constants, duplicates (a data-cleaning step, not real "selection").
  - **Statistical filters**: select variables individually — correlation strength, intuitive sign, WoE trend monotonicity, high Information Value (IV).
  - **Wrapper methods**: select variables collectively — forward/backward/stepwise regression driven by R², AUC, p-value, VIF, or exhaustive search.
  - **Embedded methods**: penalized regression (ridge, lasso, elastic net) that "unselect" variables prone to causing overfitting as part of model tuning.

### 4.5 Reject Inferencing
A 6-step process to correct for the fact that a scorecard built only on *accepted* loans is biased (it never observes what would have happened to rejected applicants):
1. Build a base logistic regression model on accepts only.
2. Infer the performance of rejected applicants using a reject-inference technique.
3. Combine accepts + inferred rejects into one "complete population" dataset.
4. Rebuild the logistic regression on the complete population → the "final logit model."
5. Validate the final model.
6. Build the final scorecard from it.
- **Analogy used in the deck**: an admissions program that only sees outcomes for admitted students underweights criteria that matter for rejected applicants; once it incorporates data on rejected applicants' performance at other schools, the revised model reduces bias in variable weighting.

### 4.6 Scaling PD to a Score, and Cutoffs
- **Scaling formulas**: Score = Offset + Factor × ln(Odds); with a "points to double the odds" (PDO) convention: Factor = PDO / ln(2); Offset = Score − Factor × ln(Odds). Worked example: 20:1 odds at a score of 600 with 50 PDO → Factor = 72.13, Offset ≈ 383.90.
- **Statistical cutoffs** vs. **business-driven cutoffs**:
  - Statistical: cost-benefit analysis (Bayes decision rule, minimax, Neyman-Pearson), or maximizing discriminatory power (max KS distance, max Youden index).
  - Business: maximize acceptance rate subject to a bad-rate constraint; minimize bad rate subject to an acceptance-rate constraint; or maximize profitability directly.
- **Confusion-matrix framing specific to credit**: True Positive (correctly predicted defaulter) has payoff 0; False Negative (missed defaulter) costs LGD; False Positive (rejected a good customer) is an opportunity cost; True Negative (correctly approved) earns interest.
- **Statistical vs. business cutoff selection pipeline**: interactive grouping → data partition → build scorecard → reject inference → repeat on rejects → apply scaling.

### 4.7a Behavioral Scorecards — Variable Construction (from OCR of *4609-Behavioral Variates.pdf*, handwritten notes)
- **Model architecture choice**: build at facility/account level or borrower/customer level? A common two-step architecture: build account-level scores first, combine multiple account scores per customer via **Min** or **Average**, then blend into a customer-level score: `Customer score = b0 + b1×account_input_Type1 + b2×account_input_Type2 + Σd×customer_variables`.
- **Behavioral covariates fall into four families**, each with concrete derived-variable recipes:
  1. **Delinquency** — current bucket, max bucket in last 3/6/9/12m, number of times bucket increased/decreased/stayed flat, consecutive-month streaks of bucket increase.
  2. **O/S Balance & Utilization** — average/max balance or utilization in last 3/6/9/12m, % change in balance/utilization, ratio of current balance to trailing average.
  3. **Payment & Pay%** — Pay% = Payment ÷ O/S balance of each month. Recipes: average/max pay% in last 3/6/9/12m; number of times payment > EMI or > 125% of EMI; number of months with increase/decrease/no-change in pay% (and the same restricted to months where bucket > 0); max consecutive-month streak of such increase/decrease/no-change.
  4. **Bank A/C-related behavior** — salary variables (% of times salary received in last 3/6m, average salary received), credit/debit amount variables (average credit/debit in last 3/6m, % of times credit > debit, % of times credit > 1.5× debit, ratio of current-month debit/credit to the 3/6m average), and cheque-return rate in last 3/6m.
- **Correlation rule of thumb**: once all candidate behavioral variables are assembled, if pairwise correlation between two variables exceeds 50%, keep only one of them to avoid instability from multicollinearity.
- **Performance-status construction mirrors behavioral-variable construction** — marked monthly. Performance = delinquency bucket + default status; default = 1 once delinquency bucket ≥ 4. Three default-status conventions:
  - **Ever-bad definition**: once bucket hits 4, default status is permanently 1 (never reverts).
  - **Instant cure**: if bucket returns from ≥4 to 0, default status instantly reverts to 0.
  - **Probationary cure**: bucket stays "stuck" at 4 for a probation period (e.g., 6 months) even after cure, and default status only reverts to 0 at the end of that period if all installments in the window were paid.
- **Practical modeling FAQs captured verbatim**: You do not need 5 full years of performance data to build a model — you can build on a recent 4–8 month snapshot and then calibrate the result to the long-run average default rate. Even after calibrating to long-run average, you still compute PD from logistic regression because the logistic model serves two objectives simultaneously: (1) risk differentiation/rank-ordering and (2) the raw PD estimate that then gets calibrated — Step 1: compute PD from logistic regression; Step 2: map PDs to a master rating scale and assign a Credit Risk Rating grade; Step 3: take the master-rating-scale mean PD (or logistic-average PD) per grade; Step 4: calibrate to the long-run observed default rate via isotonic regression, Platt scaling, or the log-odds shift method.

### 4.7b Master Rating Scale (MRS) — Design and Validation (from OCR of *4609-Behavioral Variates.pdf*)
- **Why an MRS**: (1) gives the bank a common language across products — e.g., a retail loan with PD 2% should be treated on par with a corporate loan with PD 2%; (2) ensures consistency in the number of grades and uniqueness in assigning PD.
- **Design steps**: (a) collect modeled PDs for all retail/corporate/SME loans per their individual IRRS (Internal Risk Rating Systems); (b) decide the number of grades required (typically 8–25) and set an anchor PD (e.g., Grade 7 = PD 3.8%); since PDs should increase exponentially, define a scaling factor — grades above the anchor are multiplied sequentially by the scaling factor, grades below are divided sequentially by it (ensuring linear PD spacing on a log scale); take the geometric mean to get each grade's upper/lower band (ensuring log-distances between min, mean, and max PD are equal); (c) find the modeled-PD average for each band; (d) validate the MRS. An alternate, popular way to design the MRS is fitting an exponential curve to S&P's or Moody's long-run average default rates.
- **Trade-off note**: too many grades → instability problems; too few grades → loss of granularity and concentration-exposure problems.
- **PIT vs TTC ratings note**: if the IRRS includes macroeconomic variables (MEVs) in computing logistic PD, ratings will change as macro conditions change — this is called a **PIT rating system**.
- **Validating the MRS** — assign a grade to each borrower per the MRS, then check: (a) **Discriminatory power** (needs # goods/bads per grade); (b) **Rank ordering**; (c) **Concentration** — no single grade should hold more than ~15% of exposure; (d) **Heterogeneity** — perform a t-test to confirm adjacent bins are statistically distinct; (e) **Stability** — check whether the observed default rate is stable over time per grade (in practice this can't be optimized exactly, since sub-portfolio composition shifts with the business cycle — it requires an educated guess and a long-term bank commitment to stick with the chosen scale).
- **Rating mapping to external agencies**: internal ratings can be benchmarked/mapped to external (S&P/Moody's) ratings by finding the normalized distance from the internal grade to each external grade and mapping to whichever has the lowest distance, or by finding the likelihood of the internal grade coming from each external grade (via the Normal distribution) and choosing the grade with the maximum likelihood. Uses of this mapping: (a) **Benchmarking** — external ratings serve as a benchmark to measure internal-rating-system effectiveness/accuracy; (b) **Risk management** — if internal rating is downgraded but the external rating hasn't moved, compute an external-equivalent rating via the mapping system and set capital charges accordingly; (c) **Non-rated loans** — if a loan has no external rating, assign one via the internal-to-external mapping for business decisions.
- **Worked capital example** (mortgage pool, ties MRS/PD into Basel capital calc — see also §8): pooled PD = 1.5%, Housing Loan LGD = 40%, balance O/S = 80 lac, downturn-LGD formula DLGD = 0.08 + 0.92×ELGD, copula correlation parameter ρ = 0.15, CET1 = 1.5%, Tier 2 = 2%, capital conservation buffer = 2.5%, scaling factor = 1.06. WCDR = N[(N⁻¹(TTC_PD) + √ρ·N⁻¹(0.999)) / √(1−ρ)] = N[(N⁻¹(0.015) + √0.15·N⁻¹(0.999)) / √(1−0.15)] = 14.556%. DLGD = 0.08 + 0.92×40% = 44.8%. K% = (WCDR×DLGD − TTC_PD×ELGD) = 5.921%. RWA% = K%×12.5×1.06 = 78.45% (since min capital is 8% of RWA, RWA = 12.5× min capital). RWA = 78.45%×80 = 62.76 lac (labelled "Proportion of risky assets"). Required Capital = 62.76×11.5% = 7.22 lac.

### 4.7 Application vs. Behavioral Scorecards, and Where Scorecards Are Used
- **Use cases split by lifecycle stage**:
  - Application/Acquisition: risk-based pricing, credit limit setting, ATM limits, adjudication workflow, underwriting quality, payment terms, regulatory capital, due diligence.
  - Customer/Account Management: ongoing limit setting, economic capital, usage monitoring, renewal/repricing, card authorization strategy, collections, direct marketing pre-qualification, portfolio pricing/evaluation, cross-sell, forecasting, early warning.
- **Soft pull vs. hard pull** (bureau inquiries): soft pulls (self-checks, pre-approval screening, periodic monitoring) don't affect credit score, aren't visible to other lenders, and typically don't need explicit consent. Hard pulls (actual lending decisions) can temporarily ding the score, stay visible on the report ~2 years (though impact fades), and require explicit consumer permission.
- **A cautionary discussion point** (posed as a quiz question in *Introduction_Scorecard*): a scorecard can have high Gini, pass validation and back-testing, and *still* be problematic for accept/reject decisions — implicitly flagging that statistical performance alone doesn't guarantee a scorecard is fit for a business decision (fairness, reject-inference bias, population drift, and interpretability all matter beyond raw discriminatory power).
- **Alternative-lender example (Toyota Financial)**: captive lenders can rationally accept higher credit risk than a bank because they have proprietary insight (e.g., resale value of the underlying asset) and a more holistic view of the customer relationship — illustrating why segment- and lender-specific scorecards matter.

---

## 5. Model Validation & Discriminatory Power

### 5.1 Three Lines of Defense (Governance Structure)
From the *Model Validation Masterclass* deck:
- **LoD1** — Model Owner/User, Model Developer, Model Implementation.
- **LoD2** — Model Risk Management, Model Risk Governance & Controls, Model Validation.
- **LoD3** — Internal Audit.
- LoD2's key activities: maintain validation policies/procedures/handbooks; build and maintain second-line controls (validation controls, performance-tracking controls) and their risk drivers; report risk to senior management; perform line-by-line (LbL) assessments of new/existing requirements for regulatory compliance.
- A **Group Risk Policy** formally documents each function's roles and responsibilities.

### 5.2 SR 11-7 — U.S. Federal Reserve/OCC Model Risk Management Guidance (present as a full source document, `sr1107a1.pdf`, twice in the folder)
Key definitions and structure worth internalizing:
- **Definition of a "model"**: a quantitative method/system/approach applying statistical, economic, financial, or mathematical theory to process inputs into quantitative estimates — comprising an information-input component, a processing component, and a reporting component. Applies even where inputs are partly qualitative/expert-judgment-based, as long as output is quantitative.
- **Model risk arises for two structural reasons**: (1) fundamental errors producing inaccurate outputs relative to design objectives and intended use; (2) the model being used incorrectly or outside its intended context/limitations.
- **Model quality dimensions**: precision, accuracy, discriminatory power, robustness, stability, reliability — different metrics matter for different model types (precision/accuracy for forecasting models; discriminatory power for rank-ordering models like scorecards).
- **Document structure** (useful as an internal governance checklist): Introduction → Purpose & Scope → Overview of Model Risk Management → Model Development, Implementation & Use → Model Validation → Governance, Policies & Controls → Conclusion.
- Application of the guidance should be **proportionate** — a community bank with few, simple models needs less elaborate MRM infrastructure than a large bank with extensive/complex model use.

### 5.3 Other Regulatory Model-Risk Frameworks (from *Plotting the Regulatory Picture*)
A cross-jurisdiction comparison table worth keeping as a quick reference:

| Topic | UK | EU | US | India |
|---|---|---|---|---|
| Central bank | Bank of England | European Central Bank | Federal Reserve System | RBI |
| Prudential regulator | PRA | SSM / EBA (harmonised practices) | OCC, Fed, FDIC | RBI |
| Basel capital rules | PRA (std. vs IRB) | CRD IV (qualitative) / CRR (quantitative) | Federal Reserve & OCC | RBI |
| Provisioning | IFRS 9 | IFRS 9 | CECL / ALLL | IFRS 9 |
| Stress testing | BoE stress test + ICAAP (PRA review via SREP) | EBA EU-wide stress test, ICAAP (CRD IV Pillar 2) | CCAR / DFAST (Federal Reserve) | ICAAP, Financial Stability Report |
| Model Risk Management principles | SS1/23 (PRA) | EBA/REP/2023/29 | SR 11-7 | No specific guideline (per this material) |

- **PRA's role in the UK** is described as functioning like a combination of the Fed's supervisory role and prudential-capital function; **RBI's role in India** is described analogously — both central bank and prudential regulator combined, unlike the UK/EU/US split.

### 5.4 Segmentation Performance & Discriminatory Metrics
(Cross-referenced with §2 above) — AUC, KS statistic, Youden index, Gini all recur as the standard discriminatory-power toolkit; Lemeshow's test (chi-square goodness-of-fit) is the standard calibration check.

---

## 6. Calibration & Margin of Conservatism (MoC)

### 6.1 The Model Development Lifecycle for Calibration
From *Calibration*, a full pipeline: Model Design → Data Treatment → Data Representativeness Assessment → Feeder Model / SME input assessment → Model Segmentation → PIT/Spot Model Build (sampling → variable reduction/transformation/missing-value treatment → segment build & test) → Model Performance testing (goodness-of-fit, accuracy, stability) → Calibration Segmentation → Calibration Process (long-run average default rate / downturn LGD/EAD per segment; aligning PIT/spot output to long-run/downturn levels) → MoC & Adjustments → Re-alignment for other use cases (e.g., pricing) → Development Documentation (Model Development Doc, Data Doc, Rating Summary, ProForma, SAT, Model Pre-Approval Doc — noting this may not reflect final production code) → Model Approval (submission to Validation Unit, regulatory notification).

### 6.2 PIT vs. TTC vs. Hybrid
- **PIT (Point-in-Time)** models react to current conditions; problem: capital requirements swing sharply — very high in downturns, very low in booms — which is itself destabilizing for large portfolios (mortgage book cited as a trillion-pound example).
- **TTC (Through-the-Cycle)** models use static, cycle-independent drivers, but may fail to reflect the *actual* current economic cycle.
- **Hybrid** (recommended by the UK's PRA for mortgage portfolios): blends the two. PRA formalizes this via a **"cyclicality"** metric measuring how PIT-like a model is.
- **Data-cohort tradeoffs**: PIT/overlapping cohorts have more data, no seasonality problem, but risk autocorrelation; TTC/non-overlapping cohorts have less data and a seasonality problem, but no autocorrelation problem.
- **Calibration period should span a full economic cycle**: must include at least one downturn (per EBA's regulatory technical standards on defining a downturn), should ideally capture the lead-up to and recovery from that downturn, and should span at least the latest five years of data as of estimation.
- **Data representativeness testing** (worked example included): compare the distribution of key PD drivers (e.g., revolving-utilization, payment behavior, balance trend) between the long-run-average calibration vintages and the most recent scoring month; check what % of recent-vintage accounts fall inside the 5th–95th percentile range established on calibration data. A worked table shows this consistently >85–100% across PD bands, concluding the calibration remains representative.

### 6.3 Margin of Conservatism (MoC) — Types A/B/C
- **Capital requirement formula**: Capital = Constant × EAD × PD × LGD × M (maturity adjustment).
- **MoC corrects modelled ("uncorrected") risk parameters**: MoC Corrected Parameter = Modelled Parameter adjusted by MoC-A, MoC-B, MoC-C.
  - **MoC Type A** — adjustment for **data/methodology deficiencies** (e.g., missing data).
  - **MoC Type B** — adjustment for **non-representativeness** (change in market/legal environment; forward-looking expectations).
  - **MoC Type C** — adjustment for **central estimation error** (rank-ordering error or calibration error).
- **Rank-ordering error**: occurs when the order of *calibrated* PDs disagrees with the order of *modelled* PDs for a pair of obligors ("discordant pairs"); quantified as the sum of absolute PD differences across discordant pairs, normalized to scale appropriately relative to portfolio size.
- **Calibration error MoC**: MoC = k·σ (a multiple of the standard error of the estimate).
- **PD/LGD/EAD as ratios**: any parameter can be affected via its numerator, denominator, or both by a given "trigger" (data or methodology issue); for each trigger you tabulate the count of defaulters/non-defaulters/obligors affected to size the required MoC add-on.

---

## 7. LGD, EAD & CCF Modeling

- **LGD via workout/recovery cash flows** — worked example: EAD = 550; discounted recoveries net of collection costs across 6 years summed and discounted at 5% gave a recovery rate (RR) of 33.27%, hence **LGD = 1 − RR = 66.7%**.
- **LGD regression modeling approaches** (from *GLM models*): because LGD is bounded between 0 and 1 (often with mass points at 0 and 1), specialized distributions are used:
  - **Beta regression** for LGD strictly between 0 and 1.
  - **Density blending/mixture models** — combine multiple densities (e.g., 0.4×pdf1 + 0.6×pdf2) into one new density applied across the whole dataset, without IF/ELSE branching; the "acid test" is that total probability across the domain sums to 1.
  - **Density stitching** — different densities applied to different regions of the data via IF/ELSE logic (e.g., a "one-stage inflated Beta" or "one-stage inflated Tobit" model to separately handle point masses at 0 and/or 1).
  - **Multi-stage models** — the optimizer runs multiple times, each stage filtering a data subset and estimating a density for it (example cited: a three-stage Beta AUF/LGD model), vs. **one-stage models** where the optimizer runs once on the entire dataset under one distributional assumption.
  - **General Linear Model (GLM) framework, three core assumptions**: (1) the dependent variable follows some distribution with parameter μ: y ~ f(μ); (2) the linear predictor η is a linear combination of features: η = Xβ; (3) μ is connected to η through a link function g.
- **EAD / CCF (Credit Conversion Factor)**: EAD = Amount Outstanding + CCF × Headroom (the undrawn "open to buy," OTB). A worked correlation-matrix example compares characteristic correlations between an LDP (low-default-portfolio) approach and an RP approach segmented by weeks-in-employment bands (e.g., <32 weeks, 32–66, 66–118, 118–188, 188+), each with differing LDP/RP rates (7%/9% up to 32%/23%).

### 7.1 LGD — Full 6P Framework (from OCR of *8663-LGD EAD.pdf*, handwritten notes)
Just like PD, LGD modeling is structured via the same 6P framework: **P**eriod, **P**rocyclicality, **P**ools (segmentation), **P**erformance & snapshot, **P**rediction, **P**erformance (evaluation).
1. **Period** — unlike the PD model's 1-year or 18-month window, LGD always tracks recovery for the *entire lifetime* of the loan; LGD = 1 − RR (recovery rate). First step: assign a bad flag per account (as in PD); second step: assign a workout recovery rate per account — this is the "workout approach." Since way-back defaulters have complete recovery info but recent defaulters have incomplete recovery info, LGD computed on incomplete recoveries would be understated, so recoveries are extrapolated using the **Chain Ladder Method** (a year-of-default × development-year triangle, extrapolating the missing lower-right corner). "Lifetime" in practice means the **workout period** — the point after which incremental recoveries become insignificant; this varies by product (typically 36–45 months) and is identified via a **cooling-off analysis** chart (cumulative recovery % vs. months since default, flattening out).
   - **Worked recovery/PV table**: for a 6-year workout with EAD=550, discount=5%, recovery and cost cash flows per year are discounted to PV; example results: sum of net-recovery PV = 183.0091, RR = 33.27%, **LGD = 66.7%** (matches §7's headline example).
2. **Procyclicality** — for Basel capital, start with average LGD (ELGD) and convert to downturn LGD via DLGD = 0.08 + 0.92×ELGD.
3. **Pools (segmentation)** — by: (a) product type (secured vs. unsecured); (b) LTV band (higher LTV → higher risk, for secured only); (c) time on books; (d) time since default; (e) balance outstanding; (f) risk-rating grade.
4. **Performance snapshot** — base population is (a) accounts Non-Defaulted at Observation but Defaulted in performance (NDAO), and (b) accounts already Defaulted at Observation. For already-defaulted accounts, PD doesn't need modeling (already 100%) but recoveries still need to be modeled.
5. **Prediction** — three levels of sophistication: **Simple methods** (simple/weighted average recovery rate per segment based on complete recoveries); **Intermediate method** (compute LGD per Chain-Ladder approach for each segment); **Advanced method** (model different components of LGD separately, e.g. for unsecured NDAO loans: Cure / Closed / Charge-off; for secured NDAO loans: Cure / Closed (%settlement) / Litigation → Closed (%full payment) / Sale of collateral. Advantages of the advanced/component approach: (i) as many components can be added as needed; (ii) each component can be modeled with a different statistical technique; (iii) overall LGD = Σᵢ [probability of component i × loss given component i]).
   - **Cure treatment note**: for Basel, cure is not considered ("once bad, always bad") — how cure is incorporated in business models affects how the default flag itself is defined. For LGD specifically, a cured loan still carries a loss to the extent of time value of money lost between default and the cure date.
6. **Performance (evaluation)** — confusion matrix, Spearman rank correlation, KS, stability.

### 7.2 EAD/CCF — Full 6P Framework and Worked CCF Example (from OCR of *8663-LGD EAD.pdf*)
1. **Period** — if default occurs within 1 year, the most conservative estimate of EAD is used. **Deterministic EAD**: for a term loan, the most conservative EAD estimate occurs for a loan that is 0 DPD today and defaults after 90 days, adding 90 days of interest and penalty to the outstanding amount. **Stochastic EAD**: for a credit card with O/S of 30K and a 100K limit, the exposure at default could be the current 30K or higher — just before default, borrowers tend to utilize more of the undrawn balance; this utilization-uptick rate is the **Credit Conversion Factor (CCF)**.
   - **CCF worked example**: credit limit = 3 lac (3L), loan amount at snapshot = 50K, EAD at default = 1.5L → **CCF = (EAD − Drawn) ÷ (Limit − Drawn) = (1.5L − 50K) ÷ (3L − 50K) = 40%**. General formula: **EAD = Amount O/S + CCF × Headroom**.
2. **Procyclicality** — compute average CCF first, then convert to downturn CCF and downturn EAD.
3. **Pools (segmentation)** — (a) product band (revolving vs. non-revolving exposure); (b) utilization/headroom; (c) risk rating; (d) time on books; (e) delinquency. Different CCF variants can be computed per segment.
4. **Performance snapshot** — three horizon-definition methods: **Cohort method** (accounts not defaulted at snapshot but defaulted within the next 12 months); **Fixed horizon method** (not defaulted at snapshot but defaulted in *exactly* 12 months); **Variable horizon method** (not defaulted at snapshot but defaulted in 3m, 6m, 9m, or 12m).
5. **Prediction** — simple models (segment-level average) vs. advanced models (regress CCF against explanatory variables).
6. **Performance (evaluation)** — power curve, confidence interval, Spearman rank correlation, stability.

---

## 8. Basel Capital & RWA

- **Standardized approach mechanics** (worked example): a $100 loan with a 50% risk weight gives RWA = $50. Minimum global capital requirement is **8% of RWA**. Risk weights range from 0% to as high as 1250% (a 1250% risk weight effectively means capital = full exposure).
- **Capital tiers, using a cricket-batting-order analogy**:
  1. **Common Equity Tier 1 (CET1)** — "star batsman" (highest quality capital).
  2. **Additional Tier 1 (AT1)** — "supporting batsman."
  3. **Tier 2 (T2)** — "all-rounder."
- **India-specific requirement (RBI)**: total minimum capital = 11.5% (vs. 8% global floor), broken down as CET1 = min(5.5% + 2.5% capital-conservation buffer), AT1 up to 1.5% max, T2 up to 2% max.
- **Capital Adequacy Ratio (CAR)** = Total Available Capital ÷ RWA, compared against the regulatory minimum (worked example: CET1=5, AT1=0.75 (capped), T2=1.0 (capped) on RWA of 50 → CAR = 6.75/50 = 13.5%, comfortably above the 11.5% RBI minimum).
- **Avoiding "double-counting" of expected loss**: since provisions already cover expected loss and capital covers *unexpected* loss (Worst-Case Loss − Expected Loss), regulators avoid double-penalizing banks by giving concessions — e.g., allowing general provisions into Tier 2 capital (capped at 1.25% of credit RWA), and fully deducting specific NPA provisions when calculating RWA for those NPAs.
- **Internal Ratings-Based (IRB) approach logic**: rather than assuming a flat 8%, IRB directly computes minimum Unexpected Losses (UEL) — for non-defaulted accounts: (WCDR × Downturn LGD × EAD) − (TTC PD × Downturn LGD × EAD); for defaulted accounts: (Downturn LGD × EAD) − (Actual/realized LGD × EAD). Since minimum UEL is defined as 8% of RWA, **RWA = 12.5 × UEL**. RWA is still computed (rather than working with UEL directly) because *actual* required capital ratios vary by country (e.g., India's 11.5% vs. the 8% global floor), so RWA acts as the common intermediate step before computing Available Capital and CAR against the local minimum.
- **Retail vs. wholesale exposure taxonomy** (Standardised vs. IRB approaches): Property (residential mortgage, commercial, ADC), Retail (credit cards, retail SME, other retail), Non-Retail (sovereign, bank, corporate, SME corporate, specialised lending — project/commodities/object finance, treasury/margin lending/equity). Under IRB, categories map to IPRE, QRRE, Financial Institution, Corporate (SME/general/large), and Specialised Lending sub-classes. Retail scorecards are purely quantitative; wholesale scorecards blend quantitative + qualitative factors.

### 8.1 The Three Basel-Family Regulations, and Why Losses Follow a Right-Skewed Distribution (from OCR of *7184-Basel PD model.pdf*, handwritten notes)
- Banks provide loans and can incur losses on them; these losses plot as a **right-skewed distribution**. Reading left to right along that distribution: **Expected Loss** (covered by **provisioning**, i.e. IFRS 9) → **Unexpected Loss (UEL)** up to the **Worst-Case Loss** (covered by **capital**, and priced into interest rates) → beyond worst-case, **stressed losses** (covered by insurance and capital buffers). The three main regulations governing this are (a) Basel, (b) IFRS 9, (c) stress testing.
- **Standardised vs. IRB**: under the **Standardised approach**, risk weights are computed using a simple formula given by the regulator and capital = a % of RWA — there is **no loss modeling** in the standardised approach. Under **IRB**, extensive loss modeling is done — either modeling losses directly, or modeling the three components of loss (PD, LGD, EAD) separately (the **component-based approach**), which is the approach this course's capital-calculation material focuses on.
- **Worked expected-loss example**: bank loan = 100L, PD = 3%, RR (recovery rate) = 70% ⇒ EL = 3% × 70%... [as written: EL = 3%×(1−RR)×100L] = 2.1L.
- **WCDR (Worst Case Default Rate) — 3 equivalent ways of writing the formula**, depending on which correlation is supplied:
  - Variant 1 (given correlation *between loans*, ρ; convert to loan-market correlation via √ρ): **WCDR = N[(N⁻¹(PD) + √ρ·N⁻¹(0.999)) / √(1−ρ)]**
  - Variant 1b (with ρ² in the denominator root): **WCDR = N[(N⁻¹(PD) + √ρ·N⁻¹(0.999)) / √(1−ρ²)]**
  - Variant 2 (given correlation *between loans and the market* directly, use as-is; also shown with the complementary 0.001/negative-sign form): **WCDR = N[(N⁻¹(PD) − √ρ·N⁻¹(0.001)) / √(1−ρ)]**, and the ρ² denominator variant likewise.
  - (Cross-referenced to the "Vasicek Class 1/2" material in the *Building Blocks of Basel* module — flagged in the notes as "Must!!" exam-relevant content.)
- **PD modeling under Basel — the 6P approach** (mirrors the PD 6P framework used elsewhere; this is the Basel-specific instance):
  1. **Period** — Y is a default event; per Basel, default = 90 days past due. For non-regulatory purposes, default can instead be defined via **roll-rate analysis** (the point where the roll-forward rate is highest — see §4.1). Performance window: per Basel = 1 year; for non-regulatory purposes, chosen via **vintage analysis** (the point where the cumulative default-rate curve stabilizes — see §4.1). Basel also follows "once bad, always bad" (cure not considered).
  2. **Procyclicality** — two types of PD: **TTC PD** (long-run average over the economic cycle) and **PIT PD** (changes with the macro environment); Basel uses TTC PD because (a) capital cannot be volatile — since capital is difficult to raise, it needs to be stable, and (b) PIT PD promotes procyclicality: during a recession PIT PD is higher, so capital requirements would be higher and harder to raise exactly when times are bad; also during a recession banks using PIT PD would approve fewer loans, when actually banks should be providing *more* credit to help revive the economy.
  3. **Pools (segmentation)** — banks don't build a single model on the entire portfolio; instead segment into homogeneous pools where within-pool bad rate is similar but between-pool bad rate differs significantly. Segmentation dimensions (in order applied): product-based (mortgage, QRRE, other retail) → MOB (seasoned >6 MOB vs. non-seasoned <6 MOB) → relationship with customer (new-to-bank vs. existing-to-bank) → thin file vs. thick file (bureau info) → delinquency (clean vs. dirty).
  4. **Performance & snapshot** — model is built the way it will be applied. Base for PD modeling = non-defaulted at snapshot, defaulted-or-not in performance. Two customer types at application: **non-seasoned (newly originated)** accounts — payment behavior unknown, so PD is predicted from application variables only, and at development time the snapshot = origination, relating default event to explanatory (application) variables; **seasoned accounts** — payment behavior is known, so PD is predicted from payment behavior observed in the observation period, and at development time the snapshot = a different (later) point, relating default event to behavioral variables.
  5. **Prediction** — calculate PD per loan via logistic regression; assign PD to a rating grade based on the Master Rating Scale (§4.7b); calculate average PD or Average Default Rate (ODR) per grade (the "**PD curve**"); compute WCDR using the regulatory formula above; designing the MRS and computing capital come later in the course as part of the Basel module.
  6. **Performance evaluation** — validate the model for (a) discriminatory power, (b) calibration accuracy, (c) model stability (cross-referenced to the Model Validation module).
- **The regression-preparation prerequisite (MENTOS)**: before doing regression for PD, data must be prepared using the **MENTOS** or **discretization** approach (§16 below has the full MENTOS/DPMENTOS pipeline). Logistic regression steps: (1) compute ŷ = b0+b1x1+b2x2+…+bnxn (range −∞ to ∞); (2) convert ŷ to probability via the sigmoid function, PD = 1/(1+e^(−ŷ)) or e^ŷ/(1+e^ŷ); logic: logistic regression actually regresses **log-odds** against the explanatory variables (Odds = Prob/(1−Prob), ln(Odds) = b0+b1x1+b2x2+…); Prob = Odds/(1+Odds) = e^(ln Odds)/(1+e^(ln Odds)); (3) solve parameters b0,b1,b2,… via MLE — i.e. maximize the sum of log-likelihood, where the likelihood contribution is d = pʸ(1−p)^(1−y) (if y=1, d=p; if y=0, d=1−p; L = Π d).

---

## 9. IFRS 9 / ECL / CECL

### 9.1 IFRS 9 Staging Framework
| Stage | Description | ECL recognized |
|---|---|---|
| Stage 1 – Performing | Assets at initial recognition with low credit risk; no Significant Increase in Credit Risk (SICR) since origination | 12-month ECL |
| Stage 2 – Underperforming | SICR since initial recognition (rebuttable presumption: 30+ DPD) | Lifetime ECL |
| Stage 3 – Impaired | Non-performing / credit-impaired / objective evidence of impairment (rebuttable backstop: 90+ DPD); includes POCI | Lifetime ECL |
- **Important nuance**: a loan made to a risky borrower at origination can still start in **Stage 1** if the risk was already priced in (e.g., via a higher interest rate) at origination.
- **Purchased/originated credit-impaired NPAs** (e.g., NPAs bought from another bank) are classified directly into **Stage 3**.
- **Staging decision tree**: existing defaults → Stage 3; among performing accounts, 30+ DPD → Stage 2; TDR (troubled debt restructuring) → Stage 2; otherwise assessed on qualitative factors and a PD-change threshold (change in PD ≥ threshold → Stage 2, else Stage 1), with a separate carve-out for "low credit risk" exemption.

### 9.2 "IFRS 9 is the smartest regulation" — the SMARTEST mnemonic (from *ECL training*)
- **S** — Segment Analysis & Staging
- **M** — Matrix (multi-state) or 2-stage modeling approach
- **A** — Account-level or Segment-level models
- **R** — Rates: default rates or loss rates
- **T** — Term structure of PD
- **E** — Economic variables
- **S** — Scenario PD (Point-in-Time PD)
- **T** — Through-the-cycle PD

### 9.3 ECL Approaches: Collective vs. Individual, 2-state vs. Multi-state
- **Collective / PD×LGD×EAD approach**: staging + parameters assessed on a collective basis by grouping exposures with shared risk characteristics; suited to retail/SME portfolios; typically implemented as **2-state models** considering only Default vs. Non-default (account-level PIT scorecard using borrower attributes + macro variables).
- **Individual assessment**: parameters computed per exposure across a series of time intervals (monthly/quarterly/annually) over the life of the exposure; mandatory for large exposures; typically implemented as **multi-state / segment-level models** using transition matrices with multiple states (upgrade, downgrade, status quo, default) — transforms segment-level TTC default rates into PIT default rates via calibration/transformation, leveraging models already built elsewhere in the bank.
- **ECL component definitions and data requirements**:
  - **PD**: TTC PD → PIT PD calibration → 12-month and lifetime PD estimation. Data needed: historical Observed Default Rates (ODR), macro variables.
  - **LGD**: Workout LGD (historical average recovery) or Regulatory/FIRB LGD as proxy. Data needed: date of default, discount rate, recovery amount and date.
  - **EAD**: outstanding balance at reporting date (Stage 1) or repayment schedule (Stage 2), plus CCF for off-balance-sheet items. Data needed: amortization schedule, prepayment rates, CCF estimates.
- **Discounting requirement**: ECL must reflect the time value of money, discounted using the effective interest rate at initial recognition (or an approximation).
- **PD comparison table across frameworks**:

| Framework | PD | EAD | LGD | Horizon |
|---|---|---|---|---|
| Basel | TTC | TTC | TTC | 1 year |
| IFRS 9 | PIT | PIT | PIT | Lifetime |
| Stress Testing | Stressed | Stressed | Stressed | 3 years |

- **Regulatory capital formula referenced alongside ECL** (Basel/Vasicek single-factor model):
  K = EAD·LGD·[N( (N⁻¹(PD) + √ρ·N⁻¹(0.999)) / √(1−ρ) ) − PD] × (1 + (M−2.5)b) / (1 − 1.5b)

### 9.4 CECL (US) and Multi-state Transition Matrices
- CECL parallels IFRS 9's lifetime-loss philosophy but under US GAAP; treated in the folder mainly through **Markov transition-matrix modeling**: states are Current / Delinquent-30 / Delinquent-60 / Delinquent-90 / Severely Delinquent / Default, with a transition probability matrix estimated via logistic regression for each from→to pair (diagonal cells are "balancing figures" so each row sums to 1). A worked multinomial-logit transition model regresses transition probabilities on Original LTV, Credit Score, Loan Age, GDP, unemployment rate (Urate), and HPI (House Price Index) as macro/behavioral covariates — illustrating how CECL-style loss forecasting is directly built on multi-state survival/transition modeling (see §11 also).

---

## 10. Machine Learning & Statistical Toolkit Used in Credit Risk

- **Multinomial / Multi-ordinal Logit models** (extending binary logistic regression to >2 outcome categories):
  - Binary case: P(Y=1) = 1/(1+e^(−Xβ)); the intercept in logistic regression is interpretable as a **cutoff score** — the point where predicted probability = 50%, i.e., where b₁X = −b₀ (directly analogous to, but conceptually different from, the intercept in linear regression, which is just where X̄ and Ȳ satisfy the fitted line).
  - Multi-ordinal (3 categories A/B/C) needs **2 cutoffs** instead of 1; decision rule uses two threshold parameters a₁, a₂ against the linear predictor.
  - Multinomial logit defines a base category (say P(Y=A)) and models other categories relative to it, analogous to how binary logit treats P(Y=0) as the reference.
- **GLM family** (density/link-function framework) — see §7 for full mechanics; used as the general modeling frame that logistic regression, LGD Beta regression, and other bounded/skewed-outcome models are special cases of.
- **Reject inference, segmentation via trees, variable-selection wrapper/embedded methods** — all covered above in their PD-modeling context (§4), but are general ML techniques applied specifically to the credit-risk workflow.

### 10.1 Statistics/ML Branch Map and Model-Development Stages (from OCR of *5298-ML-Quants.pdf*, handwritten notes)
Six branches of statistics, mapped to their ML analogue: (1) Descriptive statistics → exploratory data analysis; (2) Inferential statistics → sampling theory; (3) Predictive analytics → supervised learning; (4) Forecasting → time-series modeling; (5) Cluster analytics → unsupervised learning; (6) Prescriptive analytics → reinforcement learning. (Broad umbrella: "Statistical Models vs. ML Models.") Example applications cited per branch: sales as a function of ad spend (supervised — regression); default rate as a function of macro variables (supervised); credit limit as a function of past payment behavior (supervised); customer/account default-or-not, cure-or-not (supervised — classification); transaction default-or-not (supervised); employee leave-or-not (supervised); geographical/marketing/portfolio segmentation (unsupervised — clustering); algo trading (reinforcement learning).
**Model development, 3 stages**: Step 1 Data preparation (**PREP / MENTOS** — §16); Step 2 Model development; Step 3 Model evaluation.

### 10.2 Logistic Regression as the Bridge from Statistics to Neural Networks
- Since raw Y ranges [0,1] but regression needs range (−∞,∞), apply the **odds/log-odds transform**: Odds = Prob/(1−Prob); log-odds = ln(Odds); back-transform: Prob = exp(ln Odds)/(1+exp(ln Odds)), i.e. the **sigmoid function**. So logistic regression = a **linear transformation** (summation operator) followed by a **non-linear transformation** (sigmoid/activation function) — this exact two-step structure is what generalizes into neural networks (§10.5).

### 10.3 Linear Discriminant Analysis (LDA) and Support Vector Machines (SVM) — Geometric Intuition
- **LDA**: given 2D data (e.g., age, income) for defaulters vs. non-defaulters, find the separating line by (1) choosing a direction vector **w** = w1·î + w2·ĵ and projecting every observation onto it (the projections are called "shadows"); (2) finding the w for which the **projected means** of the two groups are as far apart as possible, giving w1, w2. Any line perpendicular to **w** has equation w1x1 + w2x2 − c = 0; **c** (distance from origin to the line) is chosen as the **average of the projected means** of the two groups, i.e. exactly midway between them. Any point above the line has value w1x1+w2x2−c > 0; below, < 0.
- **SVM**: same setup, but instead of separating projected *means*, SVM finds the direction **w** for which the two nearest neighboring points (one from each class) are as far apart as possible — these are the **Support Vectors**. Analogy used: "constructing a road between two clusters of houses (the two classes) — you can't run over the houses, and you want the road as wide as possible." The separating hyperplane sits midway between the support vectors (c = average of the projected *support vectors*, not the full-group means). To give special importance to the support vectors, they are normalized so that any support vector above the line has value w1x1+w2x2−c = +1, and any below = −1 (achieved by dividing the line equation through by the plugged-in value); this produces the margin — the region between the "lower hyperplane" and "upper hyperplane" bounding the decision boundary.

### 10.4 K-Nearest Neighbours (KNN)
- To classify a new borrower (with attributes x1, x2): Step 1 — find the K nearest neighbors (K is a hyperparameter), where "nearest" is measured via **Euclidean distance** (√(Δx1²+Δx2²)) or **Manhattan distance** (|Δx1|+|Δx2|); worked example: points (1,1) and (5,4) → Euclidean = 5, Manhattan = 7. Step 2 — take the majority class among the K nearest neighbors; the new point is assigned that majority class.

### 10.5 Neural Networks
- **Intuition analogy**: if you're given information and asked to respond quickly, your conscious mind linearly processes it (summation operator) and activates a response (activation function) — this is logistic regression. If you have time to think more, your subconscious/intuitive mind processes it further and produces multiple candidate thoughts, which your conscious mind then synthesizes into a final conclusion — the subconscious is the **hidden layer**, multiple thoughts are **neurons**, and the conscious mind's final output is the **output layer**. **Logistic regression is a special case of a neural network with only an input and an output layer (no hidden layer).**
- **Mechanics**: each node in a hidden (or output) layer has two functional parts — a **Summation Operator (Σ)** that multiplies each input by a weight and sums the weighted values into the node's total net input, and an **Activation Function** that transforms that net input into the node's final output. Output from one layer transmits to the next layer's nodes (or to the output layer) the same way — this transmission process is called **Forward Propagation**. Number of hidden layers, number of hidden nodes, and number of output nodes are all tunable hyperparameters; a network with a very large number of hidden layers is called a **Deep Learning** network.
- **Training / Backpropagation**: weights are found via **backward propagation using the chain rule**: `New weight = Old weight − η × (dL/dw)`, where η is the **learning rate** and L is the loss function (log loss or squared-error loss, depending on task).
- **Advantages**: (1) can model complex non-linear interactions among features; (2) can model non-linearities through activation functions. **Disadvantages**: (1) with many hidden layers the model can become complex, increasing overfitting risk; (2) "black box" — lacks interpretability.

### 10.6 Gradient Descent (the general optimizer behind logistic regression, neural nets, etc.)
- To minimize a loss function L=f(w): set dL/dw=0 and check d²L/dw²>0 for a minimum, then solve for w. When this can't be solved analytically (or in closed form), use the numerical technique **Gradient Descent**: start with an initial w, compute dL/dw at that point. If the slope is positive, decrease w; if negative, increase w — in both cases via `new weight = old weight − η × dL/dw` (learn slowly, don't jump — i.e. keep η small).

### 10.7 ROC, Confusion Matrix, and Precision/Recall (mechanics behind the discriminatory-power metrics used throughout §4–5)
- **Confusion matrix** (Predicted D/ND vs. Actual D/ND): TP, FN, FP, TN. Accuracy = (TP+TN)/N; Error rate = 1 − Accuracy. Rates are always calculated keeping the *actual* class in the denominator: TPR = TP/(TP+FN), TNR = TN/(FP+TN), FNR = FN/(TP+FN), FPR = FP/(FP+TN).
- **Specificity & Sensitivity**: Specificity = TNR; Sensitivity = TPR.
- **Precision & Recall**: **Precision** — of what was *predicted* as bad, how much actually was bad: TP/(TP+FP). **Recall** — of what was *actually* bad, how much was correctly predicted: TP/(TP+FN) (i.e. Recall = TPR = Sensitivity). Interpretation: Recall = % of actual defaulters correctly predicted; Precision = % of predicted defaulters that are actually correct.
- **ROC/Gini curve construction, from scratch**: order accounts by score into buckets; compute Cumulative Good Rate = cumulative goods/total goods, Cumulative Bad Rate = cumulative bads/total bads; plot cumulative bad rate (y) against cumulative good rate (x). A **random model** (assigns scores randomly) traces the 45° line (%bad = %good in every bucket, since there's no discrimination). A **good model**'s curve sits above the 45° line, because for low scores %bad should exceed %good. Two properties: since it's a *cumulative* bad rate, the curve is always upward-sloping; and as score/bucket improves, cumulative bad rate increases at a *decreasing* rate. A **perfect model** assigns the lowest score to all defaulters, so plotting against lowest-score buckets gives 100% bad rate captured at 0% of goods — an "L-shaped" curve that hugs the axes.

### 10.8 Ensemble Learning (Bagging, Random Forest, Boosting)
- Rather than growing a single tree, grow multiple trees (an ensemble) and take the majority outcome (classification) or average outcome (regression).
- **Bagging (Bootstrap Aggregation) & Random Forest** — exam-prep analogy: rows are different topics, columns are different paper types (theory/practical/mixed/MCQ/item-sets); learning improves more from solving *random* questions across random topics (systematic solving alone isn't as effective) — solving random questions = **Bagging**; additionally picking random *papers* (not just random questions) makes learning even more rigorous = **Random Forest**.
- **Boosting** — learn from previous mistakes: (a) **AdaBoost** — start with equal weight on all observations, then increase the weight of misclassified observations each round; (b) **Gradient Boost** — start with a base model, compute residuals, and update residuals using η×w (a learning-rate-scaled update), iterating.

---

## 11. Survival Analysis (Time-to-Default Modeling)

Positioned as an alternative to point-in-time PD models — instead of predicting whether a borrower defaults within a fixed window, survival analysis predicts **when** default occurs, and handles **censoring** (loans that are still performing, or exit for other reasons like prepayment, at the time of the analysis). Full mathematical treatment reconstructed via OCR of the handwritten notes in *9102-Survival Analysis.pdf* and *8220-2. Discrete Time non parametric estimation (KM).pdf*.

### 11.1 Core Definitions (Continuous Case)
- Let T = time to default, a continuous random variable. f(t) = pdf. F(t) = P(T<t) = CDF = probability of default. S(t) = P(T>t) = 1−CDF = **survival function** = probability of survival. F(t)+S(t)=1; F(0)=0, F(∞)=1; S(0)=1, S(∞)=0.
- **Marginal probability of default in an interval**: P(t1<T<t2) = ∫ f(t)dt from t1 to t2 = F(t2)−F(t1) = S(t1)−S(t2).
- **Conditional probability** (default between t1 and t2, given survival to t1): P(t1<T<t2 | T>t1) = [S(t1)−S(t2)] / S(t1). Worked example: P(3<T<15 | T>3) = [S(3)−S(15)]/S(3); with S(3)=0.9, S(15)=0.8 → **1-year (12-month) forward PD = (0.9−0.8)/0.9 = 1/9**.
- **Hazard function h(t)**, derived from the survival function: S(t+dt) = S(t)+dS; ds = −S(t)h(t)dt = f(t)dt ⇒ h(t) = −(1/S(t))·(dS(t)/dt) — Eq (1); S(t) = exp{−∫₀ᵗ h(u)du} — Eq (2); h(t) = f(t)/S(t) — Eq (3).
- **Hazard shapes**: (1) constant hazard h(t)=λ ⇒ exponential distribution for T, S(t)=e^(−λt), f(t)=λe^(−λt); (2) piecewise-constant hazard (λ1, λ2, λ3 over successive intervals) ⇒ piecewise-exponential S(t); (3) a smoothly varying/humped h(t) is also possible (general case).

### 11.2 Discrete-Time Survival and the Kaplan-Meier (KM) Estimator
- Why the name "survival analysis"? If you can model the survival function and get survival probabilities, you can derive any kind of PD (e.g., 3-month PD for a loan 2-MOB old = [S(2)−S(5)]/S(2); 18-month PD for a loan 15-MOB old = [S(15)−S(27)]/S(15)) — so the entire discipline centers on estimating S(t).
- Under **Kaplan-Meier**, T is a **discrete** random variable — default/death occurs at discrete points in time. In discrete time, **conditional hazard = conditional probability**: `conditional hazard = (number who died in the period) / (survivors at beginning of the period)`. Computing "survivors" requires netting out not just prior-period defaulters but also individuals who dropped out / got lost mid-stay for other reasons (e.g. prepayment, missing data) — this is **right censoring**: if a loan is non-defaulted in the study period for any reason (prepayment, loan maturity, missing info, etc.), it is right-censored.
- **Formulas**: hⱼ = dⱼ/nⱼ (nⱼ = survivors/at-risk set, dⱼ = defaults at time tⱼ). Cumulative survival: S(t) = Π_{tⱼ≤t} (1−λⱼ). Cumulative probability of survival: S1 = S0×(1−h1), S2 = S1×(1−h2), S3 = S2×(1−h3), …. Cumulative probability of default: F(t) = 1−S(t), i.e. F1=1−S1, F2=1−S2, F3=1−S3.
- **KM is non-parametric (empirical)** — it observes the survival function directly from historical data with no distributional assumption. Results can be improved (made more reliable) by segmentation.
- **Formal discrete setup**: T is a discrete RV; nⱼ = survivors (risk set) just before tⱼ, dⱼ = defaults at tⱼ; hazard λⱼ = dⱼ/nⱼ. S(t) = Π_{tⱼ≤t}(1−λⱼ).
- **Kaplan-Meier likelihood construction**: for n total obligors with m deaths and n−m censored, define δᵢ = 1 if obligor i died (observed event), 0 if censored. Joint likelihood = Π_{all i, died} f(tᵢ) × Π_{all j, censored} S(tⱼ) = Π f(tᵢ)^δᵢ · S(tᵢ)^(1−δᵢ) = Π (f(tᵢ)/S(tᵢ))^δᵢ · S(tᵢ) = Π h(tᵢ)^δᵢ · S(tᵢ) (using h=f/S).
  - **Worked MLE example under constant hazard** h(t)=λ: L = Π λ^δᵢ · e^(−λtᵢ) = λ^m · e^(−λΣtᵢ); LL = m·ln(λ) − λΣtᵢ; ∂LL/∂λ=0 ⇒ **λ̂_MLE = m / Σtᵢ** (total deaths ÷ total time at risk).

### 11.3 Parametric Estimation (Continuous T)
- If T is continuous, S(t) takes a parametric form (e.g. assume T ~ Exponential(λ), fit λ from data, obtain a parametric S(t), then derive PD). Parameters estimated via **Maximum Likelihood Estimation**: Step 1 — start with a seed value of λ; Step 2 — if there is a default, likelihood = probability of default at that tiny instant = f(t)·δt (δt is constant across obligors so it can be dropped from the optimization); if there is no default (censored), likelihood = probability of survival till t = S(t); Step 3 — take ln of the likelihood (a monotonic transform) and find λ that maximizes the sum of log-likelihoods.
- **Exponential case worked out**: f(t)=λe^(−λt), F(t)=1−e^(−λt), S(t)=e^(−λt), h(t) = f(t)/S(t) = constant = λ.
- **Constant hazard is unrealistic** — hazard should generally increase or decrease with time. Two ways to get a more realistic picture: (a) **Piecewise constant hazard model** — break the observation period into smaller periods and estimate λ separately per period; (b) **use the Weibull distribution instead of Exponential** — its shape parameter α makes the failure/hazard rate increasing or decreasing with time. Failure-rate patterns: **increasing** (α>1, "aging problem," e.g. mortality); **decreasing** (α<1, "infant mortality/teething problem," e.g. startups, exams, divorce rate, CCC-rated companies); **constant** (α=1, reduces to Exponential). Weibull formulas: F(t)=1−e^(−(t/λ)^α); S(t)=e^(−(t/λ)^α); f(t)=(α/λ)(t/λ)^(α−1)·e^(−(t/λ)^α); h(t)=f(t)/S(t) = (α/λ)(t/λ)^(α−1) (not constant — a function of time). α = shape parameter, λ = scale parameter; both estimated via MLE.

### 11.4 Proportional Hazard (PH) Models and Cox Regression
- To model hazard as a function of both time and covariates x: **h(t,x) = h₀(t) × g(x)** — baseline hazard h₀(t) (a function of time, "gives shape to the hazard rate") multiplied by g(x) (a function of the covariates, "just a scaling parameter"). Convenient because it separates **time-dependence** from **x-dependence**; hence "**Proportional Hazard Model**." Why "proportional": for two loans with covariates x1, x2, the ratio h(t,x1)/h(t,x2) = g(x1)/g(x2) is **constant over time** (provided x1, x2 are not time-varying) — the baseline hazard cancels out.
- Assume g(x) = e^(βx). Estimation steps: (1) assume a distribution for T (exponential: h₀(t)=λ constant; or Weibull: h₀(t)=(α/λ)(t/λ)^(α−1)); (2) find h(t,x) = h₀(t)·e^(βx) (multiply); (3) find S(t,x) = [S₀(t)]^(e^(βx)) (power); (4) find the likelihood and maximize the sum of log-likelihoods.
- If both the baseline hazard *and* g(x) take a parametric form, this is the full **Proportional Hazard Model**. If the baseline hazard is left **non-parametric** while g(x)=e^(βx) is parametric, this is the **Cox Proportional Hazard Model**. Cox's motivation: (1) to understand which covariates matter (via β); (2) to perform sensitivity analysis — the focus isn't on obtaining h(t,x) directly, but on how much hazard changes per unit change in x.
- **Cox regression's key practical advantage**: β can be estimated by maximizing **partial likelihood** *without ever needing to know* h₀(t). Partial Likelihood = e^(βx) / Σe^(βx) (summed over the risk set at that failure time) — interpreted (per the notes, in the original mixed-language phrasing) as: "at a given time, everyone in the risk set could default, but among them, what's borrower j's actual likelihood of defaulting" = (force of mortality of j) / (total force of mortality of those still alive/at risk). Formally: Partial Likelihood = [λ₀(t)e^(βxⱼ)] / [λ₀(t)e^(βx1) + λ₀(t)e^(βx2) + …] — the λ₀(t) terms cancel.
  - **Worked example** (6-loan dataset with gender, MOB at exit, exit type D/C, δ): partial likelihoods computed as e^(βx)/[Σe^(βx) over risk set], e.g. for the first default: e^(β·0)/(e^(β·0)+e^(β·1)+e^(β·1)+e^(β·0)+e^(β·0)+e^(β·0)) = 1/(4+2e^β).
  - **Ties in event time**: handled via the **Breslow Approximation** — take the joint likelihood assuming (arbitrarily) one loan defaults first and the other later, i.e. multiply the two individual partial-likelihood expressions together.
  - **Time-varying covariates**: handled via the **Counting Process** approach (a.k.a. time-varying betas) — slice the entire period into smaller sub-periods, treating (1) every row as a separate "loan-period," and (2) covariates as constant within each such period.
- **Credit-risk application note**: for credit-risk applications, the baseline hazard is typically estimated via **KM**, and β via **Cox regression**; combining them gives S(t,x), from which PD is derived.

### 11.5 Accelerated Failure Time (AFT) Models
- Unlike PH models (which model hazard as a function of covariates), **AFT models accelerate or decelerate time-to-default directly** by regressing a transform of T against x. Typically t ~ log-normal, i.e. ln(t) ~ Normal: **ln(t) = α + b1·x1 + b2·x2 + e**, e ~ N(0,σ²), with β estimated via MLE.
- **Likelihood construction**: if a default is observed, need f(t) under the assumed distribution of ln(t): f(t) = f(ln t)/t = f(e)/t (density of the error term divided by t, from the change-of-variables Jacobian). If survived (censored), S(t) = S(ln t) = S(e) (since ln(t) is a monotonic transform).
- **Distribution-pairing table** (distribution of T ↔ implied distribution of the AFT error term e): Log-Normal T ↔ Normal e; Log-logistic T ↔ Logistic e; Gamma T ↔ Log-Gamma e; Weibull T ↔ Extreme Value (1-parameter) e; Exponential T ↔ Extreme Value (2-parameter) e.
- Once t and its parameters are estimated, S(t,x) — and hence PD — can be derived. Worked exponential example: h(t)=λ, h(t,x)=λe^(βx), S(t)=e^(−λt), S(t,x) = e^(−λ·e^(βx)·t) = (e^(−λt))^(e^(βx)); f(t,x)=h(t,x)·S(t,x). Worked Weibull example: h(t)=(α/λ)(t/λ)^(α−1), h(t,x)=h(t)·e^(βx).

Complements the CECL transition-matrix approach in §9.4 — both are ways of modeling the *timing* and *path* of default rather than a single binary PD.

---

## 12. Macro-Economic / Time Series Modeling

Full mathematical treatment reconstructed via OCR of the handwritten notes in *7728-1.8 Time Series.pdf* (28 pages, univariate ARIMA), *8796-VAR.pdf* (multivariate VAR), and *9433-VECM (1).pdf* (cointegration/VECM). This underpins the "term structure of PD," stress-testing PD, and scenario-based ECL work referenced throughout §9.

### 12.1 Trend, Seasonality, Stationarity, and Differencing (Univariate Foundations)
- Three patterns within a time series: **Trend**, **Seasonality**, **Cyclicality**.
- **Deterministic trend** (Yt = b0+b1t+et; E(Yt)=b0+b1t, non-covariance-stationary since mean depends on t; V(Yt)=σ² constant) vs. **Stochastic trend** (Yt = b0+b1·Yt-1+et; non-constant mean *and* non-constant variance). Coefficient-driven regimes: b1=1 ⇒ **Unit Root (Random Walk)**; b1>1 ⇒ **Explosive Root**; b1<1 ⇒ **Covariance Stationary**.
  - Under the unit-root random walk, iterating forward shows Yt = t·b0 + Σeᵢ, so E(Yt)=t·b0 (not covariance stationary) and V(Yt)=σ²·t (variance grows with t).
- **Fixing deterministic trend**: **detrending** (regress Yt on t, take the residual, which is ~N(0,σ²)) or **differencing**. **Fixing stochastic trend**: only **differencing** works (detrending does not remove a stochastic trend). Differencing a deterministic-trend series: ΔYt = Yt−Yt-1 = b1+et−et-1, E[ΔYt]=b1, V[ΔYt]=2σ². Differencing a stochastic-trend series: ΔYt = b0+et, E[ΔYt]=b0, V[ΔYt]=σ².
- **Deterministic vs. stochastic seasonality** mirrors the trend case: deterministic seasonality (seasonal effects constant over time) is modeled via dummy-variable regression (Yt = b0 + b1·Q1+b2·Q2+b3·Q3+et, or without an intercept using all 4 quarter dummies) or removed via seasonal differencing; stochastic seasonality (seasonal effects non-constant over time, e.g. Yt = b0+Yt-4+et) can only be fixed via seasonal differencing.
- **Summary table** (Deterministic Trend / Stochastic Trend / Deterministic Seasonality / Stochastic Seasonality) → stationarity status and fix: Det. Trend → Not stationary → Detrending or Differencing; Stoch. Trend → May be stationary → Differencing if unit-root random walk; Det. Seasonality → Not stationary → Dummy-variable regression or seasonal differencing; Stoch. Seasonality → May be stationary → Seasonal differencing if seasonal random walk.

### 12.2 Testing for Non-Stationarity: (Augmented) Dickey-Fuller Test
- Naively you might regress Yt = b0+b1·Yt-1 and t-test H0: b1=1; **but if b1=1 the series isn't covariance stationary, so the t-statistic of the coefficient doesn't follow a t-distribution** — the ordinary t-test is invalid. **Dickey & Fuller** developed a regression-based unit-root test on a transformed version of the AR(1) model: Yt−Yt-1 = (b1−1)Yt-1 ⇒ ΔYt = g1·Yt-1, where g1 = b1−1. **Hypotheses**: H0: g1=0 (⇒ b1=1, unit root); H1: g1<0 — a one-tailed (left-tailed) test, since we want to accept g1<0 for stationarity (g1>0 would imply b1>1, an explosive root). Step 2: compare the t-stat to **DF critical values** (not ordinary t-distribution critical values).
- **Augmented Dickey-Fuller (ADF)**: ΔYt = b0 + b1·t + b2·Yt-1 + b3·ΔYt-1 + b4·ΔYt-2 + … (deterministic term + lagged level + lagged differences). Practical rules: (1) **number of lag lengths** — enough to capture short-run dynamics and make the error term white noise; choose to minimize AIC (even if that selects more lags than BIC would); (2) **deterministic terms** — have more significant impact on the t-statistic; include deterministic regressors that are statistically significant at 10%. **Decision rule**: when the null (unit root) can't be rejected, first-difference the series and repeat ADF; if still can't reject, difference again and repeat; if it still can't be rejected, consider a transformation (e.g. natural log) before differencing again.

### 12.3 ACF, PACF, and Identifying AR/MA Order
- **Correlation vs. partial correlation**: a worked lemonade/ice-cream/temperature example shows raw correlation between lemonade and ice-cream sales (0.943) can be spurious — driven entirely by a third variable (temperature); the **true correlation controlling for temperature is the partial correlation**.
- **ACF** = correlation between lag 0 and subsequent lags; **PACF** = correlation between lag 0 and subsequent lags *controlling for the effect of intervening lags*.
- **Uses of ACF/PACF**: (1) detect whether a series is covariance stationary (ACF should exhibit decay in magnitude as lag increases, for a stationary series); (2) decide the order of AR/MA (for AR — PACF shows a cutoff/sharp drop, ACF exhibits gradual decay; for MA — ACF shows a cutoff, PACF exhibits gradual decay); (3) detect whether the error term is white noise (individual autocorrelations should lie within the confidence interval [0 ± (1/√T)×1.96], since ρ~N(0,1/T); joint test via **Box-Pierce** (large-sample: T×Σρ(k)² up to that lag) or **Ljung-Box** (small-sample: T(T+2)×Σ[ρ(k)²×1/(T−k)]) — both statistics follow a χ² distribution with df = number of lags tested; number of lags to check: m=√T for a pure AR/MA, or m>Max(p,q) for ARMA(p,q). H0: ρ1=ρ2=…=ρm=0 (series is white noise) — we generally *want* to accept this null on the residuals.

### 12.4 AR, MA, ARMA — Full Derivations
- **AR(1)**: Yt=b1·Yt-1+et. Via the definition Corr(Yt,Yt-k)=Cov(Yt,Yt-k)/√[Var(Yt)Var(Yt-k)] = γk/γ0 (since variance is constant under stationarity): γ0 = b1²γ0+σ² (derived by expanding Cov(Yt,Yt)); γ1 = b1γ0; γ2 = b1γ1. General **Yule-Walker recursions** for AR(1): ρ1=b1, ρ2=b1², ρ3=b1³ (ACF decays geometrically); PACF: α1=ρ1=b1, α2 = (ρ2−ρ1²)/(1−ρ1²) = b1²−b1² = 0 (cuts off after lag 1 — the AR(1) PACF signature). For **AR(2)**: yt=b1yt-1+b2yt-2+et; 2 Yule-Walker equations (γ0=b1γ1+b2γ2+σ², γ1=b1γ0+b2γ1, γ2=b1γ1+b2γ0) solved simultaneously for γ's in terms of b1,b2,σ², then ACF/PACF derived from them.
- **MA(1)**: Yt=b1·et-1+et. γ0=Cov(Yt,Yt)=b1²σ²+σ²; γ1=Cov(Yt,Yt-1)=b1σ²; γ2=Cov(Yt,Yt-2)=0 (all higher lags = 0, the MA signature). ρ1=b1σ²/(b1²σ²+σ²)=b1/(1+b1²); ρ2=0; PACF: α1=ρ1, α2=(ρ2−ρ1²)/(1−ρ1²) — does NOT cut off (decays instead), the mirror image of AR(1)'s ACF/PACF behavior. **MA(2)**: similarly, γ0,γ1,γ2 nonzero, γ3=0 (cuts off after lag 2, matching the MA order).
- **ARMA(1,1)**: Yt = b1·Yt-1+b2·et-1+et — for ARMA models, since neither ACF nor PACF cleanly cuts off, **graphical analysis alone cannot identify the order** — full likelihood-based estimation is needed instead.
- **Identification/estimation summary table**:

| Model | Identification | Covariance (γ) | Stationarity | Invertibility | Coefficients |
|---|---|---|---|---|---|
| AR | PACF cuts off / ACF exponential decay | Yule-Walker pattern | Characteristic eqn \|z\|>1 or \|b\|<1 | Always invertible | OLS/MLE |
| MA | ACF cuts off / PACF exhibits decay | No pattern, full calculation | Always stationary | Characteristic eqn \|z\|>1 or \|b\|<1 | MLE |
| ARMA | Both ACF & PACF exhibit decay | No pattern, full calculation | Characteristic eqn on AR component | Characteristic eqn on MA component | MLE |

### 12.5 Stationarity and Invertibility Conditions
- **Stationarity (AR side)**: for Yt=b1Yt-1+b2Yt-2+…+bpYt-p+et, form the characteristic equation 1−b1z−b2z²−…−bpz^p=0; if **all roots satisfy |z|>1**, the series is stationary. Worked AR(1): 1−b1z=0 ⇒ z=1/b1; condition |z|>1 ⟺ |b1|<1. Worked AR(2) example: yt=(5/6)yt-1−(1/6)yt-2+et ⇒ characteristic roots z=2, z=3, both |z|>1 ⇒ stationary.
- **Invertibility (MA side)**: a process is invertible if et can be expressed as a linear combination of past y-lags. AR processes are *always* invertible (et can always be isolated by rearranging: et=yt−b1yt-1 for AR(1), et=yt−b1yt-1−b2yt-2 for AR(2), etc. — no separate check needed). For MA processes, invertibility is checked via the characteristic equation of the MA polynomial: 1+b1z+b2z²+…+bpz^p=0; invertible if all roots have |z|>1. Worked MA(1) invertibility derivation shows how, if invertible, an MA(1) can be rewritten as an infinite AR representation (geometric series expansion using the lag operator L): et = Yt+Yt·θ1L+Yt·θ1²L²+… = Yt+θ1Yt-1+θ1²Yt-2+….
- **Wold's Theorem / General Linear Process**: gives the template for *any* covariance-stationary process — Yt = b(L)et, b(L)=b0+b1L+b2L²+…+bpL^p, with conditions b0=1 and Σbᵢ²<∞ (ensures finite variance). "General" = any covariance-stationary process can be written this form; "Linear" = it expresses the series as a linear function of its innovations (shocks). Since infinite-distributed-lag models aren't practically usable (infinite parameters), ARMA models are fit instead as **parsimonious rational approximations** to the Wold representation.

### 12.6 Conditional vs. Unconditional Mean and Variance (Very Important — flagged repeatedly in the notes)
- **AR(1)** — Unconditional mean μ = b0/(1−b1); Unconditional variance σ²_Yt = σ²/(1−b1²); Conditional mean E(Yt|Yt-1) = b0+b1Yt-1; Conditional variance = σ² (just the innovation variance).
- **MA(1)** — Unconditional mean = b0; Unconditional variance = σ²(1+b1²); Conditional mean E(Yt|et-1) = b0+b1et-1; Conditional variance = σ².
- **Mean-reversion vs. persistence interpretation**: rewriting AR(1) as Yt = μ(1−b1)+b1Yt-1+et, the (1−b1) weight on the unconditional mean is responsible for pulling Yt back toward its long-run mean ("**mean reversion**" weight), while b1 (weight on current level/shocks) is responsible for keeping Yt at its current level ("**persistence**"). b1>0 → persistence; b1<0 → mean reversion.
- **Why study stationarity, invertibility, and Wold's theorem** (explicit Q&A in the notes): Stationarity — only if a series is stationary can you derive a meaningful long-run mean & variance. Invertibility — if an MA series is invertible you can convert it to an AR process and solve it more easily. Wold's theorem — for practical purposes, the AR/MA models actually used are approximations to the Wold representation.

### 12.7 Seasonal ARMA, ARIMA, and Model Selection (AIC/BIC)
- **AR/MA with a seasonal component**: an AR model regresses Yt on its own value in the previous *period*; the seasonal-AR variant regresses Yt on its own value in the previous *season* (PACF significant at seasonal lags instead of ordinary lags). Same logic for seasonal MA via ACF.
- **ARIMA(p,d,q)**: p = AR order, d = order of differencing, q = MA order. **SARIMA** adds a seasonal block: ARIMA(p,d,q)(ps,ds,qs)f, where f = periods per full seasonal cycle (f=12 for monthly data with an annual cycle, f=4 for quarterly data).
- **Model-order/forecast-accuracy selection, 3 tests**: (1) **Forecasting errors** — RMSE or MAPE; (2) **Goodness of fit** — R² and Adjusted R²; (3) **Information criteria** — AIC and BIC. MSE=σ̂²=Σe²/T (disadvantage: promotes larger models, i.e. overfitting risk). **AIC** = T·ln(σ̂²)+2K (constant cost of 2 per parameter). **BIC** = T·ln(σ̂²)+K·ln(T) (cost of an added parameter grows with T). Observations: BIC is stricter — imposes a higher penalty than AIC, especially for T>8; BIC is *consistent* (picks the true model as T→∞); BIC will always exclude irrelevant variables while AIC still has a chance of including them.

### 12.8 Multivariate Time Series — Cross-Correlation, VAR
(From OCR of *8796-VAR.pdf*.) Motivating example: an investor holding a portfolio of 2 stocks, returns r1, r2 observed for t=1…T, wants to forecast r1,T+1 and r2,T+1.
- **Option 1 — individual univariate models** (e.g. two separate AR(1)'s, one per return series): drawback — does not capture cross-effects/cross-correlation between the two series.
- **Solution — VAR(1) (Vector Autoregressive model)**: rt = φ0+φ1·rt-1+at, where rt is (2×1), φ0 is (2×1), φ1 is (2×2), at is (2×1) — i.e. r1,t = φ10+φ11·r1,t-1+φ12·r2,t-1+a1,t and r2,t = φ20+φ21·r1,t-1+φ22·r2,t-1+a2,t (each equation's "own lag" and "cross lag" terms are labeled explicitly in the notes). Off-diagonal φ12≠0 means r1 leads r2 at lag 1; φ21≠0 means r2 leads r1 at lag 1. General form: VAR(p).
- **Weak stationarity & Cross-Correlation Matrices (CCM)**: for a univariate rt, E(rt)=μ (constant), γ(0) (variance, constant), γ(ℓ) (autocovariance at lag ℓ) — all time-invariant under stationarity; ρ(0)=1, ρ(ℓ)=γ(ℓ)/γ(0). For a k-variate rt=[r1t,…,rkt]′: **Mean vector** E[rt]=μ (k×1, constant); **Covariance matrix at lag 0**, Γ(0)=E[(rt−μ)(rt−μ)′] (k×k), with off-diagonal element Γij(0)=Cov(ri,t,rj,t). **CCM**: ρ(0)=D⁻¹Γ(0)D⁻¹, where D is the diagonal matrix of standard deviations (√Γii(0)); this normalizes covariances into correlations. Worked 2×2 case shows explicitly why simply "dividing by variances" doesn't produce a valid correlation matrix without the D matrix construction — Γ(0) and ρ(0) are both symmetric.
- **Lead-lag relationships via CCM at nonzero lags**: ρij(ℓ) = Corr(ri,t, rj,t-ℓ) — computed by shifting one series by ℓ periods before correlating (loses ℓ observations, so the denominator uses (T−ℓ) not T). Key asymmetry: ρij(ℓ) ≠ ρij(−ℓ) in general. If ρij(ℓ)≠0 for some ℓ>0, ri leads rj at lag ℓ; if ρji(ℓ)≠0, rj leads ri at lag ℓ. Relationship: Γij(ℓ) = Cov(ri,t,rj,t-ℓ) = Cov(rj,t-ℓ,ri,t) = Cov(rj,t,ri,t+ℓ) = Γji(−ℓ), i.e. **Γ(ℓ) = Γ(−ℓ)′** (and likewise for ρ).
- **Summary of linear dependence types** (from the diagonal/off-diagonal structure of ρ(ℓ) across lags): (1) no relationship — ρij(ℓ)=ρji(ℓ)=0 for all ℓ≥0; (2) concurrent/contemporaneous relationship — ρij(0)≠0; (3) no lead-lag relationship for ℓ>0 if ρij(ℓ)=ρji(ℓ)=0; (4) unidirectional relationship — if ρij(ℓ)=0 for all ℓ>0 but ρji(ℓ)≠0 for some ℓ>0, rj "leads" / determines a future value of ri; (5) feedback relationship — if for some ℓ, ρij(ℓ)≠0, and for other ℓ, ρji(ℓ)≠0.
- **Estimating the CCM from data**: Step 1 — Γ̂(ℓ) = (1/T)·Σ_{t=ℓ+1}^{T} (rt−r̄)(rt-ℓ−r̄)′, r̄=Σrt/T; Step 2 — ρ̂(ℓ)=D̂⁻¹Γ̂(ℓ)D̂⁻¹.
- **VAR(1) estimation**: each equation (r1,t = φ10+φ11r1,t-1+φ12r2,t-1+a1,t, etc.) is estimated separately by **OLS**; (a1t,a2t)′ ~ N(0,Σ), Σ̂ = (1/(T−2))·Σ(âₜâₜ′) (the residual covariance matrix, i.e. a1,a2's variances σ1²,σ2² and covariance σ12=σ1σ2ρ). **Reduced vs. structural form**: the standard VAR(1) as written is a **reduced form** — it does not explicitly model the *concurrent* relationship between r1,t and r2,t (off-diagonal elements of Σ capture that only implicitly, through correlated residuals, not through an explicit right-hand-side term).
  - **Structural form**: Σ=LGL′ (L = lower triangular, G = diagonal matrix — a Cholesky-style decomposition), transforming the reduced-form residuals at into structural, uncorrelated shocks bt=L⁻¹at with Cov(bt)=G (diagonal). Pre-multiplying the VAR equation by L⁻¹ gives a structural-form system where the concurrent relationship between r1,t and r2,t is made explicit on the right-hand side.
- **VAR(1) stationarity condition**: rewriting as rt−μ = φ1(rt-1−μ)+at defines a **mean-corrected series** r̃t; expanding recursively, r̃t = at+φ1at-1+φ1²at-2+φ1³at-3+… (the VAR(1)↔VMA(∞) analogue of the univariate AR(1)↔MA(∞) relationship). Formal condition: writing (I−φ1B)rt=at, with characteristic polynomial φ(B)=I−φ1B, the **roots of |I−φ1B|=0 must exceed 1 in absolute value**, equivalently the **eigenvalues of φ1 must all be less than 1 in absolute value** (|φ1−λI|=0 gives the eigenvalues). Worked 2×2 numeric example confirms this via direct eigenvalue computation. **VAR(p) generalization**: μ=E(rt)=(I−φ1−φ2−…−φp)⁻¹φ0; Γ(ℓ)=φ1Γ(ℓ−1)+φ2Γ(ℓ−2)+…+φpΓ(ℓ−p) (matrix Yule-Walker recursion); ρ(ℓ)=Ω1ρ(ℓ−1)+Ω2ρ(ℓ−2)+…, where Ωᵢ=D⁻¹φᵢD.

### 12.9 Cointegration and the Vector Error Correction Model (VECM)
(From OCR of *9433-VECM (1).pdf*.)
- **Cointegration definition**: if a linear combination of two I(1) (unit-root non-stationary) series is itself stationary I(0), the series are called **cointegrated**: yt~I(1), xt~I(1), but yt−αxt~I(0). Tested via ADF on the residual of a regression of one series on the other (or via the Johansen procedure below).
- **Common stochastic trend interpretation**: two I(1) series that are cointegrated share a **common stochastic trend** Zt. Formally: xt=γ0+γ1Zt+ϵt (I(1)), yt=δ0+δ1Zt+ηt (I(1)), Zt~I(1); then δ1xt−γ1yt ~ I(0) — the common trend Zt cancels out of the linear combination.
- **Spurious regression**: two independent I(1) series will (i) trend arbitrarily up or down, and (ii) be non-stationary; regressing one on the other produces a misleadingly high R² (→1) even with no real relationship, because both are driven by unrelated stochastic trends that happen to co-move over the sample — classic teaching example: GDP of Kenya vs. India's population, R²→1 despite no causal link. If both series are non-stationary due to a genuinely **common** stochastic trend, however, they visibly "co-move" and R²→1 is *not* spurious in that case.
- **Worked numerical VAR(1)→cointegration example**: x1t, x2t following a VAR(1) with φ1=[[0.5,−1],[−0.25,0.5]] — individually non-stationary (eigenvalues λ=0,1 from |φ1−λI|=0, one unit root). Diagonalizing φ1=PΛP⁻¹ gives a transformed series yt=Lxt=P⁻¹xt with y1t=(1)y1,t-1+η1t ~ I(1) (unit root — "unconditional") and y2t=η2t ~ I(0) (white noise, purely stationary). Back-substituting L=[[1,−2],[0.5,1]] shows y1t=x1t−2x2t ~I(1) (unit root — no cointegration in this combination) while y2t=0.5x1t+x2t ~I(0) (**a stationary linear combination — the cointegrating relationship**), i.e. x1t and x2t are cointegrated via z2t=0.5x1t+x2t.
- **VECM(1) derivation from a VAR(1)**: Δxt = φ1xt-1 − Ixt-1 + et = (φ1−I)xt-1+et; substituting the eigendecomposition, (Δx1t;Δx2t) = π(x1,t-1;x2,t-1)+et where **π = αβ′** is a rank-deficient matrix (rank = number of cointegrating relationships, m): α = adjustment/loading vector (α1;α2) ("speed of mean reversion"), β = cointegrating vector (β1;β2). Worked numeric example gives π=[[−0.5,1],[−0.25,0.5]] with rank 1, decomposed as α=(−0.5;−0.25), β=(1;2)′, confirming the cointegrating equation x1,t-1+2x2,t-1 (equivalently the 0.5x1+x2 relationship above, up to scaling) is I(0) while ΔX is driven by π·xt-1 (the error-correction term) plus noise.
- **Engle-Granger 2-step ECM**: Step 1 — establish the long-run equilibrium relationship yt=α+βxt+ϵt (yt−α−βxt ~ I(0) if cointegrated — a "long-run equilibrium relationship," with the two I(1) series sharing a common stochastic trend so their difference stays I(0), i.e. the series visibly co-move rather than drift apart). Step 2 — the **Error Correction Model**: Δyt = φ0+φ1·Δxt+at, where Δyt, Δxt are first differences (both I(0)), *augmented* with the lagged equilibrium error ϵt-1 = yt-1−α−βxt-1 as an extra regressor: **Δyt = φ0+φ1t+φ1·Δxt−λ(yt-1−α−βxt-1)+et** — λ is the speed-of-adjustment coefficient pulling y back toward its long-run relationship with x whenever it has drifted away.
- **VECM(1) general form**: **Δxt = πxt-1 + Φ1Δxt-1 + et**, where πxt-1 is the "error correction term." Worked numeric example ties the abstract π=αβ′ decomposition to concrete Δx1t, Δx2t equations, each driven by the same cointegrating-equation residual (0.5x1,t-1+x2,t-1) scaled by α1, α2 respectively — labeled "speed [of] mean reversion."
- **Rank of π and the number of cointegrating relationships (m)** — for k variables, π is (k×k):
  - **Case 1: m=0** (π has rank 0 — does not exist / is a zero matrix). πxt-1 vanishes (no error correction term); all k variables are individually I(1) with k unit roots and there is no cointegration — reduces to a plain VAR in first differences (Δx1, Δx2, … — a "difference-stationary" system with no long-run relationship). Eigenvalues of φ1: full rank ⇒ eigenvalues all ≠0 (k×k has k eigenvalues); rank m ⇒ m eigenvalues ≠0, k−m eigenvalues =0.
  - **Case 2: m=k** (π is full rank). Then the levels x1t,x2t,…,xkt are themselves already I(0) (stationary) — Δx1,Δx2,… would then be over-differenced; k−m=0 unit-root series remain to account for, i.e. no cointegration analysis is needed and one would model xt directly as a stationary VAR(1): xt=α+βxt-1+…
  - **Case 3: 0<m<k** — the genuine cointegration case; π=αβ′ where α is (k×m), β′ is (m×k), giving π rank m. Full VECM: **Δxt = φ0+αβ′xt-1+Δxt-1+…+et**.
- **Johansen Test** (sequential procedure to determine m, k=2 example worked through): VECM(1): (Δx1t;Δx2t)=π(x1,t-1;x2,t-1)+Δxt-1+et, using the **Trace statistic** and **Maximum Eigenvalue statistic**. Sequential testing: **Stage 1** — H0: m=0 (no cointegrating equation) vs. H1: m>0 (m∈{1,2}); if the null is *not* rejected, stop — model Δx1,Δx2 as a plain VAR in differences (no CE); if rejected, proceed. **Stage 2** — H0: m≤1 (at most 1) vs. H1: m>1 (m=2); if the null is *not* rejected, rank=1 (one cointegrating relationship — proceed with a rank-1 VECM); if rejected, rank=2 (both variables are individually stationary — π is full rank; regress levels directly: xt=φ0+[φ11,φ12;φ21,φ22]xt-1+et, i.e. a standard stationary VAR in levels, since π=αβ′ with α,β both full k×k in this boundary case).

---

## 13. Data Preparation & Classification-Model Pipeline — the DPMENTOS Framework

Reconstructed via OCR of `Module 1 Hand written notes.pdf` (20 pages) — the fullest, most systematic treatment of data preparation in the whole folder, and the material that the "MENTOS" mnemonic used throughout §4, §7 and §8 above actually stands for.

### 13.1 Data Types and the Regression vs. Classification Split
- Data collected is either **Structured** (rows/columns) or **Unstructured** (not row/column form — generated at high speed/volume, a.k.a. "Big Data"). Structured data is further split into **Time Series** (one observational unit over a period of time, e.g. one stock's price over 365 days), **Cross-Sectional** (multiple observational units at one point in time, e.g. many stocks' prices on one Friday), and **Panel Data** (multiple units across multiple time points — a mixture of the two). Whatever is collected has two variable types: **Numerical** (Discrete — countable, e.g. loan age vs. Continuous — uncountable/any value, e.g. loan amount) and **Categorical** (2-category e.g. Default/No-Default, or Multiple-category, which splits into **Nominal** — no order, e.g. home-ownership Rent/Mortgaged/Own/None — vs. **Ordinal** — has order, e.g. Income Category Low/Medium/High or Loan Grade A/B/C/D).
- Worked example classifies 10 typical loan-model fields by type (Employment length → numerical discrete; Loan amount → numerical continuous; Home ownership → categorical nominal; Income category → categorical ordinal; Loan term → numerical discrete; Income amount → numerical continuous; Loan purpose → categorical nominal; Loan grade → categorical ordinal; Loan status (good/bad) → categorical, 2-category; Loan interest rate → numerical continuous).
- **Supervised learning definition in this context**: Loan Status = fn(Employment length, Income, Home Ownership, Loan amount, Loan term, Loan purpose) — Y = the response/target/explained/dependent variable, the X's = features/independent/explanatory variables. If Y is available, it's supervised learning, splitting into: **Classification model** (Y is a class/category, e.g. Loan Status = good/bad) vs. **Regression model** (Y is numeric, e.g. Interest Rate). The pipeline/steps for both models are ~75% similar; Classification models have more steps than Regression models, but data preparation is a common first step for both.

### 13.2 The DPMENTOS Pipeline (Data Preparation with MENTOS approach)
**Overall regression pipeline**: Data Preparation → Variable Selection → Model Building → Model Evaluation.
**Data preparation with the MENTOS approach, spelled out step by step** (each letter = one step):
- **D** — **Data Analysis / Exploratory Data Analysis (EDA)**. Three things done in EDA: (1) **Descriptive statistics** — summarize data with Mean, Median, Mode, Variance, Skewness, Kurtosis; (2) **Visualization** — two chart types: **Histogram** (bins income/whatever variable into frequency ranges, e.g. 1000-2000/2000-3000/…; tells you Range (min-max), Average/central tendency, Deviation, and Distribution shape — Normal vs. Skewed; if skewed, a Normal Transformation step converts it toward Normal) and **Box Plot** (represents the data above the zero scale at median level; box starts at Q1 (25th percentile, "first quartile") and ends at Q3 (75th percentile), area between Q3−Q1 = **IQR**, Inter-Quartile Range; **Upper boundary = Q3+1.5×IQR**, **Lower boundary = Q1−1.5×IQR**; the region between box edge and boundary = **Whiskers**; anything beyond the boundary = **Outliers**); (3) **Count check** — Missing Count (% missing = "Missing Rate," ideally below ~5%; complement = "Fill Rate") and **Cardinality** (count of distinct labels in a categorical variable; low cardinality is generally accepted, high cardinality is generally removed since it doesn't provide good results, though it can be retained if the labels create meaningful segmentation).
- **P** — **Partitioning** (of data). The dataset is split 3 ways: **60% Training** (learning data), **20% Validation** (used for best-model selection and model tuning), **20% Testing** (must be purely "virgin"/unused data, kept aside for final performance evaluation). Analogy: Training = net practice in the nets; Validation = the coach arranging an inter-squad match to pick the team/tune players; Testing = the real match (no data leakage — the pitch/opponent is genuinely new). **Two data-leakage rules**: (1) knowledge of Test-set records must never be used to train the model; (2) the entire data-preparation *intelligence* (e.g. binning cutoffs, imputation values) should be built purely on Training data, since Validation and Test data "cannot be seen" by that intelligence.
  - **Model selection pitfall and K-Fold Cross-Validation**: naively training several candidate models (e.g. M1(x1,x3,x5), M2(x2,x3,x6), M3(x1,x4,x6)) and picking whichever scores highest on a single validation split (e.g. M2 at 89%) is a **flawed procedure** — that split may have been "good luck" for M2, which could then fail on the actual test set; the fix is **K-Fold Cross-Validation**. Worked 5-fold example on 100 datapoints, 80 used for training+validation (20 held out for testing, untouched): each fold trains on 64 points and validates on a rotating 16-point block (5 folds × 16 = 80); each fold produces one score, and the model's overall score = **Average Score = (Score1+Score2+Score3+Score4+Score5)/5**. In the worked candidate-model example, this flips the naive result: M2 (89% single-split) actually only scores 87% under Avg K-fold CV, while M1 scores 91% under K-fold CV despite only 82% on the naive single split — **K-fold CV is used for (1) Model Selection, (2) Tuning, and (3) Model Selection + Tuning combined (via Nested Cross-Validation — first select the candidate architecture, then tune it)**. **Overfitting flag**: if a model performs well on Validation but poorly on Test, that is called **Overfitting** (Validation ✓, Testing ✗ ⇒ Overfitting).
- **M** — **Missing Value Imputation** (filling data where it's missing). If any explanatory variable (x1, x2, x3, …) has missing data, no model can be built on it directly, so missing values must be imputed or filled. There are **8 techniques**, chosen based on the **nature of missingness** — 3 types: **MCAR** (Missing Completely At Random — no pattern in the missing values at all, e.g. x1 missing purely at random unrelated to x2 or any other variable); **MAR** (Missing At Random — "at random" is a misleading label, since there IS a pattern, but the pattern is explained by an *observed* variable, e.g. age (x2) missing more often for older females — the pattern is explained by observed x1=gender); **MNAR** (Missing Not At Random — the pattern is explained by the *unobserved variable itself*, e.g. weight data missing specifically for overweight people out of embarrassment — the reason for missingness is bound up in the very value that's missing). **Cross-reference table** (Observed Value / Unknown Value columns, checkmark = pattern present): MCAR → ✗/✗ (no pattern either way); MAR → ✓/✗ (pattern explained by observed data only); MNAR → ✓/✓ (pattern present in both — genuinely tied to the unobserved value itself).
  - **The 8 imputation techniques, mapped to the MCAR/MAR/MNAR type each is valid for**:
    1. **Listwise Deletion** ("Complete Case Analysis") — delete the entire *row* (not column) if any variable's value is missing for that row. → valid for **MCAR**.
    2. **Mean & Median Imputation** — fill missing values with the average of existing values; use **Mean** if the variable follows a Normal Distribution, **Median** if it follows a non-Normal/skewed distribution (because in skewed distributions, the mean is affected by outliers). → **MCAR**.
    3. **Random Sample Imputation** — if the variable follows N(μ,σ), impute by random draws via simulation. → **MCAR**.
    4. **Regression Imputation** — plot the variable with missing values (x1) against a related variable (x2), find the best-fit line on **complete cases only** (x1 = b0+b1·x2), then use that line to impute x1 wherever x2 is known but x1 is missing. → **MAR**.
    5. **KNN (K-Nearest Neighbour) Imputation** — similar setup to regression imputation but non-parametric: delete rows where the predictor variables (x2, x3) are missing, plot the complete cases, and for a record whose x1 is missing, find the K (e.g. 3 or 4) nearest neighbors based on x2, x3 and impute x1 as the average of those neighbors' x1 values. → **MAR**.
    6. **Missing Indicator Approach** — create a new dummy variable and replace the missing value with 0. Worked example: Job Status (Student/Businessman/Salaried) and No. of years of Employment (which is N/A for students and businessmen but has a real value for salaried people) — because of the first variable, the second variable's missingness pattern is explained, so it is MAR. Create (number of classes − 1) dummy variables — here 3 classes ⇒ 2 dummies (S, B): Student→S=1,B=0; Businessman→S=0,B=1; Salaried→S=0,B=0 (both zero implies Salaried by elimination — no third dummy needed); then impute the missing "years of employment" with 0 for Student/Businessman rows, since the flags already carry the information. → **MAR**.
    7. **Arbitrary Value Imputation** — impute with an arbitrary value that is directionally consistent with *why* the value is missing. Example: FICO score field left blank by applicants specifically because their score is low ⇒ this is **MNAR** (the missingness reason IS the variable), so impute with a deliberately *low* arbitrary value; conversely if an income field is blank because income is high, impute with a *high* arbitrary value.
    8. **Tail Value Imputation** — if observed FICO scores range 300–800, impute missing values with the relevant tail value (e.g. 300, if the applicant likely left it blank due to a low score). → **MNAR**.
  - **Worked worst-case scenario / intuition-building example**: for a "how is interest rate compounded" question missing in 10 out of 100 loan-application questions, several fallback strategies are given as illustrations of the imputation logic rather than a fixed rule: assume any reasonable method (continuous/semi-annual/yearly) and solve — "**Arbitrary Value Imputation**"; skip those questions entirely (no value) — "**Listwise Deletion**"; observe what method was used in most of the other questions — "**Mean/Median/Mode Imputation**"; go for Bonds as semi-annual and Derivatives as continuous based on the observation in the rest of the questions — "**Regression/KNN Imputation**"; flag those questions and decide the method later after seeing the answer — "**Missing Indicator Imputation**." A summary table maps: Listwise Deletion→MCAR; Mean/Median Imputation→MCAR; Random Sample Imputation→MCAR; Regression→MAR; KNN→MAR; Missing Indicator→MAR; Arbitrary Value→MNAR; Tail Value→MNAR. Note: identifying whether a variable is MCAR, MAR, or MNAR is **subjective** and requires detailed analysis of each variable.
- **E** — **Encoding** (converting categorical data to numbers, since models only understand numbers). Two concepts: **Type of Categorical Variable** (Nominal — without order, vs. Ordinal — with order) and **Cardinality** (count of labels in a categorical variable; high cardinality should generally be removed as it doesn't provide good results). **Three encoding method families**: **Flagging-based** (One-Hot Encoding; One-Hot Encoding with Rare Labels); **Based on X** (Frequency Encoding; Ordinal/Integer/Label Encoding); **Based on Y** (Mean Encoding a.k.a. Target-Guided Encoding — considered the best method).
  1. **One-Hot Encoding** — converts a categorical variable with n classes into (n−1) binary variables (e.g. Student/Businessman → 2 binary columns).
  2. **Frequency Encoding** — replace each category with its count/frequency in the data. Drawback: if two categories happen to have the same frequency, the encoding can't distinguish them (they'll be treated as the same), so this is used only cautiously.
  3. **Ordinal Encoding** — labels that have order (A<B<C<D) are mapped to sequential integers (1,2,3,4); the problem is the *distance* between categories can't be asserted this way — you can't say "how much better" A is than B just from the integers 1 vs 2.
  4. **Mean Encoding / Target-Guided Encoding** ("Best Method") — for rating grades A,B,C,D,E, take the average value of the target (e.g. Interest Rate) for all rows within each grade, and replace the grade label with that average — directly encodes the actual relationship with Y, and preserves monotonicity/ordering meaningfully.
  5. **One-Hot Encoding with Rare Labels** — first bucket rare categories together (e.g. any category below a frequency threshold like 5% gets grouped into "Rare"), then apply one-hot encoding, avoiding an explosion of near-empty dummy columns.
  - **Which to use, when** (decision table in the notes): One-Hot Encoding → use in Low Cardinality; One-Hot with Rare Labels → use in case of Uniform Frequency; Frequency Encoding → use in Low Cardinality after Rare Labels are grouped; Ordinal Encoding → use in Ordinal Variables; Mean Encoding → Best (preserves monotonicity).
  - **Classification-model-specific encoding: Discretization + Weight of Evidence (WOE)**. A linear model can only be fit if X is **monotonic** with respect to Y — irrespective of Regression vs. Classification. When the true relationship between X and Y is **non-monotonic**, the fix is **Discretization + Categorical Encoding**: transform a continuous X into categories (bins) via Discretization, then convert those bins back to numbers via categorical encoding (this lets the classification-model pipeline *bypass* the rest of MENTOS entirely once Discretization is applied, since discretized/encoded bins no longer need missing-value imputation, normal transformation, outlier treatment, or scaling the way raw continuous variables do). Bins can be created as **Equal Width** or **Equal Frequency**. Worked WOE example (Age binned into ≤25 / 26-30 / >30, with Good/Bad counts per bin): **WOE = ln(%Bad/%Good)** (or equivalently ln(%Good/%Bad) — sign flips but conclusions are the same). Worked results: ≤25 → WOE=0 (%Bad=%Good=0.5, no explanatory power — the bin doesn't help distinguish default from non-default); 26-30 → WOE=ln(0.25/0.125)=0.693; >30 → WOE=ln(0.25/0.375)=−0.405. **WOE interpretation**: a WOE of 0 means the bin has zero explanatory power (probability of default = probability of non-default in that bin, so it can't help predict PD); the magnitude of WOE (irrespective of sign) reflects how much explanatory power the bin has. WOE is typically used when there are exactly two target categories ("Good"/"Bad", "0"/"1", etc.).
  - **Information Value (IV)**: naively summing a variable's per-bin WOEs to get "total explanatory power" is wrong, because +/− signs can cancel and understate the true explanatory power; instead **IV = Σ [(%Bad − %Good) × WOE]** per bin, summed across all bins of the variable. Worked continuation of the Age example: ≤25 → (0.5−0.5)×0=0; 26-30 → (0.25−0.125)×0.693=0.0866; >30 → (0.25−0.375)×(−0.405)=0.0507; **Total IV for "Age" = 0.1373**. **IV interpretation table**: <0.02 → Useless; 0.02–0.1 → Weak predictor; 0.1–0.3 → Medium predictor; 0.3–0.5 → Strong predictor; >0.5 → Suspicious (usually rejected in modeling — too strong to be trustworthy, may signal leakage). Rule of thumb: strong or medium predictors are usually accepted.
  - **How to create bins — the SIMPLE mnemonic**: **S** — Similar bins grouping (should be done — merge bins with similar WOE); **I** — IV optimized (bins should be chosen to maximize the variable's IV); **M** — Monotonic trend (WOE should trend monotonically across bins — should be present); **P** — Problems in Data (should NOT be present — e.g. one bin with near-zero population); **L** — Large size (each bin should have a large-enough population, should be present); **E** — Errors (should NOT be present).
  - **Pros/Cons of the Discretization+WOE approach**: Pro — builds a simple model using simple methods; Con — loses information, since converting numbers into categories/groups discards granularity. Despite the con, this approach's benefits outweigh its drawbacks in practice, which is why it's industry-standard — companies like FICO and CIBIL use exactly this approach (Discretization + WOE) when building scorecards. **In Regression models, only Target Mean Encoding is used; in Classification models, either Target Mean Encoding or Weight of Evidence (WOE) can be used** — WOE is heavily used specifically in credit-scorecard building.
- **N** — **Normal Transformation** (transforming variables toward a Normal Distribution). Transformation functions: **Box-Cox Transformation** — X^λ formula (λ tuned via MLE), works only for **positive values of X** (a key shortcoming); **Yeo-Johnson Transformation** — accommodates negative values of X as well (an extension of Box-Cox). Box-Cox's λ maps to named special cases: λ=2→Square; λ=0.5→(unlabeled, between square and no-transform); λ=1→No transformation; λ=0→Logarithmic (ln(x)); λ=−0.5→Inverse Square Root (1/√x); λ=−1→Inverse (1/x). **Why do transformation**: (1) it's an assumption/requirement of certain models — X has to be converted to Normal, and even Y can be converted to Normal; (2) it can improve model accuracy.
- **T/O** — **Outlier Engineering / Treatment**. Illustrative caution: when relating income to years of education, people with a shorter education duration who earn *less* aren't necessarily outliers if there's a real, explainable pattern; but if you consider examples like Bill Gates or Steve Jobs (very high income despite dropping out early), those points genuinely are outliers and should be kept separate from the general model / treated distinctly. **Two treatment methods**: **Trimming** (simply exclude the outliers) and **Winsorizing / Capping** (cap and floor the outliers to some non-outlier value). **Sigma-based capping** ("Six Sigma" technique) — e.g. mean=80, σ=10: cap = mean+3σ = 110, floor = mean−3σ = 50; **this technique is considered a BAD technique in industry**, because σ itself is impacted by the outliers you're trying to treat (circular). **Box-Plot-based capping** (preferred) — Upper Boundary (U.B.) = Q3+1.5×IQR (values above are capped to this upper boundary); Lower Boundary (L.B.) = Q1−1.5×IQR (values below are floored to this lower boundary). **QQ Plot** — another outlier-detection technique (visual check of empirical vs. theoretical quantiles); a common convention is to cap outliers within the 99th percentile and floor within the 1st percentile. **When to use which method**: if outliers are genuine (not measurement/data-entry errors) — do NOT trim, keep them in the model, and Winsorize if the model requires a no-outlier assumption (e.g. linear regression can throw wrong output if untamed outliers remain — "may throw wrong output"); if outliers are noise (measurement errors, typing mistakes) — trim them if sufficient data remains, or Winsorize if the amount of noisy data is low (can't afford to lose the rows).
- **S** — **Scaling** (resetting the ranges of values so different variables become comparable). Motivating example: explaining "Weight Lost" via "Gymming hours/day" (range 2–4 hrs) and "Protein intake/day" (range 75–100 gms) — very different native scales. If unscaled, the fitted regression coefficients (β_Gym, β_Protein) become **not comparable**: because Protein's scale is numerically large, its coefficient must be multiplied by a smaller number to map onto the Weight-Lost scale (making β_Protein look artificially "low"), while Gym's coefficient, on a small native scale, must be multiplied by a larger number (making β_Gym look artificially "high") — this can wrongly suggest Gymming matters more than Protein intake per day, when the apparent difference is really just an artifact of unequal scales; if coefficients aren't scaled, they simply aren't comparable to each other. **Four scaling methods, formulas and z-score output range**: **Standardization** — (X−μ)/σ, Z-score range −∞ to +∞ (mean and σ/standard deviation are impacted by outliers); **Robust Scaling** — (X−Median)/IQR, Z-score range −∞ to +∞ (median and IQR are robust against outliers — the recommended method when outliers are present); **Min-Max Scaling** — (X−Min)/(Max−Min), Z-score range strictly 0 to 1; **Mean Normalization** — (X−μ)/(Max−Min), Z-score range −1 to +1. **Key caveat repeated in the notes**: any method can be used, but you must remember that if outliers are present in the data (i.e. the distribution is skewed), you should NOT use Standardization, since it is affected by outliers — prefer Robust Scaling in that case.
- Note explicitly stated: "**Data Preparation for the Pipeline of Regression and Classification Models is the same. However, other steps in the Classification Model differ from the Regression Model**" (the Discretization+WOE branch above is the classification-specific fork).

### 13.3 Variable Selection and Model-Building Stages (context for the DPMENTOS pipeline)
- After Data Preparation, if a large number of features remain, model complexity/weight becomes a problem, so **Variable Selection** narrows down to the few important/crucial variables via the **FEW** mnemonic: **F** — Filter Methods (Basic, Statistical); **E** — Embedded Methods; **W** — Wrapper Methods (cross-referenced to the fuller treatment already in §4.4 above).
- After selecting a few variables, the model is built to give the best **TRP**: **B** — Build the model; **T**/**R**/**P** — Tuning and Refinement, then Performance Evaluation.

---

## 14. Files That Are Primarily Image/Diagram-Based (Low Extractable Text)

**Update (second extraction pass):** the 29 files below were originally flagged here as image/diagram-heavy with minimal machine-readable text. They have since been deeply re-processed using an OCR/vision-based pipeline (each PDF rasterized page-by-page, tiled into contact-sheet images, and transcribed via visual reading rather than text extraction), and their full content has now been merged into the topical sections above. Pointers to where each file's content landed:

| File | Now covered in |
|---|---|
| `Module 1 Hand written notes.pdf` | §13 (entire DPMENTOS data-preparation & classification pipeline) |
| `1466-PD_Mindmap.pdf`, `4381-CECL.pdf` | §9 (IFRS 9/CECL) — **note: `4381-CECL.pdf` duplicates the content of `1466-PD_Mindmap.pdf`**, both being PD/mind-map style overviews reused across modules |
| `4609-Behavioral Variates.pdf` | §4.7a–4.7b (behavioral scorecard variable construction, Master Rating Scale design/validation, worked WCDR/capital example) |
| `5298-ML-Quants.pdf` | §10.1–10.8 (statistics/ML branch map, LDA, SVM, KNN, Neural Networks, gradient descent, ROC/precision-recall, ensemble learning) |
| `7184-Basel PD model.pdf` | §8.1 (three Basel-family regulations, WCDR formula variants, Basel-specific PD 6P framework) |
| `8663-LGD EAD.pdf` | §7.1–7.2 (LGD and EAD/CCF full 6P frameworks, chain-ladder extrapolation, cooling-off analysis, worked CCF example) |
| `8220-2. Discrete Time non parametric estimation (KM).pdf`, `9102-Survival Analysis.pdf` | §11.1–11.5 (hazard/survival math, Kaplan-Meier estimator & likelihood, parametric/Weibull estimation, Cox PH & partial likelihood, AFT models) |
| `7728-1.8 Time Series.pdf` | §12.1–12.7 (trend/seasonality/stationarity, ADF test, ACF/PACF, AR/MA/ARMA derivations, stationarity/invertibility, Wold's theorem, ARIMA/SARIMA, AIC/BIC) |
| `8796-VAR.pdf` | §12.8 (cross-correlation matrices, VAR(1)/VAR(p), reduced vs. structural form, VAR stationarity via eigenvalues) — note: despite the filename, this deck is about the **Vector Autoregressive (VAR) model**, not Value-at-Risk |
| `9433-VECM (1).pdf` | §12.9 (cointegration, common stochastic trends, spurious regression, VECM derivation, rank of π / Johansen test) |
| `1152-1.7 Regression F.pdf`, `1438-Sample moments_2.pdf` | Referenced as the OLS/regression-theory foundation underlying §4.2 and §12; largely slide-based worked statistics exercises without additional conceptual content beyond what's captured in §4.2's CATEGORICAL mnemonic |
| `3679-Credit Risk 3.2.pdf`, `2828-Cr risk.pdf`, `2704-Credit Risk 4.pdf`, `3242-Credit Risk 5.pdf` | General credit-risk course slides; `2704-Credit Risk 4.pdf`'s CHAMPION mnemonic and `3242-Credit Risk 5.pdf`'s transition-matrix examples remain captured conceptually in §9.4/§11 (see mnemonic reproduced below) |
| `1723-LGD Regression.pdf`, `4827-LGD Secured.pdf`, `5997-LGD Modelling.pdf` | §7 and §7.1 (LGD modeling approaches, GLM/Beta regression, workout method) |
| `7778-LDP.pdf` | §7 (Low Default Portfolio correlation-matrix example, LDP vs. RP segmentation) |
| `2360-Vintage & Roll rate analysis.pdf` | §4.1 (roll-rate and vintage analysis mechanics) |
| `7677-Unsup Learning.pdf`, `3143-Machine Learning Part 3.pdf` | §10 (unsupervised learning / PCA, general ML toolkit) |
| `8472-APC.pdf` | §4.1 (Account Performance Curve, a vintage-analysis variant) |
| `4686-IFRS 9 basics.pdf` | §9.1–9.2 (IFRS 9 staging framework, SMARTEST mnemonic) |
| `1184-Behavioral Scorecar(Mortgage).pdf` | §4.7 (behavioral scorecards for mortgage products specifically) |
| `8096-vecm 4.pdf` | §12.9 (supplementary VECM worked material) |
| `5266-Model Validation.pdf` | §5 (model validation & discriminatory power) |

Two mnemonics/notes worth preserving verbatim:
- **From *Basel PD model***: in the Basel asset-correlation formula, if you're given the correlation *between loans* (ρ), you need √ρ to get the correlation between a loan and the *market* factor for use in the single-factor model; if you're given the loan-to-market correlation directly, use it as-is without transformation (see the full WCDR formula variants in §8.1).
- **From *Credit Risk 4* (CHAMPION mnemonic for model selection)**:
  - **C**HAMPION — drop all other candidate models and choose the best one
  - **D** — Data stationarity & best possible model
  - **R** — Regression output checking
  - **O** — Outcome analysis
  - **P** — Projections

No files in the folder remain unprocessed as of this update — every PDF and both extraction passes (native text + OCR/vision) have been merged into the sections above.

---

## 15. Underlying Case-Study Workbooks (Not Text-Extracted — Excel Files)

- `1.Raw Data..xlsm` (22.5 MB)
- `2.ST_Bucket0.xlsm` (26.3 MB)
- `5.ST_Bucket3.xlsm` (0.8 MB)

These are the live Excel case studies referenced throughout the Module 1–10 curriculum (raw loan-level data and stress-testing bucket examples). They contain macros (`.xlsm`) and formula-driven worked examples (e.g., the scorecard build, roll-rate/vintage calculations, and calibration worked examples referenced in the slides) — best explored directly in Excel rather than as flat text, since their value is in the live formulas and pivot structures.

---

## 16. Quick-Reference Glossary of Recurring Acronyms

| Acronym | Meaning |
|---|---|
| PD / LGD / EAD | Probability of Default / Loss Given Default / Exposure at Default |
| CCF | Credit Conversion Factor |
| TTC / PIT | Through-the-Cycle / Point-in-Time (rating philosophies) |
| WoE | Weight of Evidence |
| IV | Information Value |
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
| VECM | Vector Error Correction Model |
| SR 11-7 | US Fed/OCC Supervisory Guidance on Model Risk Management |
| SS1/23 | PRA (UK) Model Risk Management Principles |
| MRM | Model Risk Management |
| LoD1/2/3 | First/Second/Third Line of Defense |
| MRS | Master Rating Scale |
| WCDR | Worst Case Default Rate |
| DLGD / ELGD | Downturn LGD / Expected (average) LGD |
| MENTOS / DPMENTOS | Mnemonics for the data-preparation pipeline: Data analysis, Partitioning, Missing-value imputation, Encoding, Normal transformation, Outlier treatment, Scaling (§13) |
| WOE / IV | Weight of Evidence / Information Value |
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
| ROC / KS / TPR / FPR | Receiver Operating Characteristic / Kolmogorov-Smirnov / True & False Positive Rate |

---

*Source: all 60 files (57 PDFs + 3 Excel workbooks) in `Peaks 2 tails`, processed in two passes — native text extraction, then (2026-08-29, second pass) OCR/vision-based transcription of the 29 image- and handwriting-heavy PDFs that the first pass could not read (see §14 for the file-by-file mapping of where that content landed). All 57 PDFs have now been substantively incorporated; only the 3 Excel workbooks (§15) remain unprocessed as flat text, since their value is in live formulas rather than static content.*
