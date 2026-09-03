# Credit Risk Portfolio — Phase 0 (Lending Club EDA) — Project Context

This file is auto-loaded by Claude Code at session start. It exists so a new
session (VS Code extension, CLI, or otherwise) has the same standing rules
and current state as the Cowork session that has been driving this project.

## Purpose of this repo (read this first)

This is a **public-facing portfolio project** demonstrating credit risk
modeling skills — built to show to employers/recruiters, not just a private
learning exercise. The user (Devesh) completed a 60-deck credit risk
modeling course ("Peaks2Tails" / "Integrated Credit Risk Modelling in
Banks," instructor Karan Aggarwal) covering scorecard PD modeling,
IFRS 9/CECL ECL computation, Basel RWA/capital, LGD/EAD/CCF modeling, model
validation, and stress testing. This repo is where that course material
gets applied end-to-end against a real, public dataset (Lending Club
accepted loans, 2007-2018) to produce a portfolio-quality body of work.

**A full knowledge base distilled from the entire course is checked in at
`docs/Peaks2Tails_Knowledge_Base.md`.** Read it before doing any modeling
work (PD, LGD, EAD, IFRS 9 ECL, segmentation, validation, etc.) — it's the
source of truth for terminology, required methodology, and the definitions
this project must follow (e.g. default definitions per model type,
performance-window conventions, the CATEGORICAL/DPMENTOS validation
frameworks, segmentation rules). Its table of contents:

1. Course Map / How the Material Fits Together
2. Foundations: Why Credit Risk Modeling Works the Way It Does
3. Data Design & Preparation
4. PD Modeling — Scorecards
5. Model Validation & Discriminatory Power
6. Calibration & Margin of Conservatism (MoC)
7. LGD, EAD & CCF Modeling
8. Basel Capital & RWA
9. IFRS 9 / ECL / CECL
10. Machine Learning & Statistical Toolkit Used in Credit Risk
11. Survival Analysis (Time-to-Default Modeling)
12. Macro-Economic / Time Series Modeling
13. Data Preparation & Classification-Model Pipeline (DPMENTOS Framework)
14. Files That Are Primarily Image/Diagram-Based (source PDF map)
15. Underlying Case-Study Workbooks (Excel)
16. Quick-Reference Glossary of Recurring Acronyms

**Why this repo is called "Phase 0":** the current 16-notebook Lending Club
EDA suite is the data-understanding/cleaning foundation only — mapping
roughly to KB §3 (Data Design & Preparation) and §13 (DPMENTOS pipeline).
Later phases (not yet built) are expected to implement the actual modeling
stack from the KB on top of this cleaned data: scorecard/PD modeling (§4),
validation (§5), calibration (§6), LGD/EAD (§7), and IFRS 9 ECL (§9) — so
naming, definitions, and structure decisions made now in Phase 0 should
stay compatible with those later phases rather than being redone.

## What this project is

A 16-notebook Lending Club EDA suite under
`phase0_data_platform/01_lendingclub/notebooks/`:
- `01_ingestion/01_raw_to_interim.ipynb`
- `02_eda/01_data_understanding_structural_profiling.ipynb` through
  `02_eda/14_*.ipynb` (14 EDA notebooks, one dimension each)
- `03_data_cleaning/01_cleaning_and_feature_prep.ipynb`

Shared connection helper: `notebooks/_shared/nb_setup.py` — `connect()`
(read-only) or `create_fresh()` (ingestion only, wipes and rebuilds the
interim DuckDB file).

## Standing rules (non-negotiable, apply to every notebook)

1. **Evidence-in-code.** Every markdown factual/numeric claim must be
   demonstrated by actual code + printed output in the same notebook. Never
   state a number or fact that isn't traceable to a printed value nearby.
2. **Shared connection helper only.** Every notebook must use
   `nb_setup.connect()` (read-only) or `nb_setup.create_fresh()` (ingestion
   notebook only). No ad-hoc `duckdb.connect(...)` calls.
3. **No scope narrowing outside 03_data_cleaning.** EDA notebooks (02-14)
   must never narrow column scope based on an earlier notebook's test result
   or a known modeling outcome. Only `03_data_cleaning` may drop columns, and
   only with explicit justification written out. EDA markdown must never
   presuppose which columns "end up" being used — phrasing like "~27 columns
   eventually retained for modeling" is banned; that's an outcome the
   cleaning notebook decides, not something EDA should imply it already knows.

## Style conventions

- **Executive style.** Bullets and tables, not prose paragraphs. Minimal
  text. Visual flow (cell-map tables, before/after summaries) over narrative
  writing.
- **Forward-looking framing, not spoilers.** Pre-code markdown cells use
  "Answers:" (questions the code will answer) — never "Expect:" with a
  specific number, which implies the result is already known before the code
  runs.
- **Code comments.** Short `#` inline comments describing what the block
  below does. Do not describe what it doesn't do. No narrative print()
  statements as a substitute for markdown.
- **The real EDA principle — apply everywhere, not just where it's been
  done already:** whenever a group of columns has notably high missingness
  or an unusual pattern (e.g. hardship/settlement fields), the markdown must
  actually explain: what the columns mean and what kind of variables they
  are; whether the missingness itself is signal; whether/how they should be
  used in modeling; whether they need further analysis (and if so, which and
  when); how they'd be treated if used; and any other domain detail relevant
  to a modeler picking this up later. This is the actual purpose of the EDA
  exercise — get real information about variables, not just list them. Apply
  this standard to every notebook going forward, not only the ones already
  reworked.

## Additive-layering pattern (used in notebook 2, reusable elsewhere)

When annotating columns beyond the mechanical type split:
- `inferred_type` (numeric / categorical, from cast-success rate) is
  computed once and never overwritten.
- Domain-level tags (`domain_type`: date / time_period / categorical, or
  `is_ambiguous` + override notes) are separate, additive columns layered on
  top — each backed by printed evidence in the same cell, never silently
  replacing the mechanical result.
- Ambiguous-column flagging uses a `FLAGGED_ROWS = [(source, row_number,
  note), ...]` list where `source` disambiguates which preview table
  (numeric vs. categorical) the row number refers to — avoids retyping full
  column names and avoids merged-index confusion.

## Workflow with the user

One notebook at a time: implement changes → show the user the notebook
content in chat → they comment → iterate → user says "go ahead" / "update
the notebook" → sync the file to their machine (and, unless told otherwise,
`git add` + local `git commit`, but **never** `git push` — the user pushes
manually every time, see Git section below).

