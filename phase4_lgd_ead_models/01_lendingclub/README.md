# Phase 4 -- Lending Club LGD & EAD Models

⚠️ **CRITICAL: This phase is preserved from earlier work but does NOT yet follow correct methodology. These notebooks were built before Phase 1 (PD baseline) and Phase 3 (Calibration & MoC) existed.**

---

## Overview

This folder contains two notebooks for Loss Given Default (LGD) and Exposure at Default (EAD) modeling on Lending Club data:

1. **01_lgd_baseline_model.ipynb** — Logistic regression on loss rate, using origination and loan characteristics
2. **02_ead_analysis_and_sensitivity.ipynb** — EAD estimation by vintage, grade, and prepayment assumptions

**Status**: Preserved as reference; awaiting Phase 3 completion before full rewrite.

---

## Why This Phase Needs Rewriting

### The Problem

These notebooks were built **in isolation**, without proper integration into the credit risk modeling pipeline:

| Issue | Current State | Should Be |
|-------|---|---|
| **Phase 1 integration** | Does not consume PD baseline | Should load Phase 1's PD model and use its grades for segmentation |
| **Phase 3 dependency** | No TTC adjustment, no MoC | Should apply Phase 3's calibrated PD and MoC bounds |
| **Segmentation** | Single pooled model | Should build separate LGD/EAD models per PD grade |
| **Feature alignment** | Uses 31 raw Phase 0 features | Should use Phase 1's selected 15 features + risk grade |
| **Validation** | No back-testing vs Phase 1 | Should validate implied ECL against Phase 1 cohorts |
| **Assumptions** | Standalone assumptions | Should tie to Phase 3's representativeness framework |

### What Happens Next

1. **Phase 3 completion** (not yet done): Establish PIT-to-TTC calibration, MoC framework, representativeness testing
2. **Phase 4 rewrite** (after Phase 3): Notebooks will be rewritten to:
   - Load Phase 1's PD grades and Phase 3's calibrated PD
   - Build segmented LGD/EAD models (one per grade)
   - Apply MoC from Phase 3 to LGD/EAD estimates
   - Validate against Phase 1 cohorts
   - Document all assumptions tied to Phase 3 framework

---

## Preserved Notebooks

### Notebook 01 -- LGD Baseline Model

**Input**: Phase 0 data (matured, defaulted loans), Phase 1 baseline (for reference only)

**Current scope**:
- Population: Loans with 36+ month maturity, observed default (is_bad == 1)
- Target: LGDV = loss_total / funded_amnt (capped at 0-100%)
- Features: 31 Phase 0 columns (includes grade, term, int_rate, amount, etc.)
- Method: Logistic regression (binomial LGD classification) or linear regression
- Output: LGD ~73% mean

**Key issues with current approach**:
- [ ] Does not load Phase 1 PD model or grades
- [ ] Does not segment by Phase 1's risk grades
- [ ] Feature selection not aligned with Phase 1 (should use IV-selected features)
- [ ] No TTC adjustment (Phase 3 not yet available)
- [ ] No MoC applied to LGD estimate
- [ ] Validation does not reference Phase 1 cohorts

**What the rewrite will do**:
1. Load Phase 1 PD model and extract risk grades
2. Build separate LGD models for each grade (or pooled with grade as feature)
3. Use Phase 1's 15 selected features + grade for modeling
4. Apply Phase 3's TTC adjustment to PD assumptions (if used in LGD segmentation)
5. Document MoC assumptions from Phase 3
6. Compare to Phase 1 cohorts: do implied PDs from LGD×PD match observed defaults?

---

### Notebook 02 -- EAD Analysis and Sensitivity

**Input**: Phase 0 data (all loans), Phase 1 baseline (for reference only)

**Current scope**:
- Population: All Phase 0 loans (both defaulted and performing)
- Target: EAD = outstanding_principal at default date (or at observation for non-defaulted)
- Features: Loan amount, term, grade, origination vintage
- Method: Descriptive analysis + sensitivity to prepayment/utilization assumptions
- Output: EAD ~$8.7K mean

**Key issues with current approach**:
- [ ] Does not load Phase 1 PD model or grades
- [ ] No explicit segmentation by Phase 1's risk grades
- [ ] Mixes defaulted and non-defaulted loans without clear population definition
- [ ] Prepayment/utilization assumptions not tied to Phase 3 representativeness framework
- [ ] No back-testing against Phase 1 cohorts
- [ ] Sensitivity analysis not aligned with Phase 3's scenario framework (not yet done)

**What the rewrite will do**:
1. Define two populations:
   - **LGD population**: Matured loans (36+ months) that defaulted (for measuring actual loss)
   - **EAD population**: Current active loans or loans at default date (for measuring exposure)
2. Build separate EAD models by Phase 1's risk grades
3. Use Phase 1's 15 selected features + grade for modeling
4. Apply Phase 3's representativeness assumptions to prepayment/utilization
5. Sensitivity analysis will use Phase 3's scenario framework (once Phase 3 complete)
6. Document assumptions tied to Phase 3 MoC framework

---

## Expected Outputs (Current, Pre-Rewrite)

These are the outputs the preserved notebooks would produce if run as-is:

