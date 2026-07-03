import numpy as np
import pandas as pd
import sqlite3
from pandas.testing import assert_frame_equal
from src.domain.frequency import compute_frequencies


def test_hand_calculated_case():
    """count [10,20,30,40,0] -> total 100 -> % [10,20,30,40,0]."""
    df = pd.DataFrame({
        "sample_id":  ["s1"]*5,
        "population": ["b_cell","cd8_t_cell","cd4_t_cell","nk_cell","monocyte"],
        "cell_count": [10, 20, 30, 40, 0],
    })
    out = compute_frequencies(df)
    assert (out["total_count"] == 100).all()
    got = dict(zip(out["population"], out["percentage"]))
    assert got["b_cell"] == 10.0 and got["nk_cell"] == 40.0 and got["monocyte"] == 0.0


def test_percentages_sum_to_100_per_sample():
    """Oracle test. Sum of percentages should be always 100 per samples"""
    df = pd.DataFrame({
        "sample_id":  ["s1","s1","s2","s2"],
        "population": ["b_cell","nk_cell","b_cell","nk_cell"],
        "cell_count": [3, 7, 1, 1],
    })
    out = compute_frequencies(df)
    sums = out.groupby("sample_id")["percentage"].sum()
    assert np.allclose(sums.values, 100.0)


def test_matches_sql_view():
    """cross check frequencies with SQLVIEW"""
    con = sqlite3.connect("cell_counts.db")
    raw = pd.read_sql("SELECT sample_id, population, cell_count FROM cell_counts", con)
    view = pd.read_sql("SELECT sample_id, total_count, population, cell_count, percentage "
                       "FROM cell_frequencies", con)
    con.close()

    got = compute_frequencies(raw)
    keys = ["sample_id","population"]
    got = got.sort_values(keys).reset_index(drop=True)
    view = view[got.columns].sort_values(keys).reset_index(drop=True)
    assert_frame_equal(got, view, check_exact=False, atol=1e-3)