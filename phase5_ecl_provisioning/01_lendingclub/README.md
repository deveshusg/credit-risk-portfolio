# Phase 5 -- Lending Club IFRS 9 ECL Provisioning

⚠️ **CRITICAL: This phase is preserved from earlier work but does NOT yet follow correct methodology. These notebooks were built before Phase 1 (PD baseline), Phase 3 (Calibration & MoC), and Phase 4 (LGD/EAD models) were finalized.**

---

## Overview

This folder contains two notebooks for IFRS 9 Expected Credit Loss (ECL) provisioning on Lending Club data:

1. **01_ecl_baseline_and_staging.ipynb** — IFRS 9 staging logic (Stage 1/2/3) and ECL calculation at portfolio level
2. **02_ecl_sensitivity_and_validation.ipynb** — Sensitivity analysis on ECL to PD/LGD/EAD assumptions and validation against observed loss

**Status**: Preserved as reference; awaiting Phase 3 & Phase 4 completion before full rewrite.

---

## Why This Phase Needs Rewriting

### The Problem

These notebooks were built **in isolation**, without proper integration into the credit risk modeling pipeline:

| Issue | Current State | Should Be |
|---|---|---|
| **Phase 1 integration** | Does not consume PD baseline | Should load Phase 1's PD model and use its grades for ECL by grade |
| **Phase 3 dependency** | No TTC adjustment, no MoC | Should apply Phase 3's calibrated PD, TTC adjustment, and MoC bounds to ECL |
| **Phase 4 dependency** | Uses placeholder LGD/EAD | Should load Phase 4's validated segmented LGD/EAD models |
| **Staging logic** | Generic IFRS 9 thresholds | Should use Phase 3's representativeness testing thresholds for Stage 1→2 transitions |
| **ECL by grade** | Pooled portfolio ECL only | Should calculate ECL separately by grade, then aggregate |
| **Validation** | No back-testing vs Phase 1 | Should validate portfolio ECL (as % of AUM) against Phase 1 observed defaults and banking benchmarks |
| **Macro scenarios** | Ad-hoc scenario analysis | Should use Phase 3's scenario framework (once available) |
| **Term structure** | 12-month PD only | Should integrate Phase 2 survival analysis for lifetime PD term structure |

### What Happens Next

1. **Phase 3 completion** (not yet done): Establish PIT-to-TTC calibration, MoC framework, representativeness testing, scenario framework
2. **Phase 4 completion** (after Phase 3): Validated LGD and EAD models by risk grade
3. **Phase 5 rewrite** (after Phase 3 & 4): Notebooks will be rewritten to:
   - Load Phase 1's PD grades and Phase 3's calibrated/TTC-adjusted PD
   - Load Phase 4's validated LGD/EAD by grade
   - Implement staging using Phase 3's thresholds
   - Calculate ECL by grade: Stage 1 (12-month) and Stage 2/3 (lifetime)
   - Apply Phase 3's MoC to ECL estimates
   - Integrate Phase 2 survival analysis for term structure
   - Validate portfolio ECL (% AUM) against Phase 1 cohorts and banking norms
   - Document all assumptions tied to Phase 3 and Phase 4 frameworks

---

## Preserved Notebooks

### Notebook 01 -- ECL Baseline and Staging

**Input**: Phase 0 data (full portfolio), Phase 1 baseline (for reference only), provisional LGD/EAD

**Current scope**:
- Population: All Phase 0 loans (performing and defaulted)
- Stages: Stage 1 (no SICR), Stage 2 (significant increase in credit risk), Stage 3 (default)
- ECL formula: Stage 1 = 12m × LGD × EAD × PD; Stage 2/3 = lifetime × LGD × EAD × PD
- Staging thresholds: Generic IFRS 9 (e.g., probability of default increases by >X%)
- Output: Portfolio ECL ~$55-70M (~1.8-2.2% of AUM)

