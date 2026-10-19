import duckdb
conn = duckdb.connect('db/nppes_raw.duckdb', read_only=True)
cols = conn.execute("SELECT column_name FROM information_schema.columns WHERE table_schema='main' AND table_name='raw_othername_pfile_20050523_20260913'").fetchall()
for c in cols:
    print(c[0])
conn.close()