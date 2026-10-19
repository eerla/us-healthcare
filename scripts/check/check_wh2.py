import duckdb
conn = duckdb.connect('db/warehouse.duckdb', read_only=True)
tables = conn.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'main')").fetchall()
for schema, table in tables:
    try:
        cnt = conn.execute(f'SELECT COUNT(*) FROM "{schema}"."{table}"').fetchone()[0]
        print(f'  {schema}.{table}: {cnt:,} rows')
    except Exception as e:
        print(f'  {schema}.{table}: ERROR - {e}')
conn.close()