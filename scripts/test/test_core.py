import duckdb
import time

conn = duckdb.connect('db/warehouse.duckdb')
conn.execute("ATTACH 'db/nppes_raw.duckdb' AS nppes_raw (READ_ONLY)")
conn.execute("ATTACH 'db/census_raw.duckdb' AS census_raw (READ_ONLY)")

# Check dim_location - copy from nppes_raw
start = time.time()
conn.execute("CREATE OR REPLACE TABLE core.dim_location AS SELECT * FROM nppes_raw.core.dim_location")
print(f"dim_location copy: {time.time()-start:.1f}s")

# Check fact_population
start = time.time()
conn.execute(open('core/fact_population.sql').read())
print(f"fact_population: {time.time()-start:.1f}s")

conn.close()