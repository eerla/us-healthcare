import duckdb
conn = duckdb.connect('db/warehouse.duckdb')
tables = conn.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'main')").fetchall()
for schema, table in tables:
    print(f'{schema}.{table}')
conn.close()