```
models/
├── lgd_baseline_v1.joblib                     LGD logistic regression model
├── ead_analysis_v1.joblib                     EAD estimation model or summary stats
├── model_card_lgd_v1.json                     LGD model metadata
└── model_card_ead_v1.json                     EAD model metadata

data/04_assets/tables/
├── lgd_coefficients.csv                       Logistic regression coefficients
├── lgd_iv_table.csv                           Information Value for LGD features
├── ead_summary_by_grade.csv                   EAD mean/median by grade
├── ead_summary_by_vintage.csv                 EAD mean/median by origination vintage
└── ead_sensitivity_analysis.csv               EAD under different assumptions
```

**⚠️ WARNING**: These outputs are **not yet validated** against Phase 1 cohorts. Once Phase 3 is complete, all of these will be regenerated using the corrected methodology.

---

## Expected Outputs (Post-Rewrite, After Phase 3)

After Phase 3 completion and Phase 4 rewrite, the new outputs will be:

```
models/
├── lgd_model_grade_[A-G]_v2.joblib           LGD model per grade
├── ead_model_grade_[A-G]_v2.joblib           EAD model per grade
├── model_card_lgd_segmented_v2.json          LGD segmented model metadata
└── model_card_ead_segmented_v2.json          EAD segmented model metadata

data/04_assets/tables/
├── lgd_by_grade_validation.csv               LGD by grade vs Phase 1 cohorts
├── ead_by_grade_summary.csv                  EAD by grade, with MoC adjustments
├── phase4_vs_phase1_cohort_comparison.csv   Implied PD validation (LGD×EAD×PD vs observed)
└── phase4_moc_applied.csv                    MoC bounds applied from Phase 3
```

---

## How to Reproduce (Current Approach — Not Recommended)

**⚠️ These instructions are for reference only. Do NOT run these notebooks as the basis for ECL modeling. Wait for Phase 3 completion and Phase 4 rewrite.**

```bash
# If you must run the current (incorrect) approach:
cd phase4_lgd_ead_models/01_lendingclub/notebooks/

# Ensure Phase 0 data is available
ls ../../phase0_data_platform/01_lendingclub/data/03_processed/lendingclub_model_ready.parquet

# Run LGD notebook (will produce pooled LGD estimate ~73%)
jupyter notebook 01_lgd_baseline_model.ipynb

# Run EAD notebook (will produce pooled EAD estimate ~$8.7K)
jupyter notebook 02_ead_analysis_and_sensitivity.ipynb
```

**Better approach (once Phase 3 is complete)**:
- Wait for Phase 3 (Calibration & MoC) to complete
- Read Phase 3's outputs: calibrated PD, TTC adjustments, MoC framework
- Rewrite Phase 4 notebooks using Phase 3 outputs
- Run rewritten notebooks with proper segmentation and validation

---

## Design Principles (To Be Applied in Rewrite)

1. **Proper population definition**: Clearly separate matured loans (for LGD) from current exposures (for EAD)
2. **Segmentation by risk grade**: Build separate models for each Phase 1 PD grade, not pooled
3. **Feature alignment**: Use Phase 1's 15 selected features + risk grade as the feature set
4. **Phase 3 integration**: Load Phase 3's PD calibration and MoC framework; apply to LGD/EAD
5. **Validation strategy**: For each grade, compare implied PD = LGD × EAD × observed default rate; should align with Phase 1 baseline
6. **Documentation**: Every assumption ties back to Phase 3's representativeness framework and MoC bounds

---

## Known Gaps (To Be Addressed in Rewrite)

| Gap | Current | Will Be Fixed By |
|---|---|---|
| No Phase 1 integration | ❌ | Loading Phase 1 PD model and grades in rewrite |
| No Phase 3 calibration | ❌ | Loading Phase 3's calibrated PD and MoC in rewrite |
| Pooled models only | ❌ | Building segmented models by grade in rewrite |
| Feature misalignment | ❌ | Using Phase 1's selected features + grade in rewrite |
| No Phase 1 cohort validation | ❌ | Adding cohort back-test in rewrite |
| Standalone assumptions | ❌ | Tying all assumptions to Phase 3 framework in rewrite |

---

## Hand-off to Phase 5

Once Phase 4 is properly completed (after Phase 3), it will hand off to Phase 5 (IFRS 9 ECL Provisioning):

- **Phase 1 outputs**: Calibrated PD by grade (from Phase 1 + Phase 3 TTC adjustment)
- **Phase 4 outputs**: Segmented LGD and EAD models by grade, with MoC applied
- **Phase 3 framework**: Representativeness testing, MoC bounds, scenario framework
- **Phase 5 consumes**: PD × LGD × EAD by grade, plus staging logic (Stage 1/2/3) to compute ECL

---

## Next Steps

1. **Phase 3 completion** (Planned): Build calibration & MoC framework
2. **Phase 4 rewrite** (After Phase 3): Notebooks rewritten with proper methodology
3. **Phase 4 outputs regenerated**: New models and tables aligned to Phase 3 framework
4. **Phase 5 built**: ECL provisioning consuming Phase 1, 3, and 4 outputs

---

## References

- **Phase 1 (PD Baseline)**: `../../phase1_pd_modeling/01_lendingclub/README.md`
- **Phase 2 (Challenger Models)**: `../../phase2_challenger_models/01_lendingclub/README.md`
- **Phase 3 (Calibration & MoC)**: `../../phase3_calibration_moc/README.md` [Planned]
- **Course Material**: `../../docs/Peaks2Tails_Knowledge_Base.md`
- **Status**: Preserved; awaiting Phase 3 before rewrite
