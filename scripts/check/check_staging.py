import duckdb
conn = duckdb.connect('db/warehouse.duckdb')
tables = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'staging'").fetchall()
for t in tables:
    print(t[0])
conn.close()