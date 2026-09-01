# Phase 0 -- Lending Club

Phase 0 of the Credit Risk Portfolio curriculum: understand and prepare the
Lending Club unsecured-loan dataset before Phase 1 builds on it. This folder
is self-contained -- data and every notebook for this one dataset live here.
(Other Phase 0 datasets follow this same folder shape as numbered siblings
alongside this one -- see the root `README.md`.)

**Status: Phase 0 complete.** Ingestion, all 14 EDA categories, and a
cleaning pass rebuilt from the full EDA's findings are all done. A
depth/sufficiency review of the full EDA suite found 4 gaps (no duplicate
check, no independent leakage re-validation, outlier counts never turned
into a treatment decision, no documented encoding strategy) -- all 4 are now
closed (see "Gap closure" below). Lending Club's Phase 0 output
(`data/03_processed/lendingclub_model_ready.parquet`) is validated and ready
for Phase 1.

## Folder structure

```
01_lendingclub/
  data/
    01_raw/              untouched source file(s), exactly as published
    02_interim/           a persistent DuckDB file: raw data loaded, typed,
                          and the matured/windowed tables every EDA notebook
                          queries directly, read-only
    03_processed/         the final, modeling-ready parquet file -- what
                          Phase 1 actually reads
    04_assets/            every chart and headline table from notebooks/02_eda/,
                          03_data_cleaning/, and 01_ingestion/, saved as
                          standalone files (04_assets/plots/*.png,
                          04_assets/tables/*.csv) -- reusable outside Jupyter,
                          on top of (not instead of) the real output already
                          embedded in each notebook
  notebooks/
    01_ingestion/          raw -> interim (builds data/02_interim/lendingclub.duckdb)
    02_eda/                 14 category notebooks, one per EDA dimension --
                          READ-ONLY against data/02_interim/. No cleaning,
                          imputation, or transformation happens here.
    03_data_cleaning/       the ONLY place the data actually gets cleaned --
                          reads data/02_interim/, writes data/03_processed/
  README.md               this file
```

Not shown above: the build harness that generates these notebooks (executes
every cell for real, captures genuine output) lives only in the environment
that produced them -- it is not part of this delivered folder. Nothing here
depends on it; it's mentioned only so its absence isn't mistaken for
something missing.

No `.py` pipeline scripts exist in this folder -- ingestion, EDA, and
cleaning are all notebooks, so the reasoning and the code that acts on it
live in the same place.

## How to view / understand this Phase 0 dataset

1. **`notebooks/01_ingestion/01_raw_to_interim.ipynb`.** Loads the raw file,
   looks at what's actually in it, and produces
   `data/02_interim/lendingclub.duckdb`. Run this once before opening any
   other notebook -- everything else connects to that file directly rather
   than re-parsing the raw gzip.

