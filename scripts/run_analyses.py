"""
Run all analysis SQL files and write results to outputs/tables/.

Each SQL file in sql/ is expected to produce a result set that is written
to outputs/tables/{filename}.csv with a header row.
"""

import csv
import sys
from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DB_PATH = PROJECT_ROOT / "db" / "warehouse.duckdb"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "tables"


def run_analyses():
    """Run all SQL analysis files and write CSV outputs."""
    print("=" * 60)
    print("Running Analyses")
    print("=" * 60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    conn = duckdb.connect(str(DB_PATH))

    sql_dir = PROJECT_ROOT / "sql"
    sql_files = sorted([f for f in sql_dir.iterdir() if f.suffix == ".sql"])

    if not sql_files:
        print("WARNING: No SQL analysis files found in sql/")
        conn.close()
        return

    for sql_file in sql_files:
        print(f"\n  Running: {sql_file.name}")
        with open(sql_file, "r") as f:
            query = f.read()

        try:
            result = conn.execute(query).fetchall()
            columns = [d[0] for d in conn.description] if conn.description else []

            # Write to CSV
            output_name = sql_file.stem + ".csv"
            output_path = OUTPUT_DIR / output_name
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(columns)
                writer.writerows(result)

            print(f"    -> {output_path} ({len(result):,} rows)")
        except Exception as e:
            print(f"    ERROR: {e}")

    conn.close()
    print("\nAnalyses complete.")


if __name__ == "__main__":
    run_analyses()