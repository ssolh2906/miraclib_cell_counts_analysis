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