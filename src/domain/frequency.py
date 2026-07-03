"""
Relative cell-type frequency per sample.
"""

import pandas as pd


def compute_frequencies(counts: pd.DataFrame) -> pd.DataFrame:
    """
    counts: long df with columns ['sample_id', 'population', 'cell_count'].
    returns: columns ['sample_id', 'total_count', 'population', 'cell_count', 'percentage'],
             sorted by sample_id then population. percentage is full precision (no rounding).
    """
    out = counts.copy()
    out["total_count"] = out.groupby("sample_id")["cell_count"].transform("sum")
    out["percentage"] = out["cell_count"] / out["total_count"] * 100
    out = out.sort_values(["sample_id", "population"]).reset_index(drop=True)
    return out[["sample_id", "total_count", "population", "cell_count", "percentage"]]