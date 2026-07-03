"""
Run with `python run_pipeline.py` from repo root.
Reads cell_counts.db and writes outputs/*.csv, outputs/*.png.
"""

import sqlite3
from pathlib import Path

from src.data.repository import get_cell_counts
from src.domain.frequency import compute_frequencies
from src.ui.tables import save_cell_frequencies

DB_PATH = Path(__file__).resolve().parent / "cell_counts.db"


def main() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    try:
        counts = get_cell_counts(conn)
    finally:
        conn.close()

    frequencies = compute_frequencies(counts)
    save_cell_frequencies(frequencies)


if __name__ == "__main__":
    main()