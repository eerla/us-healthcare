import duckdb
conn = duckdb.connect('db/warehouse.duckdb', read_only=True)
tables = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'core'").fetchall()
for (table,) in tables:
    try:
        cnt = conn.execute(f'SELECT COUNT(*) FROM core.{table}').fetchone()[0]
        print(f'core.{table}: {cnt:,} rows')
    except Exception as e:
        print(f'core.{table}: ERROR - {e}')
conn.close()