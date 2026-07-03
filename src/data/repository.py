"""
DB read queries -> DataFrames for the domain layer.
"""

import sqlite3

import pandas as pd


def get_cell_counts(conn: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql("SELECT sample_id, population, cell_count FROM cell_counts", conn)


def get_annotated_cell_counts(conn: sqlite3.Connection) -> pd.DataFrame:
    """Long-format cell counts joined with subject + sample metadata.

    One row per (sample, population). Kept unfiltered here so the domain
    layer owns which subset (condition/treatment/sample_type/timepoint)
    each analysis needs.
    """
    query = """
        SELECT
            subj.subject_id, subj.condition, subj.age, subj.sex,
            subj.treatment, subj.response,
            sm.sample_id, sm.sample_type, sm.time_from_treatment_start,
            cc.population, cc.cell_count
        FROM cell_counts cc
        JOIN samples sm ON cc.sample_id = sm.sample_id
        JOIN subjects subj ON sm.subject_id = subj.subject_id
    """
    return pd.read_sql(query, conn)