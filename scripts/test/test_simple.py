import duckdb
import time

conn = duckdb.connect('db/warehouse.duckdb')
conn.execute("ATTACH 'db/nppes_raw.duckdb' AS nppes_raw (READ_ONLY)")
conn.execute("ATTACH 'db/census_raw.duckdb' AS census_raw (READ_ONLY)")
conn.execute("ATTACH 'db/cms_raw.duckdb' AS cms_raw (READ_ONLY)")
conn.execute("ATTACH 'db/utilization_raw.duckdb' AS utilization_raw (READ_ONLY)")
conn.execute("ATTACH 'db/marketplace_raw.duckdb' AS marketplace_raw (READ_ONLY)")

# Test a simple query
start = time.time()
try:
    cnt = conn.execute("SELECT COUNT(*) FROM core.dim_provider").fetchone()[0]
    print(f'dim_provider: {cnt:,} rows')
except Exception as e:
    print(f'ERROR: {e}')

# Test a simple analysis query
start = time.time()
try:
    conn.execute("""
        SELECT p.entity_type_code, COUNT(DISTINCT p.npi) as count
        FROM core.dim_provider p
        WHERE p.deactivation_date IS NULL OR p.deactivation_date = ''
        GROUP BY p.entity_type_code
    """)
    print(f'entity_type query: {time.time()-start:.1f}s')
except Exception as e:
    print(f'ERROR: {e}')

conn.close()