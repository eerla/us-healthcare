import duckdb
conn = duckdb.connect()
cols = conn.execute("SELECT * FROM read_csv('raw/nppes/npidata_pfile_20050523-20260913.csv', header=true, all_varchar=true, sample_size=1) LIMIT 0").description
print([c[0] for c in cols])
conn.close()