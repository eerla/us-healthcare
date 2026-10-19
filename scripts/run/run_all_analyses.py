import duckdb
import time

conn = duckdb.connect('db/warehouse.duckdb')
conn.execute("ATTACH 'db/nppes_raw.duckdb' AS nppes_raw (READ_ONLY)")
conn.execute("ATTACH 'db/census_raw.duckdb' AS census_raw (READ_ONLY)")
conn.execute("ATTACH 'db/cms_raw.duckdb' AS cms_raw (READ_ONLY)")
conn.execute("ATTACH 'db/utilization_raw.duckdb' AS utilization_raw (READ_ONLY)")
conn.execute("ATTACH 'db/marketplace_raw.duckdb' AS marketplace_raw (READ_ONLY)")

# Test 8.7
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

# Test 8.9
start = time.time()
try:
    conn.execute(open('sql/analysis_8_9_org_concentration.sql').read())
    print(f'8.9: {time.time()-start:.1f}s OK')
except Exception as e:
    print(f'8.9 ERROR: {e}')

# Test 8.10
start = time.time()
try:
    conn.execute(open('sql/analysis_8_10_medicare_util_by_specialty.sql').read())
    print(f'8.10: {time.time()-start:.1f}s OK')
except Exception as e:
    print(f'8.10 ERROR: {e}')

# Test 8.11
start = time.time()
try:
    conn.execute(open('sql/analysis_8_11_utilization_concentration.sql').read())
    print(f'8.11: {time.time()-start:.1f}s OK')
except Exception as e:
    print(f'8.11 ERROR: {e}')

# Test 8.12
start = time.time()
try:
    conn.execute(open('sql/analysis_8_12_supply_util_scatter.sql').read())
    print(f'8.12: {time.time()-start:.1f}s OK')
except Exception as e:
    print(f'8.12 ERROR: {e}')

conn.close()