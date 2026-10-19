"""
NPPES ingestion script - optimized version.

Loads downloaded NPPES CSV files into DuckDB using polars for large files.
Creates staging tables and validates data quality.
"""

import sys
import json
from pathlib import Path
import duckdb
import polars as pl

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

RAW_DIR = PROJECT_ROOT / "raw" / "nppes"
DB_PATH = PROJECT_ROOT / "db" / "nppes_raw.duckdb"
MANIFEST_PATH = PROJECT_ROOT / "manifests" / "source_manifest.csv"

# Columns to load from the main NPI data file (npidata)
NPIDATA_COLUMNS = [
    "NPI",
    "Entity Type Code",
    "Replacement NPI",
    "Employer Identification Number (EIN)",
    "Provider Organization Name (Legal Business Name)",
    "Provider Last Name (Legal Name)",
    "Provider First Name",
    "Provider Middle Name",
    "Provider Name Prefix Text",
    "Provider Name Suffix Text",
    "Provider Credential Text",
    "Provider Other Organization Name",
    "Provider Other Organization Name Type Code",
    "Provider Other Last Name",
    "Provider Other First Name",
    "Provider Other Middle Name",
    "Provider Other Name Prefix Text",
    "Provider Other Name Suffix Text",
    "Provider Other Credential Text",
    "Provider Other Last Name Type Code",
    "Provider First Line Business Mailing Address",
    "Provider Second Line Business Mailing Address",
    "Provider Business Mailing Address City Name",
    "Provider Business Mailing Address State Name",
    "Provider Business Mailing Address Postal Code",
    "Provider Business Mailing Address Country Code (If outside U.S.)",
    "Provider Business Mailing Address Telephone Number",
    "Provider Business Mailing Address Fax Number",
    "Provider First Line Business Practice Location Address",
    "Provider Second Line Business Practice Location Address",
    "Provider Business Practice Location Address City Name",
    "Provider Business Practice Location Address State Name",
    "Provider Business Practice Location Address Postal Code",
    "Provider Business Practice Location Address Country Code (If outside U.S.)",
    "Provider Business Practice Location Address Telephone Number",
    "Provider Business Practice Location Address Fax Number",
    "Provider Enumeration Date",
    "Last Update Date",
    "NPI Deactivation Reason Code",
    "NPI Deactivation Date",
    "NPI Reactivation Date",
    "Provider Sex Code",
    "Authorized Official Last Name",
    "Authorized Official First Name",
    "Authorized Official Middle Name",
    "Authorized Official Title or Position",
    "Authorized Official Telephone Number",
    "Healthcare Provider Taxonomy Code_1",
    "Provider License Number_1",
    "Provider License Number State Code_1",
    "Healthcare Provider Primary Taxonomy Switch_1",
    "Healthcare Provider Taxonomy Code_2",
    "Provider License Number_2",
    "Provider License Number State Code_2",
    "Healthcare Provider Primary Taxonomy Switch_2",
    "Healthcare Provider Taxonomy Code_3",
    "Provider License Number_3",
    "Provider License Number State Code_3",
    "Healthcare Provider Primary Taxonomy Switch_3",
    "Healthcare Provider Taxonomy Code_4",
    "Provider License Number_4",
    "Provider License Number State Code_4",
    "Healthcare Provider Primary Taxonomy Switch_4",
    "Healthcare Provider Taxonomy Code_5",
    "Provider License Number_5",
    "Provider License Number State Code_5",
    "Healthcare Provider Primary Taxonomy Switch_5",
    "Healthcare Provider Taxonomy Code_6",
    "Provider License Number_6",
    "Provider License Number State Code_6",
    "Healthcare Provider Primary Taxonomy Switch_6",
    "Healthcare Provider Taxonomy Code_7",
    "Provider License Number_7",
    "Provider License Number State Code_7",
    "Healthcare Provider Primary Taxonomy Switch_7",
    "Healthcare Provider Taxonomy Code_8",
    "Provider License Number_8",
    "Provider License Number State Code_8",
    "Healthcare Provider Primary Taxonomy Switch_8",
    "Healthcare Provider Taxonomy Code_9",
    "Provider License Number_9",
    "Provider License Number State Code_9",
    "Healthcare Provider Primary Taxonomy Switch_9",
    "Healthcare Provider Taxonomy Code_10",
    "Provider License Number_10",
    "Provider License Number State Code_10",
    "Healthcare Provider Primary Taxonomy Switch_10",
    "Healthcare Provider Taxonomy Code_11",
    "Provider License Number_11",
    "Provider License Number State Code_11",
    "Healthcare Provider Primary Taxonomy Switch_11",
    "Healthcare Provider Taxonomy Code_12",
    "Provider License Number_12",
    "Provider License Number State Code_12",
    "Healthcare Provider Primary Taxonomy Switch_12",
    "Healthcare Provider Taxonomy Code_13",
    "Provider License Number_13",
    "Provider License Number State Code_13",
    "Healthcare Provider Primary Taxonomy Switch_13",
    "Healthcare Provider Taxonomy Code_14",
    "Provider License Number_14",
    "Provider License Number State Code_14",
    "Healthcare Provider Primary Taxonomy Switch_14",
    "Healthcare Provider Taxonomy Code_15",
    "Provider License Number_15",
    "Provider License Number State Code_15",
    "Healthcare Provider Primary Taxonomy Switch_15",
    "Other Provider Identifier_1",
    "Other Provider Identifier Type Code_1",
    "Other Provider Identifier State_1",
    "Other Provider Identifier Issuer_1",
    "Other Provider Identifier_2",
    "Other Provider Identifier Type Code_2",
    "Other Provider Identifier State_2",
    "Other Provider Identifier Issuer_2",
    "Other Provider Identifier_3",
    "Other Provider Identifier Type Code_3",
    "Other Provider Identifier State_3",
    "Other Provider Identifier Issuer_3",
    "Other Provider Identifier_4",
    "Other Provider Identifier Type Code_4",
    "Other Provider Identifier State_4",
    "Other Provider Identifier Issuer_4",
    "Other Provider Identifier_5",
    "Other Provider Identifier Type Code_5",
    "Other Provider Identifier State_5",
    "Other Provider Identifier Issuer_5",
    "Is Sole Proprietor",
    "Is Organization Subpart",
    "Parent Organization LBN",
    "Parent Organization TIN",
    "Authorized Official Name Prefix Text",
    "Authorized Official Name Suffix Text",
    "Authorized Official Credential Text",
    "Healthcare Provider Taxonomy Group_1",
    "Healthcare Provider Taxonomy Group_2",
    "Healthcare Provider Taxonomy Group_3",
    "Healthcare Provider Taxonomy Group_4",
    "Healthcare Provider Taxonomy Group_5",
    "Healthcare Provider Taxonomy Group_6",
    "Healthcare Provider Taxonomy Group_7",
    "Healthcare Provider Taxonomy Group_8",
    "Healthcare Provider Taxonomy Group_9",
    "Healthcare Provider Taxonomy Group_10",
    "Healthcare Provider Taxonomy Group_11",
    "Healthcare Provider Taxonomy Group_12",
    "Healthcare Provider Taxonomy Group_13",
    "Healthcare Provider Taxonomy Group_14",
    "Healthcare Provider Taxonomy Group_15",
    "Certification Date",
]


