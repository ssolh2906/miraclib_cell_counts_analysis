import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

from src.domain.statistics import _cliffs_delta, compare_responders


def test_cliffs_delta_complete_separation():
    """Every x bigger than every y -> delta = +1 (x always 'wins' the pairwise comparison)."""
    x, y = np.array([10, 11, 12]), np.array([1, 2, 3])
    u_stat, _ = mannwhitneyu(x, y, alternative="two-sided")
    assert _cliffs_delta(x, y, u_stat) == 1.0


def test_cliffs_delta_complete_reversal():
    """Every x smaller than every y -> delta = -1."""
    x, y = np.array([1, 2, 3]), np.array([10, 11, 12])
    u_stat, _ = mannwhitneyu(x, y, alternative="two-sided")
    assert _cliffs_delta(x, y, u_stat) == -1.0


def test_cliffs_delta_identical_distributions():
    """Same values in both groups -> no tendency either way -> delta = 0."""
    x, y = np.array([1, 2, 3, 4]), np.array([1, 2, 3, 4])
    u_stat, _ = mannwhitneyu(x, y, alternative="two-sided")
    assert _cliffs_delta(x, y, u_stat) == 0.0


def _toy_frequencies(responder_values: dict, non_responder_values: dict) -> pd.DataFrame:
    """Build a compare_responders-shaped df: one population, given per-sample percentages."""
    rows = []
    for i, pct in enumerate(responder_values):
        rows.append({"sample_id": f"r{i}", "population": "b_cell", "percentage": pct, "response": "yes"})
    for i, pct in enumerate(non_responder_values):
        rows.append({"sample_id": f"n{i}", "population": "b_cell", "percentage": pct, "response": "no"})
    return pd.DataFrame(rows)


def test_compare_responders_detects_separated_groups():
    """Responder % clearly higher than non-responder % -> small p-value, positive delta."""
    df = _toy_frequencies(
        responder_values=[30, 32, 35, 33, 31],
        non_responder_values=[10, 12, 15, 13, 11],
    )
    result = compare_responders(df)
    row = result.iloc[0]
    assert row["p_value"] < 0.05
    assert row["cliffs_delta"] == 1.0


def test_compare_responders_no_difference():
    """Same distribution in both groups -> large p-value, delta near 0."""
    df = _toy_frequencies(
        responder_values=[10, 20, 30, 40, 50],
        non_responder_values=[15, 25, 35, 45, 55],
    )
    result = compare_responders(df)
    row = result.iloc[0]
    assert row["p_value"] > 0.5
    assert abs(row["cliffs_delta"]) < 0.3