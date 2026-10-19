"""
CMS Doctors & Clinicians, Facility Affiliation, Hospital General ingest script.

Loads downloaded CMS CSV files into DuckDB.
"""

import csv
import sys
from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

RAW_DIR = PROJECT_ROOT / "raw" / "cms"
DB_PATH = PROJECT_ROOT / "db" / "cms_raw.duckdb"


def find_csv_files(directory: Path) -> list:
    """Find all CSV files in the directory."""
    csv_files = []
    if not directory.exists():
        return csv_files
    for f in directory.iterdir():
        if f.is_file() and f.suffix.lower() == ".csv":
            csv_files.append(f)
    return sorted(csv_files)


def load_cms_files(conn: duckdb.DuckDBPyConnection):
    """Load CMS CSV files into DuckDB."""
    csv_files = find_csv_files(RAW_DIR)
    if not csv_files:
        print("WARNING: No CMS CSV files found in", RAW_DIR)
        print("Run download_cms.py first.")
        return

    print(f"Found {len(csv_files)} CMS CSV files to load:")
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

    print("\nCMS ingestion complete.")


def main():
    """Main ingestion entry point."""
    print("=" * 60)
    print("CMS Data Ingestion")
    print("=" * 60)

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(DB_PATH))

    load_cms_files(conn)

    tables = conn.execute("SHOW TABLES").fetchall()
    print(f"\nTables in database: {[t[0] for t in tables]}")

    conn.close()
    print("\nCMS ingestion complete.")


if __name__ == "__main__":
    main()