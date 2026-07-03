"""
Part 4: baseline data subset analysis.

Scope: melanoma + miraclib + PBMC, baseline only (time_from_treatment_start == 0).
Same predictive-biomarker framing as Part 3 (see src/domain/statistics.py).
"""

import pandas as pd

from src.domain.vocab import BASELINE, Condition, Population, Response, Sex, SampleType, Treatment


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
    Tidy (metric, group, value) summary of the baseline subset:
    sample counts per project, subject counts per response, subject counts
    per sex, and the headline number: mean B-cell count for melanoma-male
    responders at baseline.
    """
    samples = subset.drop_duplicates("sample_id")
    subjects = subset.drop_duplicates("subject_id")

    rows = []
    for project_id, count in samples.groupby("project_id").size().items():
        rows.append({"metric": "samples_per_project", "group": project_id, "value": count})

    for response, count in subjects.groupby("response").size().items():
        rows.append({"metric": "subjects_per_response", "group": response, "value": count})

    for sex, count in subjects.groupby("sex").size().items():
        rows.append({"metric": "subjects_per_sex", "group": sex, "value": count})

    male_responder_b_cell = subset.loc[
        (subset["sex"] == Sex.M)
        & (subset["response"] == Response.YES)
        & (subset["population"] == Population.B_CELL),
        "cell_count",
    ]
    rows.append({
        "metric": "b_cell_mean",
        "group": "melanoma_male_responder",
        "value": round(male_responder_b_cell.mean(), 2),
    })

    return pd.DataFrame(rows)
