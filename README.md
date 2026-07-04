---
title: miraclib_cell_counts_analysis
emoji: 🧬
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: "1.58.0"
app_file: dashboard/app.py
pinned: false
python_version: "3.12"
---

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

The source `cell-count.csv` is one flat table (1 row = 1 sample). I normalized it into
**5 tables (3NF)**: `projects → subjects → samples → cell_counts`, plus `populations`
(a controlled vocabulary of cell types) and a `cell_frequencies` VIEW. Moving subject-level
fields (`condition`, `sex`, `treatment`, `response`) out of `samples` removes the repetition
from each subject having up to 3 timepoints.

**Design decisions**

- **Long-format `cell_counts`** — population is a row, not a column. New cell type = zero
  schema change.
- **Raw counts only, percentages derived in a VIEW** — `cell_frequencies` computes Part 2 on
  the fly, so it can't drift out of sync with the counts. Single source of truth.
- **`CHECK` + `populations` FK** — controlled vocabulary. Bad values rejected at write time.
- **Natural `TEXT` keys** (`prj1`, `sbj000`) — source IDs used as-is, no surrogate keys.

**Scaling.** I design for extension by default, so growth here is cheap. The cost is a few
extra tables and joins instead of one flat file — a trade-off against complexity, but I think
this is the right balance.

- **Hundreds of projects** → add rows to `projects`. No schema change. FK index keeps
  per-project filtering fast.
- **Thousands of samples** → every FK column is indexed, so lookups stay index scans. Long
  format means the data only grows vertically.
- **Various analytics** → new populations are more rows, new metrics are more VIEWs, new
  questions are JOIN / GROUP BY. The schema rarely changes to answer a new question.

### ERD

![ERD diagram](outputs/erd.png)

---

## Code structure

The main pipeline (`src/`) follows a clean-architecture layering, and the dashboard, tests,
and pipeline entry points are kept separate.

- **`src/data`** — talks to the outside world (SQLite, CSV). Returns DataFrames.
- **`src/domain`** — pure computation (frequencies, stats, subsets). Imports neither the DB
  nor the UI, so it's easy to test and reuse.
- **`src/ui`** — turns domain results into plots and output tables.

Entry points stay thin and only wire the layers together. `load_data.py` sits at repo root
(as the task requires) but delegates its logic to `src/data/loader.py`. `run_pipeline.py`
orchestrates Parts 2–4. The dashboard reads only the CSVs in `outputs/`, so it never
recomputes or imports `src/`.

```
miraclib_cell_counts_analysis/
├── load_data.py            # Part 1 entry point (root, no args) — thin, calls src/data
├── run_pipeline.py         # Parts 2–4 orchestration (make pipeline)
├── schema.sql              # DB schema
├── data/cell-count.csv     # input
├── outputs/                # generated tables + plots
├── src/
│   ├── data/               # DB / CSV I/O, SQL queries
│   ├── domain/             # pure business logic (no DB, no UI)
│   └── ui/                 # plots + output-table formatting
├── dashboard/              # Streamlit app (reads outputs/ only)
│   ├── app.py
│   ├── sections/           # overview / frequencies / stats / subset
│   └── components/         # data loading, charts, filters
└── tests/                  # unit tests for domain logic
```

---

## Part 2 — Cell population frequencies

For each sample, total count = sum of the 5 populations, and each population's relative
frequency = `count / total_count * 100`. This is computed in SQL by the `cell_frequencies`
VIEW (see `schema.sql`), so it's always derived from the raw counts, never stored.

Output: `outputs/cell_frequencies.csv` (52,500 rows = 10,500 samples × 5 populations). The
first five columns are the ones the task asks for — `sample`, `total_count`, `population`,
`count`, `percentage` — followed by sample metadata (`subject`, `project`, `condition`, `sex`,
`treatment`, `response`, `sample_type`, `time_from_treatment_start`) that the dashboard and
later parts reuse.

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