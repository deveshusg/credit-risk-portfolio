\# Credit Risk Portfolio



A clean, reproducible portfolio of credit-risk analytics and modeling projects by \*\*Devesh Gupta\*\*.



\## 🚀 Overview — What’s in this repo

This repository contains end-to-end credit risk projects focused on practical, interview-defendable work:



\- Point-in-Time PD — IFRS9-style PiT PD modeling (priority).

\- ECL (PD × EAD × LGD) — combining PD, EAD, LGD for provisioning.

\- Through-the-Cycle PD — vintage stability \& backtests.

\- Rule-based ECL — stage migration \& explainable provisioning rules.

\- SQL case studies — cohort repayment analytics \& fraud detection queries.

\- Retail / Wholesale credit strategy — policy simulation and limit-setting.

\- Streamlit demos — small interactive apps (PiT demo \& ECL calculator).



---



\## 🔧 Quick start (run in cloud — no local setup required)



\### Colab (author + run notebooks)

Open any notebook in Colab:

https://colab.research.google.com/github/deveshusg/credit-risk-portfolio/blob/main/notebooks/02\_point\_in\_time\_pd.ipynb

(Replace "02\_point\_in\_time\_pd.ipynb" with the notebook you want.)



\### Binder (interactive JupyterLab)

Launch JupyterLab via Binder:

https://mybinder.org/v2/gh/deveshusg/credit-risk-portfolio/main?urlpath=lab



\### Streamlit demo (run in cloud or locally)

To run the simple demo locally (if you have Python installed):

pip install -r requirements.txt

streamlit run streamlit\_apps/pit\_demo.py



---



\## 📁 Repo structure (short)

notebooks/         # Jupyter notebooks (PiT, ECL, TtC, SQL case studies)

data/              # small sample datasets for fast runs (no raw Kaggle dumps)

src/               # reusable functions (data\_prep, modeling, metrics, viz)

streamlit\_apps/    # small interactive demos

sql/               # SQL case studies (cohort analysis, fraud detection)

artifacts/         # charts, reports, decks



---



\## 📥 Data \& reproducibility notes

\- Large public datasets (Home Credit, LendingClub, Fannie Mae) are NOT stored here. See data/README\_DATA.md for download links and reproducible kaggle / Colab commands.

\- Each notebook contains a small sample so it can run on Binder/Colab instantly.



---



\## 📬 Contact

Devesh Gupta — deveshusg@gmail.com  

LinkedIn: https://www.linkedin.com/in/gupta-devesh/



---



\## License

MIT License — see LICENSE



