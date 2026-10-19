"""
Run all analyses with parameter substitution.
"""
import duckdb
import time
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import config

def run_analysis(conn: duckdb.DuckDBPyConnection, label: str, sql_file: str, params: dict = None) -> float:
    """Run a single analysis with parameter substitution."""
    sql_path = Path(__file__).resolve().parent / sql_file
    if not sql_path.exists():
        print(f'{sql_file}: ERROR - File not found')
        return 0.0
    
    sql = open(sql_path).read()
    
    # Substitute parameters
    if params:
        for key, value in params.items():
            placeholder = f'${{{key}}}'
            if isinstance(value, str):
                sql = sql.replace(placeholder, f"'{value}'")
            else:
                sql = sql.replace(placeholder, str(value))
    
    start = time.time()
    try:
        conn.execute(sql)
        elapsed = time.time() - start
        print(f'{Path(sql_file).name}: {elapsed:.1f}s OK')
        return elapsed
    except Exception as e:
        print(f'{Path(sql_file).name}: ERROR - {e}')
        return 0.0

def main():
    print("=" * 60)
    print("Running Analyses")
    print("=" * 60)
    
    conn = duckdb.connect('db/warehouse.duckdb')
    conn.execute("ATTACH 'db/nppes_raw.duckdb' AS nppes_raw (READ_ONLY)")
    conn.execute("ATTACH 'db/census_raw.duckdb' AS census_raw (READ_ONLY)")
    conn.execute("ATTACH 'db/cms_raw.duckdb' AS cms_raw (READ_ONLY)")
    conn.execute("ATTACH 'db/utilization_raw.duckdb' AS utilization_raw (READ_ONLY)")
    conn.execute("ATTACH 'db/marketplace_raw.duckdb' AS marketplace_raw (READ_ONLY)")
    
    params = {
        'target_state': config.target_state,
        'target_county': config.target_county,
        'target_specialty': config.target_specialty,
        'target_plan_year': config.target_plan_year,
    }
    
    analyses = [
        ('8.1', 'sql/analysis_8_1_npi_by_entity_type.sql'),
        ('8.2', 'sql/analysis_8_2_individuals_by_specialty.sql'),
        ('8.3', 'sql/analysis_8_3_primary_care_per_100k.sql'),
        ('8.4', 'sql/analysis_8_4_specialist_density_by_county.sql'),
        ('8.5', 'sql/analysis_8_5_provider_concentration_by_state.sql'),
        ('8.6', 'sql/analysis_8_6_providers_multiple_locations.sql'),
        ('8.7', 'sql/analysis_8_7_clinician_rows_per_npi.sql'),
        ('8.8', 'sql/analysis_8_8_providers_per_facility.sql'),
        ('8.9', 'sql/analysis_8_9_org_concentration.sql'),
        ('8.10', 'sql/analysis_8_10_medicare_util_by_specialty.sql'),
        ('8.11', 'sql/analysis_8_11_utilization_concentration.sql'),
        ('8.12', 'sql/analysis_8_12_supply_util_scatter.sql'),
        ('CT Funnel', 'sql/ct_provider_funnel.sql'),
    ]
    
    for label, sql_file in analyses:
        start = time.time()
        try:
            conn.execute(open(f'sql/{sql_file}').read() if not sql_file.startswith('sql/') else open(sql_file).read())
            # Substitute parameters
            sql = open(sql_file if sql_file.startswith('sql/') else f'sql/{sql_file}').read()
            for key, value in {'target_state': config.target_state}.items():
                sql = sql.replace(f'${{{key}}}', f"'{value}'")
            conn.execute(sql)
            print(f'{label}: {time.time()-start:.1f}s OK')
        except Exception as e:
            print(f'{label}: ERROR - {e}')
    
    conn.close()
    print("\nAnalyses complete.")

if __name__ == "__main__":
    from pathlib import Path
    import time
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from config import config
    import duckdb
    main()