import duckdb
import time

conn = duckdb.connect('db/warehouse.duckdb')
conn.execute("ATTACH 'db/nppes_raw.duckdb' AS nppes_raw (READ_ONLY)")
conn.execute("ATTACH 'db/census_raw.duckdb' AS census_raw (READ_ONLY)")
conn.execute("ATTACH 'db/cms_raw.duckdb' AS cms_raw (READ_ONLY)")
conn.execute("ATTACH 'db/utilization_raw.duckdb' AS utilization_raw (READ_ONLY)")
conn.execute("ATTACH 'db/marketplace_raw.duckdb' AS marketplace_raw (READ_ONLY)")

# Test analysis 8.3
start = time.time()
try:
    conn.execute(open('sql/analysis_8_3_primary_care_per_100k.sql').read())
    print(f'8.3: {time.time()-start:.1f}s OK')
except Exception as e:
    print(f'8.3 ERROR: {e}')

# Test 8.4
start = time.time()
try:
    conn.execute(open('sql/analysis_8_4_specialist_density_by_county.sql').read())
    print(f'8.4: {time.time()-start:.1f}s OK')
except Exception as e:
    print(f'8.4 ERROR: {e}')

conn.close()