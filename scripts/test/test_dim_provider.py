import duckdb
import time

conn = duckdb.connect('db/warehouse.duckdb')
conn.execute("ATTACH 'db/nppes_raw.duckdb' AS nppes_raw (READ_ONLY)")
conn.execute("ATTACH 'db/census_raw.duckdb' AS census_raw (READ_ONLY)")
conn.execute("ATTACH 'db/cms_raw.duckdb' AS cms_raw (READ_ONLY)")
conn.execute("ATTACH 'db/utilization_raw.duckdb' AS utilization_raw (READ_ONLY)")

start = time.time()
conn.execute(open('core/dim_provider.sql').read())
print(f'dim_provider: {time.time()-start:.1f}s')

cnt = conn.execute('SELECT COUNT(*) FROM core.dim_provider').fetchone()[0]
print(f'core.dim_provider: {cnt:,} rows')

conn.close()