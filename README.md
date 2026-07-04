# miraclib_cell_counts_analysis

This repository is for Teiko's technical exam.

Analysis of `cell-count.csv` (PBMC immune cell populations) to understand how the drug candidate
**miraclib** relates to treatment response, using a SQLite database, Python analysis pipeline, and
an interactive Streamlit dashboard.

Python version: **3.12** (see `.python-version`, `.devcontainer/devcontainer.json`).

---

## How to run

```bash
make setup      # install dependencies
make pipeline   # build cell_counts.db + generate all outputs/ tables & plots
make dashboard  # launch Streamlit dashboard (localhost:8501)
```

TODO: one-paragraph walkthrough of what each step does and what to expect as output
(console progress logs, files created under `outputs/`).

---

## Data schema

TODO: rationale for the 3-table schema (`subjects`, `samples`, `cell_counts` long format),
why population is stored as rows rather than columns, and how this scales to hundreds of
projects / thousands of samples / new analytics.

### ERD

![ERD diagram](outputs/erd.png)

---

## Code structure

TODO: overview of the `src/data` / `src/domain` / `src/ui` clean-architecture layering, why
`load_data.py` lives at repo root while its logic is delegated to `src/data/loader.py`, and how
this keeps the codebase easy to extend one file at a time.

---

## Part 2 — Cell population frequencies

TODO: brief description of relative frequency calculation, pointer to
`outputs/cell_frequencies.csv`.

---

## Part 3 — Responder vs non-responder comparison (melanoma + miraclib + PBMC)

TODO: baseline (t=0) rationale — "immune setpoint" framing, repeated-measures /
pseudoreplication handling, compositional-data caveat, and summary of results
(Mann-Whitney U, effect size, BH-adjusted q-value, ROC-AUC, PCA).

Outputs: `outputs/response_stats.csv`, `outputs/boxplots.png`, `outputs/pca.png`,
`outputs/roc_curves.png`.

---

## Part 4 — Melanoma / miraclib / PBMC baseline subset

TODO: why this subset is implemented as separate SQL queries (one per requirement) rather
than a single pandas filter, and the headline result (melanoma, male, responder, baseline
B cell mean).

Outputs: `outputs/melanoma_miraclib_pbmc_baseline_samples.csv`,
`outputs/subset_cohort_counts.csv`, `outputs/subset_population_means.csv`.

---

## Live dashboard

- **Codespaces**: `make dashboard` starts Streamlit on port 8501, auto-forwarded by Codespaces.
- **Permanent link (Hugging Face Spaces)**: TODO — not yet deployed.

---

## Limitations / future work

TODO: pharmacodynamic (longitudinal t=0→7/14) extension, other stretch ideas.