import duckdb
import os

# Check nppes_raw.duckdb
conn = duckdb.connect('db/nppes_raw.duckdb', read_only=True)
tables = conn.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'main')").fetchall()
print("=== nppes_raw.duckdb ===")
for schema, table in tables:
    try:
        cnt = conn.execute(f'SELECT COUNT(*) FROM "{schema}"."{table}"').fetchone()[0]
        print(f"  {schema}.{table}: {cnt:,} rows")
    except Exception as e:
        print(f"  {schema}.{table}: error - {e}")
conn.close()

# Check census_raw.duckdb
census_path = 'db/census_raw.duckdb'
if os.path.exists(census_path):
    conn = duckdb.connect(census_path, read_only=True)
    tables = conn.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'main')").fetchall()
    print("\n=== census_raw.duckdb ===")
    for schema, table in tables:
        try:
            cnt = conn.execute(f'SELECT COUNT(*) FROM "{schema}"."{table}"').fetchone()[0]
            print(f"  {schema}.{table}: {cnt:,} rows")
        except Exception as e:
            print(f"  {schema}.{table}: error - {e}")
    conn.close()
else:
    print("\n=== census_raw.duckdb: NOT FOUND ===")

# Check raw census files
print("\n=== raw/census/ files ===")
census_dir = 'raw/census'
if os.path.exists(census_dir):
    for f in sorted(os.listdir(census_dir)):
        path = os.path.join(census_dir, f)
        if os.path.isfile(path):
            print(f"  {f}: {os.path.getsize(path):,} bytes")

# Check manifest
print("\n=== manifests/source_manifest.csv ===")
with open('manifests/source_manifest.csv', 'r') as f:
    print(f.read())

# Check warehouse
wh_path = 'db/warehouse.duckdb'
if os.path.exists(wh_path):
    conn = duckdb.connect(wh_path, read_only=True)
    tables = conn.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'main')").fetchall()
    print("\n=== warehouse.duckdb ===")
    for schema, table in tables:
        try:
            cnt = conn.execute(f'SELECT COUNT(*) FROM "{schema}"."{table}"').fetchone()[0]
            print(f"  {schema}.{table}: {cnt:,} rows")
        except Exception as e:
            print(f"  {schema}.{table}: error - {e}")
    conn.close()
else:
    print("\n=== warehouse.duckdb: NOT FOUND ===")