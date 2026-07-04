"""
Part 4: baseline data subset analysis.

Scope: melanoma + miraclib + PBMC, baseline only (time_from_treatment_start == 0).
Same predictive-biomarker framing as Part 3 (see src/domain/statistics.py).
"""

import pandas as pd

from src.domain.vocab import BASELINE, Condition, SampleType, Treatment


def filter_melanoma_miraclib_pbmc_baseline(annotated_counts: pd.DataFrame) -> pd.DataFrame:
    """melanoma + miraclib + PBMC + baseline (t=0). One row per (sample, population)."""
    mask = (
            (annotated_counts["condition"] == Condition.MELANOMA)
            & (annotated_counts["treatment"] == Treatment.MIRACLIB)
            & (annotated_counts["sample_type"] == SampleType.PBMC)
            & (annotated_counts["time_from_treatment_start"] == BASELINE)
    )
    return annotated_counts.loc[mask].reset_index(drop=True)


def combine_cohort_counts(
    samples_per_project: pd.DataFrame,
    subjects_per_response: pd.DataFrame,
    subjects_per_sex: pd.DataFrame,
) -> pd.DataFrame:
    """
    Assemble the three Part 4 count queries (each already filtered/grouped in
    SQL) into one tidy (metric, group, value) table.
    """
    rows = []
    for _, row in samples_per_project.iterrows():
        rows.append({"metric": "samples_per_project", "group": row["project_id"], "value": row["sample_count"]})
    for _, row in subjects_per_response.iterrows():
        rows.append({"metric": "subjects_per_response", "group": row["response"], "value": row["subject_count"]})
    for _, row in subjects_per_sex.iterrows():
        rows.append({"metric": "subjects_per_sex", "group": row["sex"], "value": row["subject_count"]})

    return pd.DataFrame(rows)


def summarize_population_means(subset: pd.DataFrame) -> pd.DataFrame:
    """
    Mean cell count per population, broken down by sex and response, for the
    baseline subset. Part 4's specific question (melanoma males, responders)
    is the row where sex="M", response="yes", population="b_cell".
    """
    means = (
        subset.groupby(["sex", "response", "population"])["cell_count"]
        .mean()
        .round(2)
        .reset_index(name="mean_cell_count")
    )
    return means
