"""
Census ACS 5-Year ingest script.

Loads Census ACS population data into DuckDB and creates staging models.
"""

import csv
import sys
from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

RAW_DIR = PROJECT_ROOT / "raw" / "census"
DB_PATH = PROJECT_ROOT / "db" / "census_raw.duckdb"

ACS_YEAR = 2023


def find_csv_files(directory: Path) -> list:
    """Find all Census CSV files in the directory."""
    csv_files = []
    if not directory.exists():
        return csv_files
    for f in directory.iterdir():
        if f.is_file() and f.suffix.lower() == ".csv":
            csv_files.append(f)
    return sorted(csv_files)


def load_census_files(conn: duckdb.DuckDBPyConnection):
    """Load Census CSV files into DuckDB."""
    csv_files = find_csv_files(RAW_DIR)
    if not csv_files:
        print("WARNING: No Census CSV files found in", RAW_DIR)
        print("Run download_census.py first.")
        return

    print(f"Found {len(csv_files)} Census CSV files to load:")
    for f in csv_files:
        print(f"  - {f.name}")

    for csv_file in csv_files:
        table_name = f"raw_{csv_file.stem.lower().replace(' ', '_').replace('-', '_')}"
        print(f"\n  Loading: {csv_file.name}")
        conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.execute(f"""
            CREATE TABLE {table_name} AS
            SELECT * FROM read_csv(
                '{csv_file}',
                header=true,
                all_varchar=true
            )
        """)
        row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"    Loaded into {table_name}: {row_count:,} rows")

    print("\nCensus ingestion complete.")


def main():
    """Main ingestion entry point."""
    print("=" * 60)
    print("Census ACS Ingestion")
    print("=" * 60)

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(DB_PATH))

    load_census_files(conn)

    tables = conn.execute("SHOW TABLES").fetchall()
    print(f"\nTables in database: {[t[0] for t in tables]}")

    conn.close()
    print("\nCensus ingestion complete.")


if __name__ == "__main__":
    main()