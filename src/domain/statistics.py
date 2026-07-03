"""
Part 3: responder vs non-responder comparison, per population.


Scope: melanoma + miraclib + PBMC, baseline only (time_from_treatment_start == 0).
Baseline-only is a deliberate choice, not a shortcut: it frames the comparison as a
*predictive* biomarker (measured before treatment) rather than a pharmacodynamic one,
and it sidesteps pseudoreplication from repeated measures (each subject has 3 samples,
one per timepoint, which are not independent observations).
"""

import numpy as np
import pandas as pd
from scipy.stats import false_discovery_control, mannwhitneyu
from sklearn.decomposition import PCA
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

from src.domain.frequency import compute_frequencies
from src.domain.vocab import BASELINE, POPULATION_COLUMNS, Condition, Response, SampleType, Treatment


def filter_predictive_subset(annotated_counts: pd.DataFrame) -> pd.DataFrame:
    """melanoma + miraclib + PBMC + baseline (t=0), responder/non-responder only."""
    mask = (
            (annotated_counts["condition"] == Condition.MELANOMA)
            & (annotated_counts["treatment"] == Treatment.MIRACLIB)
            & (annotated_counts["sample_type"] == SampleType.PBMC)
            & (annotated_counts["time_from_treatment_start"] == BASELINE)
            & (annotated_counts["response"].isin([Response.YES, Response.NO]))
    )
    return annotated_counts.loc[mask].reset_index(drop=True)


def compute_response_frequencies(subset: pd.DataFrame) -> pd.DataFrame:
    """Per-sample relative frequency (%) for the filtered subset, with response attached."""
    counts = subset[["sample_id", "population", "cell_count"]].rename(
        columns={"sample_id": "sample_id"}
    )
    freq = compute_frequencies(counts)
    response_by_sample = subset[["sample_id", "response"]].drop_duplicates()
    return freq.merge(response_by_sample, on="sample_id", how="left")


def _cliffs_delta(x: np.ndarray, y: np.ndarray, u_statistic: float) -> float:
    """Effect size for Mann-Whitney U. Positive = x (responder) tends higher than y."""
    n1, n2 = len(x), len(y)
    return (2 * u_statistic) / (n1 * n2) - 1


def _iqr(values: np.ndarray) -> float:
    q75, q25 = np.percentile(values, [75, 25])
    return q75 - q25


def compare_responders(freq_with_response: pd.DataFrame) -> pd.DataFrame:
    """
    Per-population Mann-Whitney U test, responder (yes) vs
    non-responder (no).
    Returns one row per population (fixed order:
    POPULATION_COLUMNS, the original
    CSV column order, matching plots.py): n per group,
    medians, IQRs, U, p-value,
    Cliff's delta effect size, and BH-adjusted q-value.
    """
    rows = []
    for population in POPULATION_COLUMNS:
        group = freq_with_response.loc[freq_with_response["population"] ==
                                       population]
    responders = group.loc[group["response"] ==
                           Response.YES, "percentage"].to_numpy()
    non_responders = group.loc[group["response"] ==
                               Response.NO, "percentage"].to_numpy()

    u_stat, p_value = mannwhitneyu(responders,
                                   non_responders, alternative="two-sided")

    rows.append({
        "population": population,
        "n_responder": len(responders),
        "n_non_responder": len(non_responders),
        "median_responder": np.median(responders),
        "median_non_responder":
            np.median(non_responders),
        "iqr_responder": _iqr(responders),
        "iqr_non_responder": _iqr(non_responders),
        "u_statistic": u_stat,
        "p_value": p_value,
        "cliffs_delta": _cliffs_delta(responders,
                                      non_responders, u_stat),
    })

    result = pd.DataFrame(rows)
    result["q_value"] = false_discovery_control(result["p_value"], method="bh")
    return result


def population_auc(freq_with_response: pd.DataFrame) -> pd.DataFrame:
    """
    Per-population ROC-AUC: how well does this population's frequency alone
    separate responders from non-responders? responder ('yes') is the positive class.

    `auc` > 0.5 means higher frequency predicts responder; < 0.5 means higher
    frequency predicts non-responder. `auc_abs` = max(auc, 1-auc) is separability
    regardless of direction, so populations can be ranked by predictive strength.
    """
    rows = []
    for population, group in freq_with_response.groupby("population"):
        y_true = (group["response"] == Response.YES).astype(int)
        auc = roc_auc_score(y_true, group["percentage"])
        rows.append({"population": population, "auc": auc, "auc_abs": max(auc, 1 - auc)})

    return pd.DataFrame(rows).sort_values("auc_abs", ascending=False).reset_index(drop=True)


def pca_projection(freq_with_response: pd.DataFrame) -> pd.DataFrame:
    """
    2D PCA of each sample's 5-population frequency profile, to see whether
    responders/non-responders separate on the *overall* profile rather than
    any single population. Standardized first so no single high-frequency
    population (e.g. cd4_t_cell) dominates the variance just by having a
    bigger scale.
    """
    wide = freq_with_response.pivot(index="sample_id", columns="population", values="percentage")
    response_by_sample = (
        freq_with_response[["sample_id", "response"]].drop_duplicates().set_index("sample_id")
    )
    wide = wide.join(response_by_sample)

    features = wide.drop(columns="response")
    scaled = StandardScaler().fit_transform(features)
    components = PCA(n_components=2, random_state=0).fit_transform(scaled)

    return pd.DataFrame({
        "sample_id": wide.index,
        "pc1": components[:, 0],
        "pc2": components[:, 1],
        "response": wide["response"].to_numpy(),
    }).reset_index(drop=True)
