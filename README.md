# FAIR INCLUSIVE AV — Gender Pay Gap Calculator Prototype

This repository contains the proof-of-concept prototype for a gender pay gap (GPG) calculator designed for the European audiovisual sector, built as part of an application for **EURO-MEI Project 101250721 (FAIR INCLUSIVE AV)**. The prototype demonstrates that a sector-specific pay gap instrument can be constructed from project-based, multi-employer contract data -> something existing tools (Logib, UK GPG reporting service, Austrian Equal Pay Tool) cannot do, as they assume a single employer and a permanently employed workforce. The simulated dataset covers **693 contracts, 230 workers, 65 productions, and 22 variables** spanning four countries (ES, FR, DE, IE), generated with a fixed random seed for full reproducibility.

---

## What it implements

| Method | Specification |
|---|---|
| Unadjusted GPG | Mean and median pay gap by gender, Eurostat SES definition |
| Adjusted GPG | OLS regression controlling for role, seniority, experience, production type, contract type, and country |
| Pay quartile distribution | Per Directive 2023/970 Art. 9.1.f |
| Gap by category of workers | Per Directive 2023/970 Art. 9.1.g |
| Oaxaca-Blinder decomposition | Explained vs. unexplained gap components, consistent with Logib methodology |
| MNAR bias detection | Missing Not At Random test for selective non-reporting of pay by gender/role |
| Worker-year FTE aggregation | Contracts aggregated to FTE equivalent using Eurostat SES 220-day reference |

**Key finding:** 14.1% of the total pay gap is unexplained by structural characteristics (the Art. 10 joint pay assessment proxy), while the remainder is attributable to occupational segregation and seniority differentials. The prototype also demonstrates that MNAR bias in pay reporting for women in low-paid roles leads to underestimation of the true gap — a methodological consideration that must be addressed in any real-data implementation.

---

## Requirements

- Python 3.9+
- `pandas`, `numpy`, `scipy`, `statsmodels`, `matplotlib`, `seaborn`
- `reportlab` (for PDF generation only)
- `jupyter` (to run the analysis notebook)

Install all dependencies:

```bash
pip install pandas numpy scipy statsmodels matplotlib seaborn reportlab jupyter
```

---

## How to run

### Analysis notebook

```bash
jupyter notebook gpg_analysis.ipynb
```

Or view the pre-rendered output in `gpg_analysis.html` (no installation required).

### Regenerate the methodology proposal PDF

```bash
python generate_methodology.py
```

Output: `methodology_proposal.pdf`

### Regenerate the dataset

```bash
python generate_dataset.py
```

Recreates `audiovisual_pay_dataset.csv` with random seed 42.

### Regenerate figures

Figures are produced by `gpg_analysis.ipynb`. Run all cells to regenerate the `figures/` directory.

### Regenerate the codebook PDF

```bash
python generate_codebook.py
```

Output: `codebook.pdf`

---

## Repository structure

```
.
├── audiovisual_pay_dataset.csv   # Simulated dataset (693 contracts, 230 workers, 65 productions)
├── codebook.pdf                  # Full variable codebook with definitions and distributions
├── create_notebook.py            # Script to programmatically create gpg_analysis.ipynb
├── figures/                      # All output figures (PNG) referenced by the notebook and PDF
│   ├── fig1c_pay_quartiles.png
│   ├── fig3_oaxaca_blinder.png
│   ├── fig4a_gpg_contract_type.png
│   ├── fig4b_gpg_production_type.png
│   ├── fig4c_gpg_debut.png
│   ├── fig4d_intersectional_heatmap.png
│   ├── fig5a_heatmap_role_contract.png
│   ├── fig5b_oaxaca_policy.png
│   ├── fig5c_quartiles_policy.png
│   ├── fig5d_scatter_experience_pay.png
│   └── fig5e_gpg_by_role_ranked.png
├── generate_codebook.py          # Generates codebook.pdf using ReportLab
├── generate_dataset.py           # Generates the synthetic CSV dataset (seed 42)
├── generate_methodology.py       # Generates methodology_proposal.pdf using ReportLab
├── gpg_analysis.html             # Pre-rendered notebook output (viewable without Jupyter)
├── gpg_analysis.ipynb            # Main analysis notebook
└── methodology_proposal.pdf      # Methodology proposal for EURO-MEI Project 101250721
```

---

## Disclaimer

All data in this repository are **entirely synthetic**, generated programmatically with a fixed random seed. No real workers, productions, companies, or pay records are represented. No personal data, confidential information, or proprietary datasets have been used in the development of this prototype.

---

*Proof of concept for EURO-MEI FAIR INCLUSIVE AV — Project 101250721. April 2026. :-)*
