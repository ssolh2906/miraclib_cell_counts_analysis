"""
Part 1 entry point. Run with `python load_data.py` (no args, no -m) from repo root.
Creates cell_counts.db in the repo root and loads data/cell-count.csv into it.
"""

from pathlib import Path

from src.data.database import get_connection, init_schema
from src.data.loader import load_into_db

DB_PATH = Path(__file__).resolve().parent / "cell_counts.db"


def main() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = get_connection(str(DB_PATH))
    try:
        init_schema(conn)
        load_into_db(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
