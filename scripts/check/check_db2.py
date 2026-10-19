import duckdb

conn = duckdb.connect('db/nppes_raw.duckdb', read_only=True)
schemas = conn.execute("SELECT schema_name FROM information_schema.schemata").fetchall()
print('Schemas:', [s[0] for s in schemas])

# Check all tables with schema-qualified names
tables = conn.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'main')").fetchall()
print('\nAll non-system tables:')
for schema, table in tables:
    cnt = conn.execute(f'SELECT COUNT(*) FROM "{schema}"."{table}"').fetchone()[0]
    print(f'  {schema}.{table}: {cnt} rows')

# Check raw file sizes
print('\n--- Raw CSV sizes ---')
import os
for f in sorted(os.listdir('raw/nppes')):
    if f.endswith('.csv'):
        path = os.path.join('raw/nppes', f)
        size = os.path.getsize(path)
        print(f'  {f}: {size/1024/1024:.1f} MB')

conn.close()