**Key issues with current approach**:
- [ ] Does not load Phase 1 PD baseline or grades
- [ ] Staging thresholds not tied to Phase 3's representativeness testing
- [ ] Uses provisional/placeholder LGD and EAD (not from Phase 4)
- [ ] No MoC from Phase 3 applied to ECL
- [ ] No term-structure PD from Phase 2 survival analysis (Stage 2/3 uses 24-month proxy)
- [ ] No ECL by grade (pooled portfolio calculation only)
- [ ] No validation that portfolio ECL (% AUM) matches banking norms
- [ ] Assumes PD/LGD/EAD are independent (no correlation adjustments)

**What the rewrite will do**:
1. Load Phase 1 PD grades and Phase 3's TTC-adjusted PD
2. Load Phase 4's validated LGD and EAD models by grade
3. Implement staging logic using Phase 3's representativeness thresholds:
   - Stage 1: Loans with PD increase < threshold (defined by Phase 3)
   - Stage 2: Loans with PD increase >= threshold
   - Stage 3: Loans in default (as defined by Phase 1)
4. Calculate ECL by grade:
   - Stage 1: 12-month PD × LGD × EAD × (1 + MoC_phase3)
   - Stage 2/3: Lifetime PD × LGD × EAD × (1 + MoC_phase3)
5. Use Phase 2 survival analysis for lifetime PD term structure (if available)
6. Aggregate ECL by grade to portfolio level
7. Validate: portfolio ECL / AUM should be within expected range for this portfolio

---

### Notebook 02 -- ECL Sensitivity and Validation

**Input**: Phase 0 data, Phase 1 baseline, ECL from Notebook 01, provisional scenarios

**Current scope**:
- Sensitivity: ECL to +/- changes in PD, LGD, EAD (e.g., PD ± 10%, LGD ± 5%, EAD ± 10%)
- Scenarios: Base case (baseline), upside (good economy), downside (recession)
- Validation: Compare ECL to observed defaults and recovery, check for alignment to IFRS 9 principles
- Output: ECL ranges and sensitivity tables

**Key issues with current approach**:
- [ ] Sensitivity not tied to Phase 3's scenario framework
- [ ] Macro scenario assumptions are ad-hoc (not formalized in Phase 7)
- [ ] Validation does not back-test to Phase 1 cohorts
- [ ] No analysis of which grade/vintage drives ECL changes
- [ ] Assumes PD/LGD/EAD can be varied independently (ignores correlation)
- [ ] No stress test severity tied to industry standards

**What the rewrite will do**:
1. Load Phase 3's scenario framework (base, upside, downside macro assumptions)
2. For each scenario, recalculate PD using Phase 3's scenario mappings
3. Recalculate ECL using Phase 4's LGD/EAD by grade
4. Sensitivity analysis: systematically vary PD/LGD/EAD by grade; show which grade is most sensitive
5. Back-test: for Phase 1 cohorts, did observed defaults match Phase 1 PD? Does implied ECL match observed loss?
6. Stress test: apply market stress (e.g., recession scenario from Phase 7); show ECL impact by grade and vintage
7. Compare portfolio ECL (% AUM) to banking benchmarks and Phase 1 observed experience
8. Document which assumptions drive ECL variability

---

## Expected Outputs (Current, Pre-Rewrite)

These are the outputs the preserved notebooks would produce if run as-is:

```
models/
├── ecl_staging_logic_v1.joblib                ECL staging model (probability of Stage 2/3)
├── ecl_baseline_v1.joblib                     ECL baseline calculation logic
├── model_card_ecl_v1.json                     ECL model metadata
└── model_card_staging_v1.json                 Staging model metadata

data/04_assets/tables/
├── ecl_by_stage.csv                           Stage 1/2/3 breakdown (count, EAD, ECL)
├── ecl_by_grade.csv                           ECL by risk grade (if computed)
├── ecl_by_vintage.csv                         ECL by origination vintage
├── ecl_sensitivity_pd.csv                     ECL sensitivity to PD ±10%
├── ecl_sensitivity_lgd.csv                    ECL sensitivity to LGD ±5%
├── ecl_sensitivity_ead.csv                    ECL sensitivity to EAD ±10%
├── ecl_scenario_analysis.csv                  ECL under base/upside/downside scenarios
└── ecl_vs_observed_loss.csv                   Comparison: ECL (predicted) vs observed default rates
```

