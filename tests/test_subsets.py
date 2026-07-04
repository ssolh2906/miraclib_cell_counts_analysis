import pandas as pd

from src.domain.subsets import compare_responders_by_sex_melanoma_miraclib_pbmc_baseline
from src.domain.vocab import POPULATION_COLUMNS


def _sample_rows(sample_id: str, sex: str, response: str, b_cell_count: int) -> list[dict]:
    """One synthetic sample: b_cell count varies, other 4 populations fixed at 100 each."""
    rows = []
    for population in POPULATION_COLUMNS:
        count = b_cell_count if population == "b_cell" else 100
        rows.append({
            "sample_id": sample_id,
            "subject_id": sample_id,
            "project_id": "proj1",
            "condition": "melanoma",
            "sex": sex,
            "treatment": "miraclib",
            "response": response,
            "sample_type": "PBMC",
            "time_from_treatment_start": 0,
            "population": population,
            "cell_count": count,
        })
    return rows


def _build_cohort(sex: str, responder_counts: list[int], non_responder_counts: list[int]) -> list[dict]:
    rows = []
    for i, count in enumerate(responder_counts):
        rows.extend(_sample_rows(f"{sex}_r{i}", sex, "yes", count))
    for i, count in enumerate(non_responder_counts):
        rows.extend(_sample_rows(f"{sex}_n{i}", sex, "no", count))
    return rows


def test_compare_responders_by_sex_detects_separated_groups():
    """b_cell % clearly higher for responders in both sexes -> small p, positive difference."""
    rows = _build_cohort("M", [300, 320, 310, 330, 305], [50, 60, 55, 65, 52]) + _build_cohort(
        "F", [300, 320, 310, 330, 305], [50, 60, 55, 65, 52]
    )
    result = compare_responders_by_sex_melanoma_miraclib_pbmc_baseline(pd.DataFrame(rows))

    b_cell_rows = result.loc[result["population"] == "b_cell"]
    assert (b_cell_rows["p_value"] < 0.05).all()
    assert (b_cell_rows["difference"] > 0).all()


def test_compare_responders_by_sex_no_difference():
    """Same (shifted) distribution for responders/non-responders -> p close to 1, difference ~ 0."""
    rows = _build_cohort("M", [10, 20, 30, 40, 50], [15, 25, 35, 45, 55]) + _build_cohort(
        "F", [10, 20, 30, 40, 50], [15, 25, 35, 45, 55]
    )
    result = compare_responders_by_sex_melanoma_miraclib_pbmc_baseline(pd.DataFrame(rows))

    b_cell_rows = result.loc[result["population"] == "b_cell"]
    assert (b_cell_rows["p_value"] > 0.5).all()
    assert (b_cell_rows["difference"].abs() < 5).all()


def test_compare_responders_by_sex_shape_and_columns():
    """2 sexes x 5 populations = 10 rows, in the specified column order."""
    rows = _build_cohort("M", [300, 320, 310, 330, 305], [50, 60, 55, 65, 52]) + _build_cohort(
        "F", [300, 320, 310, 330, 305], [50, 60, 55, 65, 52]
    )
    result = compare_responders_by_sex_melanoma_miraclib_pbmc_baseline(pd.DataFrame(rows))

    assert list(result.columns) == [
        "sex", "population", "n_responder", "n_non_responder",
        "median_responder", "median_non_responder", "difference",
        "u_statistic", "p_value", "q_value",
    ]
    assert len(result) == 2 * len(POPULATION_COLUMNS)
    assert list(result["sex"]) == ["M"] * len(POPULATION_COLUMNS) + ["F"] * len(POPULATION_COLUMNS)
    assert list(result.loc[result["sex"] == "M", "population"]) == POPULATION_COLUMNS
