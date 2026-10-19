import duckdb
import time

conn = duckdb.connect('db/warehouse.duckdb')
conn.execute("ATTACH 'db/nppes_raw.duckdb' AS nppes_raw (READ_ONLY)")

# Copy dim_specialty from nppes_raw
start = time.time()
conn.execute("CREATE OR REPLACE TABLE core.dim_specialty AS SELECT * FROM nppes_raw.core.dim_specialty")
print(f'dim_specialty copied: {time.time()-start:.1f}s')

# Copy bridge_provider_location from nppes_raw
start = time.time()
conn.execute("CREATE OR REPLACE TABLE core.bridge_provider_location AS SELECT * FROM nppes_raw.core.bridge_provider_location")
print(f'bridge_provider_location copied: {time.time()-start:.1f}s')

# Check counts
for table in ['dim_specialty', 'bridge_provider_location']:
    cnt = conn.execute(f'SELECT COUNT(*) FROM core.{table}').fetchone()[0]
    print(f'core.{table}: {cnt:,} rows')

conn.close()