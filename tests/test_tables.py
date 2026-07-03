import pandas as pd

from src.ui.tables import save_response_stats


def _toy_stats() -> pd.DataFrame:
    """One population's compare_responders-shaped row."""
    return pd.DataFrame([{
        "population": "b_cell",
        "n_responder": 331,
        "n_non_responder": 325,
        "median_responder": 9.785035,
        "median_non_responder": 9.758175,
        "iqr_responder": 4.211664,
        "iqr_non_responder": 4.030093,
        "u_statistic": 55244.0,
        "p_value": 0.548541,
        "cliffs_delta": 0.027079,
        "q_value": 0.885328,
    }])


def test_save_response_stats_writes_expected_columns(tmp_path):
    path = tmp_path / "response_stats.csv"
    save_response_stats(_toy_stats(), path=path)

    out = pd.read_csv(path)
    assert list(out.columns) == [
        "population", "n_responder", "n_non_responder",
        "median_responder", "median_non_responder",
        "iqr_responder", "iqr_non_responder",
        "u_statistic", "p_value", "cliffs_delta", "q_value",
    ]
    assert out.loc[0, "population"] == "b_cell"


def test_save_response_stats_rounds_to_4_decimals(tmp_path):
    path = tmp_path / "response_stats.csv"
    save_response_stats(_toy_stats(), path=path)

    out = pd.read_csv(path)
    assert out.loc[0, "p_value"] == 0.5485
    assert out.loc[0, "cliffs_delta"] == 0.0271
