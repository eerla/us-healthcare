import duckdb
import time

conn = duckdb.connect('db/warehouse.duckdb')
conn.execute("ATTACH 'db/nppes_raw.duckdb' AS nppes_raw (READ_ONLY)")
conn.execute("ATTACH 'db/census_raw.duckdb' AS census_raw (READ_ONLY)")
conn.execute("ATTACH 'db/cms_raw.duckdb' AS cms_raw (READ_ONLY)")
conn.execute("ATTACH 'db/utilization_raw.duckdb' AS utilization_raw (READ_ONLY)")
conn.execute("ATTACH 'db/marketplace_raw.duckdb' AS marketplace_raw (READ_ONLY)")

# Test analysis 8.7
start = time.time()
try:
    conn.execute(open('sql/analysis_8_7_clinician_rows_per_npi.sql').read())
    print(f'8.7: {time.time()-start:.1f}s OK')
except Exception as e:
    print(f'8.7 ERROR: {e}')

# Test 8.8
start = time.time()
try:
    conn.execute(open('sql/analysis_8_8_providers_per_facility.sql').read())
    print(f'8.8: {time.time()-start:.1f}s OK')
except Exception as e:
    print(f'8.8 ERROR: {e}')

conn.close()