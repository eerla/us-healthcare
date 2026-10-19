"""
Run all dbt-style SQL transformations in dependency order.

Single connection: attach databases, then create staging/core/mart TABLEs
all referencing the attached raw databases. All runs in one connection
so attachments persist for the entire pipeline.
"""

import sys
from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DB_PATH = PROJECT_ROOT / "db" / "warehouse.duckdb"

# Ordered list of SQL files to apply (dependencies first)
SQL_FILES = [
    # Staging (creates TABLEs from attached raw databases)
    "staging/stg_npi.sql",
    "staging/stg_npi_location.sql",
    "staging/stg_npi_other_names.sql",
    "staging/stg_npi_endpoints.sql",
    "staging/stg_population.sql",
    "staging/stg_population_county.sql",
    "staging/stg_clinician.sql",
    "staging/stg_affiliation.sql",
    "staging/stg_hospital.sql",
    "staging/stg_utilization.sql",
    "staging/stg_provider_service.sql",
    # Marketplace staging
    "staging/stg_marketplace_plan.sql",
    "staging/stg_marketplace_service_area.sql",
    "staging/stg_marketplace_network.sql",
    "staging/stg_marketplace_rate.sql",
    "staging/stg_marketplace_benefits.sql",
    "staging/stg_marketplace_business_rules.sql",
    "staging/stg_marketplace_plan_crosswalk.sql",
    "staging/stg_marketplace_machine_readable_url.sql",
    "staging/stg_marketplace_transparency_coverage.sql",
    # Core dimensions (creates TABLEs from staging)
    "core/dim_provider.sql",
    "core/dim_location.sql",
    "core/dim_specialty.sql",
    "core/bridge_provider_location.sql",
    "core/fact_population.sql",
    "core/dim_organization.sql",
    "core/dim_facility.sql",
    "core/bridge_provider_group.sql",
    "core/bridge_provider_facility.sql",
    "core/fact_provider_utilization.sql",
    "core/fact_provider_service.sql",
    # Marts (creates TABLEs from core)
    "mart/mart_provider_supply.sql",
    "mart/mart_specialty_supply.sql",
    "mart/mart_geographic_access.sql",
    "mart/mart_provider_concentration.sql",
    "mart/mart_facility_ecosystem.sql",
]


def run_transform():
    """Apply all SQL files in order."""
    print("=" * 60)
    print("Running Transformations")
    print("=" * 60)

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Connect to the warehouse database
    conn = duckdb.connect(str(DB_PATH))

    # Ensure schemas exist
    for schema in ["staging", "core", "mart"]:
        conn.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")

    # Attach raw databases (will persist for this connection)
    nppes_path = PROJECT_ROOT / "db" / "nppes_raw.duckdb"
    if nppes_path.exists():
        conn.execute(f"ATTACH '{nppes_path}' AS nppes_raw (READ_ONLY)")
        print("  Attached: nppes_raw.duckdb")

    census_path = PROJECT_ROOT / "db" / "census_raw.duckdb"
    if census_path.exists():
        conn.execute(f"ATTACH '{census_path}' AS census_raw (READ_ONLY)")
        print("  Attached: census_raw.duckdb")

    cms_path = PROJECT_ROOT / "db" / "cms_raw.duckdb"
    if cms_path.exists():
        conn.execute(f"ATTACH '{cms_path}' AS cms_raw (READ_ONLY)")
        print("  Attached: cms_raw.duckdb")

    utilization_path = PROJECT_ROOT / "db" / "utilization_raw.duckdb"
    if utilization_path.exists():
        conn.execute(f"ATTACH '{utilization_path}' AS utilization_raw (READ_ONLY)")
        print("  Attached: utilization_raw.duckdb")

    marketplace_path = PROJECT_ROOT / "db" / "marketplace_raw.duckdb"
    if marketplace_path.exists():
        conn.execute(f"ATTACH '{marketplace_path}' AS marketplace_raw (READ_ONLY)")
        print("  Attached: marketplace_raw.duckdb")

    # Drop existing staging views/tables to allow type change
    for schema in ["staging", "core", "mart"]:
        tables = conn.execute(
            f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema}'"
        ).fetchall()
        for (table,) in tables:
            conn.execute(f"DROP TABLE IF EXISTS {schema}.{table}")
            conn.execute(f"DROP VIEW IF EXISTS {schema}.{table}")

    # Apply each SQL file - all run in same connection with attachments alive
    for sql_file in SQL_FILES:
        path = PROJECT_ROOT / sql_file
        if not path.exists():
            print(f"  WARNING: {sql_file} not found, skipping")
            continue

        print(f"\n  Applying: {sql_file}")
        with open(path, "r") as f:
            sql = f.read()
        try:
            conn.execute(sql)
            print(f"    OK")
        except Exception as e:
            print(f"    ERROR: {e}")
            conn.close()
            raise

    # Summary
    print("\n" + "=" * 60)
    print("Transform Summary")
    print("=" * 60)

    for schema in ["staging", "core", "mart"]:
        tables = conn.execute(
            f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema}'"
        ).fetchall()
        print(f"\n  {schema}:")
        for (table,) in tables:
            try:
                cnt = conn.execute(f'SELECT COUNT(*) FROM "{schema}"."{table}"').fetchone()[0]
                print(f"    {table}: {cnt:,} rows")
            except Exception:
                print(f"    {table}: (view)")

    conn.close()
    print("\nTransform complete.")


if __name__ == "__main__":
    run_transform()