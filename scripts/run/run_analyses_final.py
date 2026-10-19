import duckdb
import time

conn = duckdb.connect('db/warehouse.duckdb')
conn.execute("ATTACH 'db/nppes_raw.duckdb' AS nppes_raw (READ_ONLY)")
conn.execute("ATTACH 'db/census_raw.duckdb' AS census_raw (READ_ONLY)")
conn.execute("ATTACH 'db/cms_raw.duckdb' AS cms_raw (READ_ONLY)")
conn.execute("ATTACH 'db/utilization_raw.duckdb' AS utilization_raw (READ_ONLY)")
conn.execute("ATTACH 'db/marketplace_raw.duckdb' AS marketplace_raw (READ_ONLY)")

# Run remaining analyses
analyses = [
    ('8.7', 'sql/analysis_8_7_clinician_rows_per_npi.sql'),
    ('8.8', 'sql/analysis_8_8_providers_per_facility.sql'),
    ('8.9', 'sql/analysis_8_9_org_concentration.sql'),
    ('8.10', 'sql/analysis_8_10_medicare_util_by_specialty.sql'),
    ('8.11', 'sql/analysis_8_11_utilization_concentration.sql'),
    ('8.12', 'sql/analysis_8_12_supply_util_scatter.sql'),
]

for label, sql_file in [
    ('8.7', 'sql/analysis_8_7_clinician_rows_per_npi.sql'),
    ('8.8', 'sql/analysis_8_8_providers_per_facility.sql'),
    ('8.9', 'sql/analysis_8_9_org_concentration.sql'),
    ('8.10', 'sql/analysis_8_10_medicare_util_by_specialty.sql'),
    ('8.11', 'sql/analysis_8_11_utilization_concentration.sql'),
    ('8.12', 'sql/analysis_8_12_supply_util_scatter.sql'),
]:
    start = time.time()
    try:
        conn.execute(open(sql_file).read())
        print(f'{label}: {time.time()-start:.1f}s OK')
    except Exception as e:
        print(f'{label}: ERROR - {e}')

conn.close()