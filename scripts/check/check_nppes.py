import duckdb
conn = duckdb.connect('db/nppes_raw.duckdb', read_only=True)
tables = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'core'").fetchall()
for (table,) in tables:
    cnt = conn.execute(f'SELECT COUNT(*) FROM core.{table}').fetchone()[0]
    print(f'nppes_raw.core.{table}: {cnt:,} rows')
conn.close()