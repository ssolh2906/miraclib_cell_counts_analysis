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
            subj.subject_id, subj.project_id, subj.condition, subj.age, subj.sex,
            subj.treatment, subj.response,
            sm.sample_id, sm.sample_type, sm.time_from_treatment_start,
            cc.population, cc.cell_count
        FROM cell_counts cc
        JOIN samples sm ON cc.sample_id = sm.sample_id
        JOIN subjects subj ON sm.subject_id = subj.subject_id
    """
    return pd.read_sql(query, conn)


def get_baseline_miraclib_melanoma_pbmc_samples(conn: sqlite3.Connection) -> pd.DataFrame:
    """Part 4 step 1: identify all melanoma PBMC samples at baseline (t=0) from
    patients treated with miraclib. One row per sample."""
    query = """
        SELECT sm.sample_id, subj.project_id, subj.subject_id, subj.sex, subj.response
        FROM samples sm
        JOIN subjects subj ON sm.subject_id = subj.subject_id
        WHERE subj.condition = 'melanoma' AND subj.treatment = 'miraclib'
          AND sm.sample_type = 'PBMC' AND sm.time_from_treatment_start = 0
    """
    return pd.read_sql(query, conn)


def get_melanoma_miraclib_pbmc_baseline_samples_per_project(conn: sqlite3.Connection) -> pd.DataFrame:
    """Part 4 extension: sample count per project, within the baseline subset."""
    query = """
        SELECT subj.project_id, COUNT(*) AS sample_count
        FROM samples sm
        JOIN subjects subj ON sm.subject_id = subj.subject_id
        WHERE subj.condition = 'melanoma' AND subj.treatment = 'miraclib'
          AND sm.sample_type = 'PBMC' AND sm.time_from_treatment_start = 0
        GROUP BY subj.project_id
    """
    return pd.read_sql(query, conn)


def get_melanoma_miraclib_pbmc_baseline_subjects_per_response(conn: sqlite3.Connection) -> pd.DataFrame:
    """Part 4 extension: responder/non-responder subject count, within the baseline subset."""
    query = """
        SELECT subj.response, COUNT(DISTINCT subj.subject_id) AS subject_count
        FROM samples sm
        JOIN subjects subj ON sm.subject_id = subj.subject_id
        WHERE subj.condition = 'melanoma' AND subj.treatment = 'miraclib'
          AND sm.sample_type = 'PBMC' AND sm.time_from_treatment_start = 0
        GROUP BY subj.response
    """
    return pd.read_sql(query, conn)


def get_melanoma_miraclib_pbmc_baseline_subjects_per_sex(conn: sqlite3.Connection) -> pd.DataFrame:
    """Part 4 extension: male/female subject count, within the baseline subset."""
    query = """
        SELECT subj.sex, COUNT(DISTINCT subj.subject_id) AS subject_count
        FROM samples sm
        JOIN subjects subj ON sm.subject_id = subj.subject_id
        WHERE subj.condition = 'melanoma' AND subj.treatment = 'miraclib'
          AND sm.sample_type = 'PBMC' AND sm.time_from_treatment_start = 0
        GROUP BY subj.sex
    """
    return pd.read_sql(query, conn)