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


def save_melanoma_miraclib_pbmc_baseline_samples(
    samples: pd.DataFrame, path: Path = OUTPUTS_DIR / "melanoma_miraclib_pbmc_baseline_samples.csv"
) -> None:
    """Part 4 step 1: melanoma + miraclib + PBMC samples at baseline (t=0), one row per sample."""
    path.parent.mkdir(parents=True, exist_ok=True)
    samples.to_csv(path, index=False)


def save_cohort_counts(counts: pd.DataFrame, path: Path = OUTPUTS_DIR / "subset_cohort_counts.csv") -> None:
    """Part 4 baseline subset: sample counts per project, subject counts per response/sex."""
    path.parent.mkdir(parents=True, exist_ok=True)
    counts.to_csv(path, index=False)


def save_population_means(
    means: pd.DataFrame, path: Path = OUTPUTS_DIR / "subset_population_means.csv"
) -> None:
    """Part 4 baseline subset: mean cell count per population, by sex and response."""
    path.parent.mkdir(parents=True, exist_ok=True)
    means.to_csv(path, index=False)