**⚠️ WARNING**: These outputs are **not yet validated** against Phase 1 cohorts or Phase 3's calibration framework. Once Phase 3 & 4 are complete, all of these will be regenerated using the corrected methodology.

---

## Expected Outputs (Post-Rewrite, After Phase 3 & 4)

After Phase 3 completion, Phase 4 completion, and Phase 5 rewrite, the new outputs will be:

```
models/
├── staging_logic_v2.joblib                    Staging model using Phase 3 thresholds
├── ecl_calculator_v2.joblib                   ECL calculation using Phase 1/3/4 outputs
├── model_card_ecl_segmented_v2.json           ECL segmented by grade model metadata
└── model_card_staging_v2.json                 Staging model metadata (Phase 3 aligned)

data/04_assets/tables/
├── ecl_by_stage_and_grade.csv                 Stage/Grade breakdown with Phase 3 thresholds
├── ecl_by_grade_summary.csv                   ECL by grade with MoC applied (from Phase 3)
├── ecl_by_vintage_and_grade.csv               ECL by vintage and grade
├── phase5_vs_phase1_cohort_validation.csv    ECL prediction accuracy vs Phase 1 observed defaults
├── ecl_sensitivity_phase3_scenarios.csv       Sensitivity using Phase 3's macro scenarios
├── ecl_stress_test_results.csv                Stress test results (recession scenario, etc.)
└── portfolio_ecl_summary_v2.csv               Final portfolio ECL (% AUM) with validation
```

---

## How to Reproduce (Current Approach — Not Recommended)

**⚠️ These instructions are for reference only. Do NOT run these notebooks as the basis for regulatory ECL reporting. Wait for Phase 3 & 4 completion and Phase 5 rewrite.**

```bash
# If you must run the current (incorrect) approach:
cd phase5_ecl_provisioning/01_lendingclub/notebooks/

# Ensure Phase 0 data is available
ls ../../phase0_data_platform/01_lendingclub/data/03_processed/lendingclub_model_ready.parquet

# Run ECL staging notebook (will produce pooled portfolio ECL ~$55-70M)
jupyter notebook 01_ecl_baseline_and_staging.ipynb

# Run sensitivity and validation notebook (will produce sensitivity tables)
jupyter notebook 02_ecl_sensitivity_and_validation.ipynb
```

**Better approach (once Phase 3 & 4 are complete)**:
- Wait for Phase 3 (Calibration & MoC) to complete
- Wait for Phase 4 (LGD & EAD models) to complete
- Read Phase 3's outputs: calibrated PD, TTC adjustments, MoC framework, representativeness thresholds, scenario definitions
- Read Phase 4's outputs: validated LGD and EAD by risk grade
- Rewrite Phase 5 notebooks using Phase 1, 3, and 4 outputs
- Run rewritten notebooks with proper segmentation, staging thresholds, and validation

---

## Design Principles (To Be Applied in Rewrite)

1. **Proper dependencies**: Load Phase 1 (PD baseline), Phase 3 (calibration/MoC/scenarios), and Phase 4 (LGD/EAD by grade)
2. **Staging by representativeness**: Use Phase 3's thresholds to determine when a loan transitions from Stage 1 to Stage 2 (significant increase in credit risk)
3. **ECL by grade**: Calculate Stage 1/2/3 ECL separately for each risk grade, then aggregate
4. **MoC application**: Apply Phase 3's MoC to all ECL estimates (Stage 1, 2, 3)
5. **Term structure**: Use Phase 2 survival analysis (if available) to get lifetime PD for Stage 2/3
6. **Validation strategy**: For each grade, compare Phase 5 predicted ECL to Phase 1 observed defaults; portfolio-level ECL should be within 1.5-3% of AUM
7. **Scenario framework**: Use Phase 3's macro scenarios (base/upside/downside) for sensitivity analysis
8. **Documentation**: Every assumption ties back to Phase 1 (PD grades), Phase 3 (calibration/MoC/thresholds), and Phase 4 (LGD/EAD validation)

---

## Known Gaps (To Be Addressed in Rewrite)

