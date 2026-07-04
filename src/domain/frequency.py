"""
Relative cell-type frequency per sample.
"""

import pandas as pd

from src.domain.vocab import POPULATION_COLUMNS


def compute_frequencies(counts: pd.DataFrame) -> pd.DataFrame:
    """
    counts: long df with columns ['sample_id', 'population', 'cell_count'].
    returns: columns ['sample_id', 'total_count', 'population', 'cell_count', 'percentage'],
             sorted by sample_id then population (canonical order). percentage is full
             precision (no rounding).
    """
    out = counts.copy()
    out["total_count"] = out.groupby("sample_id")["cell_count"].transform("sum")
    out["percentage"] = out["cell_count"] / out["total_count"] * 100
    out["population"] = pd.Categorical(out["population"], categories=POPULATION_COLUMNS, ordered=True)
    out = out.sort_values(["sample_id", "population"]).reset_index(drop=True)
    out["population"] = out["population"].astype(str)
    return out[["sample_id", "total_count", "population", "cell_count", "percentage"]]


# Sample/subject metadata carried alongside the frequency numbers so the
# dashboard can filter Part 2 by cohort. Kept out of compute_frequencies (which
# is cross-checked against the bare SQL view) to avoid changing that contract.
METADATA_COLUMNS = [
    "subject_id",
    "project_id",
    "condition",
    "sex",
    "treatment",
    "response",
    "sample_type",
    "time_from_treatment_start",
]


def compute_frequencies_with_metadata(annotated: pd.DataFrame) -> pd.DataFrame:
    """
    annotated: long df with ['sample_id', 'population', 'cell_count'] plus the
        subject/sample metadata columns in METADATA_COLUMNS.
    returns: same per-sample percentages as compute_frequencies, with the
        metadata columns retained (one row per sample x population).
    """
    out = annotated.copy()
    out["total_count"] = out.groupby("sample_id")["cell_count"].transform("sum")
    out["percentage"] = out["cell_count"] / out["total_count"] * 100
    out["population"] = pd.Categorical(out["population"], categories=POPULATION_COLUMNS, ordered=True)
    out = out.sort_values(["sample_id", "population"]).reset_index(drop=True)
    out["population"] = out["population"].astype(str)
    ordered = (
        ["sample_id"]
        + METADATA_COLUMNS
        + ["total_count", "population", "cell_count", "percentage"]
    )
    return out[ordered]