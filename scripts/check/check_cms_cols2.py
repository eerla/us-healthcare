import duckdb
conn = duckdb.connect('db/warehouse.duckdb')
conn.execute("ATTACH 'db/cms_raw.duckdb' AS cms_raw (READ_ONLY)")

for table in ['raw_facility_affiliation_data', 'raw_hospital_general_information']:
    print(f"\n=== {table} ===")
    cols = conn.execute(f"SELECT * FROM cms_raw.{table} LIMIT 0").description
    for c in cols:
        print(c[0])

conn.close()