| Gap | Current | Will Be Fixed By |
|---|---|---|
| No Phase 1 integration | ❌ | Loading Phase 1 PD model, grades, and 12m-PD in rewrite |
| No Phase 3 calibration | ❌ | Loading Phase 3's TTC adjustment, MoC, representativeness thresholds in rewrite |
| No Phase 4 LGD/EAD | ❌ | Loading Phase 4's validated segmented LGD/EAD models in rewrite |
| Generic staging thresholds | ❌ | Using Phase 3's representativeness thresholds in rewrite |
| Pooled ECL only | ❌ | Building ECL by grade in rewrite |
| No MoC applied | ❌ | Applying Phase 3's MoC bounds to ECL estimates in rewrite |
| No term structure | ❌ | Integrating Phase 2 survival analysis for lifetime PD in rewrite |
| No Phase 1 cohort validation | ❌ | Adding cohort back-test in rewrite |
| Ad-hoc scenarios | ❌ | Using Phase 3's formalized scenario framework in rewrite |
| Standalone assumptions | ❌ | Tying all assumptions to Phase 1, 3, and 4 frameworks in rewrite |

---

## IFRS 9 Staging Rules (Correct Application After Rewrite)

Once Phase 3 is complete with its representativeness thresholds, staging will follow this logic:

### Stage 1 → Stage 2 Transition
A loan moves from Stage 1 to Stage 2 when its **probability of default increases significantly**.

**Operationalization** (to be defined by Phase 3):
- Example 1: If origination PD = 5% and current PD >= 7.5% (50% relative increase), move to Stage 2
- Example 2: If origination PD = 5% and current PD >= 10% (absolute increase of 5%), move to Stage 2
- The exact threshold is determined by Phase 3's representativeness testing and is specified in the rewrite

### Stage 2 → Stage 3 Transition
A loan moves to Stage 3 when it enters default, as defined by Phase 1:
- Example: Payment 90+ days past due, or loan flagged as default in Phase 0

### ECL Calculation by Stage
- **Stage 1**: ECL = 12-month PD × LGD × EAD × (1 + MoC_phase3)
- **Stage 2**: ECL = Lifetime PD × LGD × EAD × (1 + MoC_phase3)
- **Stage 3**: ECL = (1 - Recovery Rate) × EAD × (1 + MoC_phase3), approximated as LGD × EAD in simplified form

---

## Hand-off to Phase 6

Once Phase 5 is properly completed (after Phase 3 & 4), it will hand off to Phase 6 (Capital & Segmentation):

- **Phase 1 outputs**: Calibrated PD by grade (from Phase 1 + Phase 3 TTC adjustment)
- **Phase 3 outputs**: MoC bounds, scenario framework, representativeness testing results
- **Phase 4 outputs**: Validated LGD and EAD by grade
- **Phase 5 outputs**: ECL by stage and grade, with validation against Phase 1 cohorts
- **Phase 6 consumes**: Portfolio ECL, stage breakdown, scenario sensitivity to design capital framework (RWA/CRAR)

---

## Next Steps

1. **Phase 3 completion** (Planned): Build calibration & MoC framework, representativeness testing, scenario definitions
2. **Phase 4 completion** (After Phase 3): Build validated LGD/EAD models by grade
3. **Phase 5 rewrite** (After Phase 3 & 4): Notebooks rewritten with proper methodology, using all upstream outputs
4. **Phase 5 outputs regenerated**: New ECL calculations, segmentation, validation, and stress test results
5. **Phase 6 built**: Capital framework consuming Phase 1, 3, 4, and 5 outputs

---

## References

- **Phase 1 (PD Baseline)**: `../../phase1_pd_modeling/01_lendingclub/README.md`
- **Phase 2 (Challenger Models)**: `../../phase2_challenger_models/01_lendingclub/README.md`
- **Phase 3 (Calibration & MoC)**: `../../phase3_calibration_moc/README.md` [Planned]
- **Phase 4 (LGD & EAD)**: `../../phase4_lgd_ead_models/01_lendingclub/README.md`
- **Course Material**: `../../docs/Peaks2Tails_Knowledge_Base.md`
- **IFRS 9 Standard**: IAS 39 / IFRS 9 impairment model (expected credit loss framework)
- **Status**: Preserved; awaiting Phase 3 & 4 before rewrite
