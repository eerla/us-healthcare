import duckdb
conn = duckdb.connect('db/warehouse.duckdb')
tables = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'core' AND table_name LIKE 'fact%'").fetchall()
for t in tables:
    print(t[0])

tables = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'mart'").fetchall()
for t in tables:
    print(t[0])

conn.close()