## Git / push situation (hard constraint, not a bug)

- Local commits work fine from the Cowork sandbox (`device_bash`), with git
  identity `user.name = deveshusg`, `user.email = deveshusg@gmail.com`
  configured locally in this repo's `.git/config`.
- **Pushing to GitHub is categorically impossible from that sandbox** — no
  credential store is reachable there. The user must run
  `git push origin main` themselves after every round of commits.
- The Claude Code VS Code extension (this session, if you're reading this
  from there) runs natively on the user's machine and *does* have real git
  credentials — so from here, `git push` should actually work. Still always
  ask before pushing.

## Current sweep status (as of last Cowork session)

| Notebook | Status |
|---|---|
| `01_ingestion/01_raw_to_interim.ipynb` | Rewritten in executive style, evidence-first. Committed locally (`a289ba4`). **Not yet pushed.** |
| `02_eda/01_data_understanding_structural_profiling.ipynb` | Rewritten (executive style + eyeball/ambiguous-flagging workflow + date/time_period tagging). Latest 23-cell version is on the user's disk but **not yet committed** (user explicitly said "don't commit" for that last delivery — needs their go-ahead before committing). Earlier version committed locally (`e727a2e`), also **not yet pushed**. |
| `02_eda/02_data_quality_integrity.ipynb` through `02_eda/14_*.ipynb`, and `03_data_cleaning/01_cleaning_and_feature_prep.ipynb` | **Not yet reviewed/reworked.** Same one-by-one workflow applies. |

## Known data-understanding findings worth remembering

- `member_id`: 100% null (scrubbed by Lending Club pre-publication) — dead
  weight, not signal.
- `id` and `policy_code` pass the numeric cast-rate test but are actually an
  identifier and a near-constant code respectively — flagged ambiguous, not
  true numeric features.
- `is_bad` is the modeling target column, not a feature — don't flag it as
  miscategorized when it shows up in numeric column scans.
- `hardship_flag` is misleadingly always `'N'` in the windowed (matured
  loans) population — it reflects "currently in an active hardship plan,"
  not historical hardship status. `hardship_type IS NULL` is the field that
  actually reflects whether a loan ever had a hardship event. Verified:
  `hardship_type` not-null → bad_rate 70.5% (n=5,726) vs. null → bad_rate
  20.3% (n=1,190,153).
- `debt_settlement_flag`: Y → bad_rate 100.0% (n=32,337) vs. N → bad_rate
  18.3% (n=1,163,542) — settlement flag is close to definitionally tied to
  "bad," worth being careful about in feature design (potential leakage).
- `sec_app_earliest_cr_line` should carry the `date` domain tag (co-borrower
  credit history start date), same treatment as `earliest_cr_line`.

## Next step

Continue the one-by-one review workflow starting with
`02_eda/02_data_quality_integrity.ipynb`, applying all rules above. When
domain framing is needed for a column group (e.g. hardship fields, roll-rate
questions, anything touching default/performance-window definitions), check
`docs/Peaks2Tails_Knowledge_Base.md` first rather than guessing — it's the
canonical source for how this project defines and treats those concepts.
