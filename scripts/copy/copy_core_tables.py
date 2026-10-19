import duckdb
import time

conn = duckdb.connect('db/warehouse.duckdb')
conn.execute("ATTACH 'db/nppes_raw.duckdb' AS nppes_raw (READ_ONLY)")

for table in ['dim_location', 'fact_population', 'dim_organization', 'dim_facility', 'bridge_provider_group', 'bridge_provider_facility']:
    start = time.time()
    conn.execute(f"CREATE OR REPLACE TABLE core.{table} AS SELECT * FROM nppes_raw.core.{table}")
    cnt = conn.execute(f"SELECT COUNT(*) FROM core.{table}").fetchone()[0]
    print(f"core.{table}: {cnt:,} rows ({time.time()-start:.1f}s)")

conn.close()