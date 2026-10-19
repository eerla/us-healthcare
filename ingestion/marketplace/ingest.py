"""
CMS Marketplace PUFs ingestion script.

Loads downloaded Marketplace PUF CSV/XLSX files into DuckDB.
"""
import sys
import tempfile
import zipfile
from pathlib import Path
import duckdb
import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

RAW_DIR = PROJECT_ROOT / "raw" / "marketplace"
DB_PATH = PROJECT_ROOT / "db" / "marketplace_raw.duckdb"


# Mapping from file pattern to table name
FILE_TABLE_MAP = {
    "plan-attributes-puf.csv": "raw_plan_attributes",
    "service-area-puf.csv": "raw_service_area",
    "network-puf.csv": "raw_network",
    "business-rules-puf.csv": "raw_business_rules",
    "rate-puf.csv": "raw_rate",
    "benefits-and-cost-sharing-puf.csv": "raw_benefits_cost_sharing",
    "plan-id-crosswalk-puf.csv": "raw_plan_id_crosswalk",
    "machine-readable-url-puf.xlsx": "raw_machine_readable_url",
    "service-area-puf.csv": "raw_service_area",
    "business-rules-puf.csv": "raw_business_rules",
    "rate-puf.csv": "raw_rate",
    "plan-id-crosswalk-puf.csv": "raw_plan_id_crosswalk",
    "benefits-and-cost-sharing-puf.csv": "raw_benefits_cost_sharing",
    "machine-readable-url-puf.xlsx": "raw_machine_readable_url",
    "transparency_in_coverage_puf.xlsx": "raw_transparency_coverage",
}


def extract_and_load_files(conn: duckdb.DuckDBPyConnection):
    """Extract files from ZIP and load into DuckDB."""
    csv_files = []
    xlsx_files = []
    if not RAW_DIR.exists():
        return

    for f in RAW_DIR.iterdir():
        if f.is_file() and f.suffix == '.zip':
            with zipfile.ZipFile(f) as z:
                for name in z.namelist():
                    if name.endswith('.csv'):
                        # Extract to temp file
                        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.csv') as tmp:
                            tmp.write(z.read(name))
                            csv_files.append((name, Path(tmp.name)))
                    elif name.endswith('.xlsx'):
                        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.xlsx') as tmp:
                            tmp.write(z.read(name))
                            xlsx_files.append((name, Path(tmp.name)))

    print(f"Found {len(csv_files)} CSV files and {len(xlsx_files)} XLSX files to load:")

    for name, tmp_path in csv_files:
        table_name = FILE_TABLE_MAP.get(name, f"raw_{name.replace('.csv', '').replace('-', '_')}")
        print(f"\n  Loading: {name} -> {table_name}")
        conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.execute(f"""
            CREATE TABLE {table_name} AS
            SELECT * FROM read_csv(
                '{tmp_path}',
                header=true,
                all_varchar=true
            )
        """)
        row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"    Loaded {row_count:,} rows")
        tmp_path.unlink()

    for name, tmp_path in xlsx_files:
        table_name = FILE_TABLE_MAP.get(name, f"raw_{name.replace('.xlsx', '').replace('-', '_')}")
        print(f"\n  Loading: {name} -> {table_name}")
        conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        # Read with pandas and insert into DuckDB
        df = pd.read_excel(tmp_path)
        conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df")
        row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"    Loaded {row_count:,} rows")
        tmp_path.unlink()

    print("\nMarketplace ingestion complete.")


def load_marketplace_files(conn: duckdb.DuckDBPyConnection):
    """Load Marketplace CSV/XLSX files into DuckDB."""
    extract_and_load_files(conn)


def main():
    """Main ingestion entry point."""
    print("=" * 60)
    print("CMS Marketplace PUFs Ingestion")
    print("=" * 60)

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(DB_PATH))

    load_marketplace_files(conn)

    tables = conn.execute("SHOW TABLES").fetchall()
    print(f"\nTables in database: {[t[0] for t in tables]}")

    conn.close()
    print("\nMarketplace ingestion complete.")


if __name__ == "__main__":
    import zipfile
    import pandas as pd
    import tempfile
    main()