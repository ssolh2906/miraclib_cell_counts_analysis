---
title: miraclib_cell_counts_analysis
emoji: 🧬
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8501
pinned: false
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

The instruction fixes the cohort: melanoma patients on miraclib, PBMC samples only. I compare
them at **baseline (t=0)** — the timepoint that matters for prediction. A difference at t=0
would flag responders *before* treatment even starts (the individual's **immune setpoint**).
It also keeps the test clean: each subject has 3 timepoints, so
using only t=0 gives one independent sample per subject (656 subjects, 331 responders / 325
non-responders).

**Method.** For each of the 5 populations I run a Mann-Whitney U test, report an effect size
(Cliff's delta) and median (IQR), and draw a boxplot. Because 5 populations are
tested at once, I apply a Benjamini-Hochberg **q-value** in the pipeline — strictly not needed
given the result, but it can be effective in other dataset.
**Result — no population separates responders at baseline.**

| population | median (R vs NR) | p | q (BH) | Cliff's δ |
|---|---|---|---|---|
| b_cell     | 9.79 vs 9.76   | 0.55 | 0.89 |  0.03 |
| cd8_t_cell | 24.40 vs 24.60 | 0.51 | 0.89 | -0.03 |
| cd4_t_cell | 29.63 vs 29.53 | 0.80 | 0.89 |  0.01 |
| nk_cell    | 15.00 vs 14.89 | 0.89 | 0.89 | -0.01 |
| monocyte   | 19.61 vs 20.29 | 0.21 | 0.89 | -0.06 |

Every p is non-significant and every effect size is near zero. Two extra checks agree: PCA of
the 5-population profile shows the two groups fully overlapping with near-coincident centroids
(no significant separation), and per-population ROC-AUC sits between 0.47 and 0.51 — right on
the diagonal, i.e. no better than chance.

So my honest conclusion is that **baseline PBMC frequency alone does not distinguish miraclib
responders**. It's consistent across the p-value, effect
size, PCA, and AUC. One caveat worth naming: frequencies are compositional (they sum to 100%
per sample), so the populations aren't independent.
Absence of evidence is not evidence of absence. No significant difference here doesn't prove there is none. 
A rawer or richer signal (single-cell resolution, more markers) or a larger cohort could still surface one that this snapshot can't.

Outputs: `outputs/response_stats.csv`, `outputs/boxplots.png`, `outputs/pca.png`,
`outputs/roc_curves.png`.

---

## Part 4 — Melanoma / miraclib / PBMC baseline subset

**Headline result — melanoma males, responders, baseline: mean B cell count = 10401.28.**

Step 1 identifies the cohort: Melanoma PBMC samples at baseline (t=0) from patients on
miraclib — 656 samples.

The task says to *query the database and extend the query*, so I wrote each requirement as its
own SQL query (samples-per-project, subjects-per-response, subjects-per-sex) rather than one
pandas filter over a dumped table. It keeps the work in SQL where it belongs and each query
reads as exactly the question it answers. Function and file names spell out the cohort
(`melanoma_miraclib_pbmc_baseline_*`) so it's clear what was filtered without reading the body.

I also ran an optional check on this cohort: responder vs non-responder, split by sex, for each
population, with a boxplot and a Mann-Whitney U p-value. Nothing seems significant (every q bhigher than 0.05), consistent with Part 3. I deliberately tested **relative frequency (%)** here,
not raw counts — on raw counts female cd4_t_cell looks significant, but that's an artifact of
responders simply having more total cells, which the compositional (%) view corrects.

Outputs: `outputs/melanoma_miraclib_pbmc_baseline_samples.csv`,
`outputs/subset_cohort_counts.csv`, `outputs/subset_population_means.csv`,
`outputs/melanoma_miraclib_pbmc_baseline_response_stats.csv`,
`outputs/melanoma_miraclib_pbmc_baseline_boxplots_by_sex.png`.

---

## Live dashboard

- **Codespaces**: `make dashboard` starts Streamlit on port 8501, auto-forwarded by Codespaces.
- **Permanent link (Hugging Face Spaces)**: TODO — not yet deployed.

---

## Limitations / future work

- **Timeline extension.** The analysis is baseline-only (t=0). The 7 and 14 day timepoints are
  already in the schema, so a pharmacodynamic view (how each population shifts on treatment,
  t=0→7→14) is a natural next step — paired within-subject, not the baseline snapshot.
- **More universal subset queries.** Part 4 is implemented as separate, explicit queries per
  requirement. They work, but they could be parameterized (condition, treatment, sample_type,
  timepoint as arguments) into one reusable function instead of one query per case.