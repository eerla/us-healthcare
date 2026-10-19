import duckdb
import time

conn = duckdb.connect('db/warehouse.duckdb')
conn.execute("ATTACH 'db/nppes_raw.duckdb' AS nppes_raw (READ_ONLY)")
conn.execute("ATTACH 'db/census_raw.duckdb' AS census_raw (READ_ONLY)")
conn.execute("ATTACH 'db/cms_raw.duckdb' AS cms_raw (READ_ONLY)")
conn.execute("ATTACH 'db/utilization_raw.duckdb' AS utilization_raw (READ_ONLY)")
conn.execute("ATTACH 'db/marketplace_raw.duckdb' AS marketplace_raw (READ_ONLY)")

analyses = [
    'sql/analysis_8_7_clinician_rows_per_npi.sql',
    'sql/analysis_8_8_providers_per_facility.sql',
    'sql/analysis_8_9_org_concentration.sql',
    'sql/analysis_8_10_medicare_util_by_specialty.sql',
    'sql/analysis_8_11_utilization_concentration.sql',
    'sql/analysis_8_12_supply_util_scatter.sql',
]

for sql_file in analyses:
    start = time.time()
    try:
        conn.execute(open(sql_file).read())
        print(f'{sql_file}: {time.time()-start:.1f}s OK')
    except Exception as e:
        print(f'{sql_file}: ERROR - {e}')

conn.close()