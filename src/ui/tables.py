"""
Output-table formatting: domain results -> outputs/*.csv.
Align column names with specification, round percentages to 4 decimal places.
"""

from pathlib import Path

import pandas as pd

OUTPUTS_DIR = Path(__file__).resolve().parents[2] / "outputs"


def save_cell_frequencies(frequencies: pd.DataFrame, path: Path = OUTPUTS_DIR / "cell_frequencies.csv") -> None:
    out = frequencies.rename(columns={"sample_id": "sample", "cell_count": "count"})
    out = out[["sample", "total_count", "population", "count", "percentage"]]
    out["percentage"] = out["percentage"].round(4)
    path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(path, index=False)


def save_response_stats(stats: pd.DataFrame, path: Path = OUTPUTS_DIR / "response_stats.csv") -> None:
    """Part 3 Mann-Whitney(p)/effect-size(cliifs_delta)/BH results(q), one row per population."""
    round_cols = [
        "median_responder", "median_non_responder", "iqr_responder", "iqr_non_responder",
        "cliffs_delta", "p_value", "q_value",
    ]
    out = stats.copy()
    out[round_cols] = out[round_cols].round(4)
    path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(path, index=False)


def save_subset_summary(summary: pd.DataFrame, path: Path = OUTPUTS_DIR / "subset_summary.csv") -> None:
    """Part 4 baseline subset: (metric, group, value) rows, incl. headline B-cell mean."""
    path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(path, index=False)