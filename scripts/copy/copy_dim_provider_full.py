import duckdb
import time

conn = duckdb.connect('db/warehouse.duckdb')
conn.execute("ATTACH 'db/nppes_raw.duckdb' AS nppes_raw (READ_ONLY)")

# Copy dim_provider from nppes_raw (100k sample)
start = time.time()
conn.execute("CREATE OR REPLACE TABLE core.dim_provider AS SELECT * FROM nppes_raw.core.dim_provider")
print(f'dim_provider copied: {time.time()-start:.1f}s')

cnt = conn.execute('SELECT COUNT(*) FROM core.dim_provider').fetchone()[0]
print(f'core.dim_provider: {cnt:,} rows')

conn.close()