2. **Read the `notebooks/02_eda/` notebooks in numeric order.** Each one
   covers one EDA dimension (data understanding, data quality, univariate,
   bivariate/multivariate, pattern/cluster discovery, temporal/spatial,
   target definition, statistical validation, transformation diagnostics,
   population drift, sampling/representativeness, categorical/text,
   causal/quasi-causal reasoning, and governance/synthesis -- 14 categories).
   Every notebook opens with an index cell listing what it covers and what
   to expect; every code cell has a markdown cell before it (what/why/how/
   expected) and one after it (what the real output means and what's next).

3. **`notebooks/02_eda/14_eda_governance_synthesis_reporting.ipynb`** is the
   capstone -- it pulls every other EDA notebook's findings into one place:
   a full feature inventory with IV, what's formally statistically validated
   vs. descriptive, every known caveat, and concrete action items for both
   the cleaning rebuild and Phase 1. Read this one if you only have time for
   one notebook beyond the ingestion step.

4. **`notebooks/03_data_cleaning/01_cleaning_and_feature_prep.ipynb`** is
   where the data actually gets cleaned -- imputation, transforms, feature
   selection -- and every decision in it cites the specific `02_eda/`
   notebook and cell that justified it. Produces
   `data/03_processed/lendingclub_model_ready.parquet`.

Every number and chart in every notebook above is genuine output from
actually executing that cell, not hand-typed -- the harness that does this
lives outside this delivered folder (see the note under "Folder structure"),
so there's nothing further to open here.

## EDA notebook categories (`notebooks/02_eda/`)

| # | Category | Status |
|---|---|---|
| 01 | Data Understanding & Structural Profiling | built |
| 02 | Data Quality & Integrity | built |
| 03 | Univariate, Distributional & Visual Analysis | built |
| 04 | Bivariate & Multivariate Relationships | built |
| 05 | Pattern, Anomaly, Cluster & Latent-Structure Discovery | built |
| 06 | Temporal, Sequential & Spatial Analysis | built |
| 07 | Target, Outcome & Objective-Oriented Analysis | built |
| 08 | Statistical Validation, Inference, Robustness & Sensitivity (incl. formal hypothesis testing) | built |
| 09 | Transformation, Feature Diagnostics & Analytical Preparation | built |
| 10 | Dataset Comparison, Population Drift & Distribution Shift | built |
| 11 | Sampling, Representativeness & Population Analysis | built |
| 12 | Text, Categorical, High-Cardinality & Multimedia Data | built (proportionally short -- this dataset has minimal free-text/multimedia content) |
| 13 | Causal, Quasi-Causal & Mechanism-Oriented Exploration | built |
| 14 | EDA Governance, Intelligence, Synthesis & Reporting | built |

All 14 categories are complete. Depth was matched to the real content each
category has for this dataset -- notebooks with rich material (04, 05, 08,
09, 10, 13) run 15-40+ real-executed cells; notebook 12 stays short because
the dataset genuinely has little free-text or multimedia content to analyze.

## Key findings (from notebook 14's synthesis)

**Feature strength (IV):** `grade` (0.47) and `int_rate` (0.46) are by far
the strongest predictors, followed by `term` and `fico_range_low` (medium
band). Most other retained features fall in the weak band; `purpose`,
`pub_rec`, `delinq_2yrs`, `open_acc`, `revol_bal`, and `total_acc` fall below
the conventional "useful" IV threshold on their own (though several still
passed formal significance testing -- see below).

**What's formally statistically validated (notebook 08):** grade's bad-rate
ordering (pairwise z-tests, all 6 adjacent-grade pairs significant), the
purpose-vs-is_bad association (chi-square, survives Bonferroni correction),
the income gap between good and bad loans (Mann-Whitney U), and the
2013-2017 window choice itself (sensitivity comparison against including
2012 or 2018). The baseline logistic regression's AUC carries a bootstrap
95% CI of [0.695, 0.698].

**Grade and int_rate are near-definitional, not causal (notebook 13):**
`grade` is Lending Club's own risk-model output, not an independent
borrower characteristic -- its predictive power reflects how good LC's own
model already is. `int_rate` tracks grade almost exactly but retains a real
within-grade bad-rate spread (~4.5 points), most likely carrying signal from
`sub_grade` (not in the current feature set). `dti`'s effect survives
stratifying by both grade and income, making it the most plausible
independently-mechanistic feature in the set. `purpose`'s apparent effect
shrinks substantially once grade is held fixed -- largely confounded.

**Population drift (notebook 10):** `int_rate`'s distribution shifted
moderately within the modeling window (PSI 0.140, 2013 vs. 2017), so
origination year carries real signal -- worth considering as a model feature
or validation-split dimension. The windowed population is *not* meaningfully
different from the excluded years on the features checked (PSI well under
0.1), so the window boundary itself doesn't raise a representativeness
concern.

**Multicollinearity and transforms (notebook 09):** `tot_cur_bal` and
`avg_cur_bal` show elevated VIF (redundant information). The blanket log
transform used in the original cleaning pass improved target correlation for
9 of 16 fields, not all 16 -- 7 fields (`acc_open_past_24mths`,
`avg_cur_bal`, `bc_open_to_buy`, `num_actv_rev_tl`, `open_acc`, `revol_bal`,
`tot_cur_bal`) should be reconsidered.

**Pattern/anomaly discovery (notebook 05):** no unsupervised method found a
clean, separable "bad loan" segment -- consistent with credit risk being
genuinely probabilistic. MiniBatchKMeans (full 1.19M rows) found clusters
with bad rates ranging 13.2%-24.8% against a 20.5% population average;
Isolation Forest anomalies had a modestly different bad rate than normal
borrowers. Cluster membership and anomaly score are candidate engineered
features for Phase 1, not a primary modeling strategy on their own.

**Representativeness (notebook 11):** geographic concentration is
population-proportional (HHI 528, unconcentrated), though the smallest
states have single-digit loan counts and should be excluded from any
per-state analysis. Grade G's bad-rate confidence interval is roughly 10x
wider than grade C's, though both remain narrow in absolute terms.

**High-cardinality fields (notebook 12):** `emp_title` (317,489 distinct
values, self-reported free text) is not usable as a feature without real
occupation-taxonomy normalization work. Every other categorical field is
low-cardinality and already covered elsewhere in the suite.

## Cleaning rebuild -- complete

`notebooks/03_data_cleaning/01_cleaning_and_feature_prep.ipynb` has been
fully rebuilt to incorporate every actionable finding from the complete
14-category EDA suite. `data/03_processed/lendingclub_model_ready.parquet`
was regenerated and validated against the rebuilt logic.

| | Original pass (7 EDA notebooks) | Rebuilt (14 EDA notebooks) |
|---|---|---|
| Rows | 1,195,879 | 1,195,879 (unchanged -- same population) |
| Columns | 48 | 42 |
| Numeric features | 20 | 19 (`avg_cur_bal` dropped -- elevated VIF vs. `tot_cur_bal`) |
| Log-transformed fields | 16 | 9 (7 dropped -- didn't improve target correlation, notebook 09) |
| New engineered features | -- | `issue_year` (drift signal, notebook 10), `addr_state_grouped` (small-state handling, notebook 11) |
| Missing values | 0 | 0 |
| Bad rate | 20.5% | 20.5% (unchanged -- confirms the rebuild changed *feature engineering*, not the underlying population) |

Every column-level decision in the rebuilt notebook cites the specific
`02_eda/` notebook and finding that justifies it -- see
`notebooks/03_data_cleaning/01_cleaning_and_feature_prep.ipynb` cell 1 for
the full before/after column list.

## Gap closure -- complete

A depth/sufficiency review asked a narrower question than "is each notebook
deep enough" (already true): does the *combined* output of all 14 EDA
notebooks give the cleaning notebook everything it needs to make defensible
cleaning decisions? It found 4 real gaps, all now closed:

| Gap | Where it's closed | What was done |
|---|---|---|
| No duplicate/uniqueness check anywhere in the suite | `notebooks/02_eda/02_data_quality_integrity.ipynb`, cell 6 | `id` uniqueness checked at every pipeline stage (raw/matured/windowed) plus a full-row duplicate check on `windowed` -- zero duplicates found at every stage |
| The ~40-column leakage drop list was never independently re-validated against the full raw schema | `notebooks/02_eda/02_data_quality_integrity.ipynb`, cell 7 | scanned all 121 dropped columns' correlation with `is_bad`; the extreme-correlation ones are exactly the payment-history/hardship fields the drop list targeted; the 43 in a moderate-correlation band triage almost entirely into post-origination or co-borrower fields (correctly excluded), leaving 15 genuinely unused origination-time fields flagged as Phase 1 feature candidates -- not leakage, not a mistake in the original list |
| Outlier *counts* (notebook 02, cells 3-4) were never turned into a treatment *decision* | `notebooks/02_eda/02_data_quality_integrity.ipynb`, cell 8 (decision) and `notebooks/03_data_cleaning/01_cleaning_and_feature_prep.ipynb`, cells 6-7 (applied) | every retained numeric feature classified as leave-as-is / log-handled / naturally-bounded / dropped / cap-at-1st-99th-percentile; the cleaning notebook now winsorizes the 8 flagged fields for real (~1.5% of rows per field, both tails) |
| Categorical-encoding strategy was never documented | `notebooks/02_eda/14_eda_governance_synthesis_reporting.ipynb`, cell 7 | recorded, per categorical field, the real cardinality and a recommended Phase 1 encoding approach -- the deliberate decision to leave every categorical field unencoded in `03_processed/` (a Phase 1 modeling choice, not a Phase 0 one) is now written down, not just implicit |

`data/03_processed/lendingclub_model_ready.parquet` was regenerated from the
gap-closure rebuild (same 1,195,879 rows x 42 columns, same 20.5% bad rate
-- winsorizing changes values within existing columns, not row count or
column count) and re-validated, now including an `id`-uniqueness check on
the notebook's own final output.

## Standalone assets (`data/04_assets/`)

Every chart and each notebook's headline table also exist as standalone
files, on top of (not instead of) the real output already embedded in every
notebook -- useful for pulling a specific chart or table into a writeup or
slide without opening Jupyter.

- `data/04_assets/plots/*.png` -- 19 charts across the suite (notebooks 03,
  04, 05, 06, 07), one file per chart, named `<notebook>_c<cell>_<slug>.png`.
- `data/04_assets/tables/*.csv` -- 52 tables, one file per headline
  DataFrame each notebook actually prints (the feature-inventory/IV table,
  PSI tables, VIF table, cluster/anomaly summaries, the outlier-decision
  table, etc.), named `<notebook>_<variable_name>.csv`.

**These save calls live directly inside each notebook's own code cells** --
every `plt.savefig(...)` and `df.to_csv(...)` runs as part of the notebook's
normal execution, right after the chart or table it saves, not from a
separate external script. Opening any notebook and reading its cell source
shows exactly how its assets were produced; re-running a notebook end to end
regenerates them for real. Headline tables were saved as CSV rather than into
a second DuckDB database, since every one is small (dozens to low hundreds of
rows) and meant to be opened directly (Excel, a text editor, `pd.read_csv`)
-- a second database would add cross-referencing overhead for no benefit at
this size. `data/02_interim/` stays the only database in this dataset's
folder.

## Key decisions from ingestion (`notebooks/01_ingestion/`)

- **Modeling window: 2013-2017 matured loans only.** Earlier years have too
  little volume to be reliable; 2018 looks artificially safe purely because
  of right-censoring. See `notebooks/01_ingestion/01_raw_to_interim.ipynb`
  and `notebooks/02_eda/06_temporal_sequential_spatial.ipynb`.
- **Target (`is_bad`):** 1 for Charged Off / Default, 0 for Fully Paid.
  Still-open loans (Current, Late, In Grace Period) are excluded entirely,
  not treated as good. See `notebooks/02_eda/07_target_outcome_objective.ipynb`.
- **Missingness:** mostly structural (hardship/settlement fields that only
  populate for loans that hit hardship), not a data-quality problem. One
  exception -- `emp_length`'s ~5.9% missingness is genuinely informative
  (higher bad rate when missing) and gets its own flag rather than a silent
  fill. See `notebooks/02_eda/02_data_quality_integrity.ipynb`.
