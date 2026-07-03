"""
DB read queries -> DataFrames for the domain layer.
"""

import sqlite3

import pandas as pd


def get_cell_counts(conn: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql("SELECT sample_id, population, cell_count FROM cell_counts", conn)