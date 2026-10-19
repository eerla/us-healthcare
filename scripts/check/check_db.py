import duckdb

conn = duckdb.connect('db/nppes_raw.duckdb', read_only=True)
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print('Tables:', [t[0] for t in tables])
for t in tables:
    try:
        cnt = conn.execute(f'SELECT COUNT(*) FROM "{t[0]}"').fetchone()[0]
        print(f'  {t[0]}: {cnt} rows')
    except Exception as e:
        print(f'  {t[0]}: error - {e}')
conn.close()