def find_csv_files(directory: Path) -> list:
    """Find all CSV files in the directory, excluding the zip file and fileheaders."""
    csv_files = []
    for f in directory.iterdir():
        if f.is_file() and f.suffix.lower() == ".csv" and not f.name.endswith("_fileheader.csv"):
            csv_files.append(f)
    return sorted(csv_files)


def load_npidata_with_polars(conn: duckdb.DuckDBPyConnection):
    """Load the main NPI data file using polars for speed."""
    npidata_file = RAW_DIR / "npidata_pfile_20050523-20260913.csv"
    if not npidata_file.exists():
        print(f"ERROR: {npidata_file} not found")
        return

    print(f"\n  Loading npidata with polars (this may take a minute)...")
    df = pl.read_csv(
        npidata_file,
        columns=NPIDATA_COLUMNS,
        infer_schema_length=10000,
        truncate_ragged_lines=True,
    )
    print(f"    Read {len(df):,} rows, {len(df.columns)} columns")

    # Normalize NPI to 10-char string
    df = df.with_columns(pl.col("NPI").cast(pl.Utf8).str.pad_start(10, "0"))

    # Write to DuckDB
    conn.execute("DROP TABLE IF EXISTS raw_npidata_pfile_20050523_20260913")
    conn.register("npidata_df", df)
    conn.execute("CREATE TABLE raw_npidata_pfile_20050523_20260913 AS SELECT * FROM npidata_df")
    conn.unregister("npidata_df")
    print(f"    Loaded into raw_npidata_pfile_20050523_20260913")


