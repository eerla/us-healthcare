import duckdb

conn = duckdb.connect('db/cms_raw.duckdb')

# Re-read clinicians with proper settings
conn.execute("DROP TABLE IF EXISTS raw_doctors_and_clinicians_national_downloadable_file")
conn.execute("""
    CREATE TABLE raw_doctors_and_clinicians_national_downloadable_file AS
    SELECT * FROM read_csv(
        'raw/cms/Doctors_and_Clinicians_National_Downloadable_File.csv',
        header=true,
        all_varchar=true,
        max_line_size=10000000
    )
""")
cnt = conn.execute("SELECT COUNT(*) FROM raw_doctors_and_clinicians_national_downloadable_file").fetchone()[0]
print(f"Clinicians: {cnt:,} rows")

# Re-read affiliation
conn.execute("DROP TABLE IF EXISTS raw_facility_affiliation_data")
conn.execute("""
    CREATE TABLE raw_facility_affiliation_data AS
    SELECT * FROM read_csv(
        'raw/cms/Facility_Affiliation_Data.csv',
        header=true,
        all_varchar=true,
        max_line_size=10000000
    )
""")
cnt = conn.execute("SELECT COUNT(*) FROM raw_facility_affiliation_data").fetchone()[0]
print(f"Affiliation: {cnt:,} rows")

conn.close()