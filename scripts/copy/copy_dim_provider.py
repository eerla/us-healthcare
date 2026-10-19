import duckdb
import time

conn = duckdb.connect('db/warehouse.duckdb')
conn.execute("ATTACH 'db/nppes_raw.duckdb' AS nppes_raw (READ_ONLY)")
conn.execute("ATTACH 'db/census_raw.duckdb' AS census_raw (READ_ONLY)")
conn.execute("ATTACH 'db/cms_raw.duckdb' AS cms_raw (READ_ONLY)")

# Copy dim_provider from nppes_raw
start = time.time()
conn.execute("CREATE OR REPLACE TABLE core.dim_provider AS SELECT * FROM nppes_raw.core.dim_provider")
print(f"Copied dim_provider: {time.time()-start:.1f}s")

conn.close()