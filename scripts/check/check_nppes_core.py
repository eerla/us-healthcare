import duckdb
conn = duckdb.connect('db/nppes_raw.duckdb', read_only=True)
tables = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'core'").fetchall()
for t in tables:
    cnt = conn.execute(f'SELECT COUNT(*) FROM core.{t[0]}').fetchone()[0]
    print(f'core.{t[0]}: {cnt:,} rows')
conn.close()