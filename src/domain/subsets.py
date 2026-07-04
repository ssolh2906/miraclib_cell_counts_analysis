"""
Part 4: baseline data subset analysis.

Scope: melanoma + miraclib + PBMC, baseline only (time_from_treatment_start == 0).
Same predictive-biomarker framing as Part 3 (see src/domain/statistics.py).
"""

import numpy as np
import pandas as pd
from scipy.stats import false_discovery_control, mannwhitneyu

from src.domain.frequency import compute_frequencies_with_metadata
from src.domain.vocab import BASELINE, POPULATION_COLUMNS, Condition, Response, SampleType, Sex, Treatment


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
    means["population"] = pd.Categorical(means["population"], categories=POPULATION_COLUMNS, ordered=True)
    means = means.sort_values(["sex", "response", "population"]).reset_index(drop=True)
    means["population"] = means["population"].astype(str)
    return means


def compute_melanoma_miraclib_pbmc_baseline_response_frequencies(
    melanoma_miraclib_pbmc_baseline: pd.DataFrame,
) -> pd.DataFrame:
    """
    Per-(sample, population) relative frequency (%) for the baseline cohort,
    with sex + response attached, responder/non-responder only. Shared by the
    sex-stratified stats and the matching boxplot so both are drawn from the
    same numbers.
    """
    freq = compute_frequencies_with_metadata(melanoma_miraclib_pbmc_baseline)
    return freq.loc[freq["response"].isin([Response.YES, Response.NO])].reset_index(drop=True)


def compare_responders_by_sex_melanoma_miraclib_pbmc_baseline(
    melanoma_miraclib_pbmc_baseline: pd.DataFrame,
) -> pd.DataFrame:
    """
    Sex-stratified (M, F) responder vs non-responder comparison, per population,
    for the melanoma + miraclib + PBMC baseline (t=0) cohort. Percentage-based
    (not raw cell count), so it stays compositional-comparable with Part 3 and
    avoids confounding by per-sample total cell count. BH q-value is computed
    within each sex, across its 5 populations.
    """
    freq = compute_melanoma_miraclib_pbmc_baseline_response_frequencies(melanoma_miraclib_pbmc_baseline)

    rows = []
    for sex in [Sex.M, Sex.F]:
        sex_freq = freq.loc[freq["sex"] == sex]
        sex_rows = []
        for population in POPULATION_COLUMNS:
            group = sex_freq.loc[sex_freq["population"] == population]
            responders = group.loc[group["response"] == Response.YES, "percentage"].to_numpy()
            non_responders = group.loc[group["response"] == Response.NO, "percentage"].to_numpy()

            u_stat, p_value = mannwhitneyu(responders, non_responders, alternative="two-sided")
            median_responder = np.median(responders)
            median_non_responder = np.median(non_responders)

            sex_rows.append({
                "sex": sex.value,
                "population": population,
                "n_responder": len(responders),
                "n_non_responder": len(non_responders),
                "median_responder": median_responder,
                "median_non_responder": median_non_responder,
                "difference": median_responder - median_non_responder,
                "u_statistic": u_stat,
                "p_value": p_value,
            })

        q_values = false_discovery_control([row["p_value"] for row in sex_rows], method="bh")
        for row, q_value in zip(sex_rows, q_values):
            row["q_value"] = q_value
        rows.extend(sex_rows)

    columns = [
        "sex", "population", "n_responder", "n_non_responder",
        "median_responder", "median_non_responder", "difference",
        "u_statistic", "p_value", "q_value",
    ]
    return pd.DataFrame(rows, columns=columns)
