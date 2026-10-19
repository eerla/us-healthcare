import duckdb
import time

conn = duckdb.connect('db/warehouse.duckdb')
conn.execute("ATTACH 'db/nppes_raw.duckdb' AS nppes_raw (READ_ONLY)")
conn.execute("ATTACH 'db/census_raw.duckdb' AS census_raw (READ_ONLY)")
conn.execute("ATTACH 'db/cms_raw.duckdb' AS cms_raw (READ_ONLY)")
conn.execute("ATTACH 'db/utilization_raw.duckdb' AS utilization_raw (READ_ONLY)")
conn.execute("ATTACH 'db/marketplace_raw.duckdb' AS marketplace_raw (READ_ONLY)")

# Test a simple staging query
start = time.time()
conn.execute(open('staging/stg_marketplace_plan.sql').read())
print(f'stg_marketplace_plan: {time.time()-start:.1f}s')

# Check count
cnt = duckdb.connect('db/warehouse.duckdb').execute('SELECT COUNT(*) FROM staging.stg_marketplace_plan').fetchone()[0]
print(f'Rows: {cnt:,}')