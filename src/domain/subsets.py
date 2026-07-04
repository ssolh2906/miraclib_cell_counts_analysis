"""
Part 4: baseline data subset analysis.

Scope: melanoma + miraclib + PBMC, baseline only (time_from_treatment_start == 0).
Same predictive-biomarker framing as Part 3 (see src/domain/statistics.py).
"""

import pandas as pd

from src.domain.vocab import BASELINE, Condition, SampleType, Treatment


def filter_baseline_subset(annotated_counts: pd.DataFrame) -> pd.DataFrame:
    """melanoma + miraclib + PBMC + baseline (t=0). One row per (sample, population)."""
    mask = (
            (annotated_counts["condition"] == Condition.MELANOMA)
            & (annotated_counts["treatment"] == Treatment.MIRACLIB)
            & (annotated_counts["sample_type"] == SampleType.PBMC)
            & (annotated_counts["time_from_treatment_start"] == BASELINE)
    )
    return annotated_counts.loc[mask].reset_index(drop=True)


def summarize_subset(subset: pd.DataFrame) -> pd.DataFrame:
    """
    Tidy summary of the baseline subset: sample counts per project, subject
    counts per response, subject counts per sex, and per-population mean
    cell count for every (sex, response) group. Part 4's specific question
    (melanoma males, responders) is one slice of that last table: group="M_yes".
    """
    samples = subset.drop_duplicates("sample_id")
    subjects = subset.drop_duplicates("subject_id")

    rows = []
    for project_id, count in samples.groupby("project_id").size().items():
        rows.append({"metric": "samples_per_project", "group": project_id, "population": None, "value": count})

    for response, count in subjects.groupby("response").size().items():
        rows.append({"metric": "subjects_per_response", "group": response, "population": None, "value": count})

    for sex, count in subjects.groupby("sex").size().items():
        rows.append({"metric": "subjects_per_sex", "group": sex, "population": None, "value": count})

    for (sex, response), group_df in subset.groupby(["sex", "response"]):
        for population, cell_counts in group_df.groupby("population")["cell_count"]:
            rows.append({
                "metric": "population_mean",
                "group": f"{sex}_{response}",
                "population": population,
                "value": round(cell_counts.mean(), 2),
            })

    return pd.DataFrame(rows)
