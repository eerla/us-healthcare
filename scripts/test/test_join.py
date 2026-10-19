import duckdb
import time

conn = duckdb.connect('db/warehouse.duckdb')
conn.execute("ATTACH 'db/nppes_raw.duckdb' AS nppes_raw (READ_ONLY)")
conn.execute("ATTACH 'db/census_raw.duckdb' AS census_raw (READ_ONLY)")
conn.execute("ATTACH 'db/cms_raw.duckdb' AS cms_raw (READ_ONLY)")

# Test a simple query
start = time.time()
result = conn.execute("SELECT COUNT(*) FROM staging.stg_clinician c JOIN core.dim_provider p ON c.npi_normalized = p.npi").fetchone()
print(f"Join test: {time.time()-start:.1f}s - {result[0]:,} rows")

conn.close()