# Credit Risk Portfolio — Integrated Credit Risk Modelling

An end-to-end, inside-out build of a bank's credit-risk modelling stack, showcasing the full
"Integrated Credit Risk Modelling in Banks" curriculum: PD scorecards, alternative/challenger
PD approaches (behavioral scorecards, ML models, survival analysis), PIT/TTC calibration and
Margin of Conservatism, Master Rating Scale design, LGD/EAD modelling, Basel capital (RWA/CAR),
IFRS 9 ECL and CECL transition matrices, macro-driven stress testing, and a model governance /
validation layer — built "inside out," each phase wrapping a new capability around the one before it.

## Two segments, one codebase

Two structurally different products are modelled side by side throughout: **mortgage/secured**
(Fannie Mae Single-Family Loan Performance data) and **unsecured** (Lending Club personal loans).
They are never pooled into one model — each phase's code is shared, but every segment gets its
own fitted parameters, its own methodology choices (see `phase0_data_platform/configs/segments.yaml`),
and its own outputs. Phase 6 shows why: segmented models beat a pooled baseline on discriminatory power.

## Phases (inside out)

| Phase | What it builds |
|---|---|
| 0 — Data Platform | Streaming ingestion of large raw files into a partitioned Parquet lake, on a 16GB-RAM laptop, with full reproducibility/traceability |
| 1 — PD Core Model | Application scorecard: roll-rate/vintage analysis, WOE binning, logistic regression, reject inference, validation |
| 2 — Challenger Models | Behavioral scorecard, ML toolkit (LDA/SVM/KNN/Neural Net/ensembles), survival analysis (KM/Cox/AFT) |
| 3 — Calibration & MoC | PIT-to-TTC calibration, representativeness testing, Margin of Conservatism (Type A/B/C) |
| 4 — Ratings & Capital | Master Rating Scale, LGD, EAD/CCF, Basel capital stack (WCDR → RWA → CET1/AT1/T2 → CAR) |
| 5 — IFRS 9 / CECL / Stress | Staging & ECL, CECL transition matrices, VAR/VECM macro models, scenario stress testing |
| 6 — Governance & Dashboard | Three Lines of Defense, SR 11-7-style validation report, segmented-vs-pooled comparison, dashboard |

Each phase folder is self-contained (`README.md`, `notebooks/`, `src/`, `outputs/`, `tests/`) and
depends only on the phases before it — open any phase's README to understand it without reading the rest.

## Cross-cutting conventions

- **Reproducibility & traceability**: every ingestion or modelling run that involves randomness or
  external data writes a run manifest (git commit, config hash, seed, row counts) via
  `phase0_data_platform/lineage/lineage_log.py`. Later phases reuse this utility rather than inventing
  their own logging.
- **Environments**: `dev` / `test` / `prod` / `audit`, defined in `phase0_data_platform/configs/environments.yaml`.
  `test` runs on a small locally-extracted data fixture (not committed to git — see that phase's README);
  `dev` runs on your real downloaded files with a row cap for fast iteration; `prod`/`audit` run on the
  full chosen sample, with `audit` guaranteeing zero sampling/logging shortcuts.
- **Segmentation**: a config-driven fork, not a merged-dataset model feature — see
  `phase0_data_platform/configs/segments.yaml` and that phase's README for why.

## Setup

```
pip install -r requirements.txt
```

Raw data is **not** included or auto-downloaded — see `phase0_data_platform/README.md` for exactly
what to download by hand and where to place it.
