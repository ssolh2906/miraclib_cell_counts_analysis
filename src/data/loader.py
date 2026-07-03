"""
CSV -> DB loading (Part 1).

Reads the wide cell-count.csv (one row per sample, one column per population)
and populates the normalized schema: projects, subjects, samples, populations,
cell_counts (long format).
"""

import sqlite3
from pathlib import Path

import pandas as pd

from src.domain.vocab import POPULATION_COLUMNS

CSV_PATH = Path(__file__).resolve().parents[2] / "data" / "cell-count.csv"

SUBJECT_COLUMNS = ["subject", "project", "condition", "age", "sex", "treatment", "response"]
SAMPLE_COLUMNS = ["sample", "subject", "sample_type", "time_from_treatment_start"]


def _nullable(df: pd.DataFrame) -> pd.DataFrame:
    """Replace pandas NaN with None so NULLs are inserted, not the string 'NaN'."""
    return df.astype(object).where(pd.notna(df), None)


def load_csv(csv_path: Path = CSV_PATH) -> pd.DataFrame:
    return pd.read_csv(csv_path)


def load_into_db(conn: sqlite3.Connection, csv_path: Path = CSV_PATH) -> None:
    df = load_csv(csv_path)

    projects = _nullable(df[["project"]].drop_duplicates().rename(columns={"project": "project_id"}))
    conn.executemany(
        "INSERT INTO projects (project_id, name) VALUES (?, NULL)",
        projects.itertuples(index=False, name=None),
    )

    subjects = _nullable(df[SUBJECT_COLUMNS].drop_duplicates(subset=["subject"]))
    conn.executemany(
        """
        INSERT INTO subjects (subject_id, project_id, condition, age, sex, treatment, response)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        subjects[["subject", "project", "condition", "age", "sex", "treatment", "response"]]
        .itertuples(index=False, name=None),
    )

    samples = _nullable(df[SAMPLE_COLUMNS])
    conn.executemany(
        """
        INSERT INTO samples (sample_id, subject_id, sample_type, time_from_treatment_start)
        VALUES (?, ?, ?, ?)
        """,
        samples[["sample", "subject", "sample_type", "time_from_treatment_start"]]
        .itertuples(index=False, name=None),
    )

    conn.executemany(
        "INSERT INTO populations (population) VALUES (?)",
        [(p,) for p in POPULATION_COLUMNS],
    )

    long_df = df.melt(
        id_vars=["sample"],
        value_vars=POPULATION_COLUMNS,
        var_name="population",
        value_name="cell_count",
    )
    conn.executemany(
        "INSERT INTO cell_counts (sample_id, population, cell_count) VALUES (?, ?, ?)",
        long_df[["sample", "population", "cell_count"]].itertuples(index=False, name=None),
    )

    conn.commit()