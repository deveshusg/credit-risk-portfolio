# Data sources & instructions

This folder contains instructions and links to the public datasets used (or useful) for credit-risk model development.
Some datasets are hosted on Kaggle (require Kaggle account & API token) and some are large (Fannie Mae). Where possible a small local sample is provided in `data/` for quick runs.

---

## Recommended datasets (links & short notes)

1. **Give Me Some Credit** (Kaggle competition)  
   - Link: https://www.kaggle.com/c/GiveMeSomeCredit  
   - Note: Classic small PD dataset. Requires Kaggle login to download.

2. **Home Credit - Default Risk** (Kaggle competition)  
   - Link: https://www.kaggle.com/c/home-credit-default-risk  
   - Note: Rich retail credit dataset with many tables. Requires Kaggle login. Large.

3. **Lending Club Loan Data** (public historic loan records)  
   - Link (Kaggle mirrors & aggregated copies): search Kaggle for "LendingClub" or use LendingClub's public data portals / academic mirrors. Example aggregator: https://www.kaggle.com/datasets (search "LendingClub")  
   - Note: Very large. Use year-wise slices for experiments.

4. **Fannie Mae Single-Family Loan Performance (SFLP)**  
   - Link: https://www.fanniemae.com/research/datasets/single-family-loan-performance-data  
   - Note: Very large mortgage-level dataset. Good for long-run default studies. Use sampled subsets for local experiments.

5. **UCI — Default of Credit Card Clients**  
   - Link: https://archive.ics.uci.edu/ml/datasets/default+of+credit+card+clients  
   - Note: Small, quick for demos and reproducible examples.

6. **Sample / repo-provided small files (for Binder/Colab quick runs)**  
   - `data/sample_pit.csv` — minimal PiT demo sample  
   - `data/sample_ecl.csv` — minimal ECL demo sample  
   - `data/sample_sql_case.csv` — tiny SQL test file

---

## How to download

### Recommended local layout:
- `data/raw/` → full raw datasets (should *not* be committed to Git due to size / licensing)
- `data/processed/` → cleaned / sampled data used by notebooks
- `data/samples/` → very small example files (safe to commit)

### Using Kaggle (recommended for Kaggle-hosted data)
1. Install: `pip install kaggle`
2. Place your `kaggle.json` (API token) in `%USERPROFILE%\.kaggle\kaggle.json` (Windows)
   - Create it on https://www.kaggle.com -> Account -> API -> Create New Token
3. Example download command (competition):  
   `kaggle competitions download -c <competition-slug> -p data/raw --unzip`  
   Example (GiveMeSomeCredit):  
   `kaggle competitions download -c GiveMeSomeCredit -p data/raw --unzip`

### Direct HTTP downloads (Fannie Mae / UCI / official sources)
Use `curl` or PowerShell `Invoke-WebRequest`. Example (PowerShell):
```powershell
Invoke-WebRequest -Uri "<direct-file-url>" -OutFile "data/raw/<filename>"