def load_other_files(conn: duckdb.DuckDBPyConnection):
    """Load other NPPES files (endpoints, other names, practice locations) with DuckDB."""
    csv_files = find_csv_files(RAW_DIR)
    csv_files = [f for f in csv_files if f.name != "npidata_pfile_20050523-20260913.csv"]

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
        print(f"    Loaded {row_count:,} rows into {table_name}")


def profile_tables(conn: duckdb.DuckDBPyConnection):
    """Profile loaded tables."""
    tables = conn.execute("SHOW TABLES").fetchall()
    profiles = []

    print("\n" + "=" * 60)
    print("NPPES Ingestion Summary")
    print("=" * 60)

    for (table_name,) in tables:
        if not table_name.startswith("raw_"):
            continue

        row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        columns = [c[0] for c in conn.execute(f"SELECT * FROM {table_name} LIMIT 0").description]

        # Null rates for key columns
        key_cols = ["NPI", "Entity Type Code", "Legal Business Name", "City", "State", "Zip Code"]
        null_rates = {}
        for col in key_cols:
            # Find matching column (case-insensitive, handle different naming)
            matching_col = None
            for c in columns:
                if c.lower() == col.lower():
                    matching_col = c
                    break
            if matching_col:
                null_count = conn.execute(f'SELECT COUNT(*) FROM {table_name} WHERE "{matching_col}" IS NULL').fetchone()[0]
                null_rate = null_count / row_count if row_count > 0 else 0
                null_rates[col] = null_rate

        print(f"  {table_name}: {row_count:,} rows, {len(columns)} columns")
        profiles.append({
            "table": table_name,
            "file": table_name.replace("raw_", "") + ".csv",
            "row_count": row_count,
            "columns": columns,
            "null_rates": null_rates,
        })

    # Save profiles
    profile_path = PROJECT_ROOT / "manifests" / "nppes_profiles.json"
    with open(profile_path, "w") as f:
        json.dump(profiles, f, indent=2, default=str)
    print(f"\nProfiles saved to: {profile_path}")


def main():
    """Main ingestion entry point."""
    print("=" * 60)
    print("NPPES Ingestion (Optimized)")
    print("=" * 60)

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Connect to DuckDB
    conn = duckdb.connect(str(DB_PATH))
    print(f"DuckDB database: {DB_PATH}")

    # Load main NPI data with polars
    load_npidata_with_polars(conn)

    # Load other files with DuckDB
    load_other_files(conn)

    # Profile
    profile_tables(conn)

    # Validate
    print("\n" + "=" * 60)
    print("Validation")
    print("=" * 60)

    tables = conn.execute("SHOW TABLES").fetchall()
    print(f"Tables in database: {[t[0] for t in tables]}")

    conn.close()
    print("\nNPPES ingestion complete.")


if __name__ == "__main__":
    main()