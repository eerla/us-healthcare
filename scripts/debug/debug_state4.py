import duckdb

conn = duckdb.connect('db/warehouse.duckdb')
conn.execute("ATTACH 'db/nppes_raw.duckdb' AS nppes_raw (READ_ONLY)")
conn.execute("ATTACH 'db/census_raw.duckdb' AS census_raw (READ_ONLY)")
conn.execute("ATTACH 'db/cms_raw.duckdb' AS cms_raw (READ_ONLY)")
conn.execute("ATTACH 'db/utilization_raw.duckdb' AS utilization_raw (READ_ONLY)")
conn.execute("ATTACH 'db/marketplace_raw.duckdb' AS marketplace_raw (READ_ONLY)")

# Check state populations
result = conn.execute("SELECT state, SUM(total_population) as pop FROM staging.stg_population_county GROUP BY state ORDER BY pop DESC LIMIT 10").fetchall()
print('State populations:', result)

# Check state providers
empty = ""
result = conn.execute("SELECT p.practice_state as state, COUNT(DISTINCT p.provider_sk) as provider_count FROM core.dim_provider p WHERE (p.deactivation_date IS NULL OR p.deactivation_date = ?) AND p.practice_state IS NOT NULL AND p.practice_state <> ? GROUP BY p.practice_state ORDER BY provider_count DESC LIMIT 10", [empty, empty]).fetchall()
print('State providers:', result)

conn.close()