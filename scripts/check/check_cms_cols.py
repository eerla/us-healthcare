import duckdb
conn = duckdb.connect('db/warehouse.duckdb')
conn.execute("ATTACH 'db/cms_raw.duckdb' AS cms_raw (READ_ONLY)")
cols = conn.execute("SELECT * FROM cms_raw.raw_doctors_and_clinicians_national_downloadable_file LIMIT 0").description
for c in cols:
    print(c[0])
conn.close()