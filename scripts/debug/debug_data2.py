import duckdb

conn = duckdb.connect('db/warehouse.duckdb')
conn.execute("ATTACH 'db/nppes_raw.duckdb' AS nppes_raw (READ_ONLY)")
conn.execute("ATTACH 'db/census_raw.duckdb' AS census_raw (READ_ONLY)")
conn.execute("ATTACH 'db/cms_raw.duckdb' AS cms_raw (READ_ONLY)")
conn.execute("ATTACH 'db/utilization_raw.duckdb' AS utilization_raw (READ_ONLY)")
conn.execute("ATTACH 'db/marketplace_raw.duckdb' AS marketplace_raw (READ_ONLY)")

# Fix CT county providers query - use county_fips not county_name
result = conn.execute("""
    SELECT l.county_fips, COUNT(DISTINCT p.provider_sk) as provider_count
    FROM core.dim_provider p
    JOIN core.bridge_provider_location bpl ON p.provider_sk = bpl.provider_sk
    JOIN core.dim_location l ON bpl.location_sk = l.location_sk
    WHERE l.state = 'CT' AND (p.deactivation_date IS NULL OR p.deactivation_date = '')
    GROUP BY l.county_fips
    ORDER BY provider_count DESC
""").fetchall()
print('CT county providers:', result)

# Check CT specialty groups via taxonomy
result = conn.execute("""
    SELECT s.specialty_group, COUNT(DISTINCT p.provider_sk) as cnt
    FROM core.dim_provider p
    JOIN core.bridge_provider_location bpl ON p.provider_sk = bpl.provider_sk
    JOIN core.dim_location l ON bpl.location_sk = l.location_sk
    JOIN core.dim_specialty s ON p.primary_taxonomy_code = s.taxonomy_code
    WHERE l.state = 'CT' AND (p.deactivation_date IS NULL OR p.deactivation_date = '')
    GROUP BY s.specialty_group
    ORDER BY cnt DESC
""").fetchall()
print('CT specialty groups:', result)

# Check state providers
result = conn.execute("""
    SELECT p.practice_state, COUNT(DISTINCT p.provider_sk) as cnt
    FROM core.dim_provider p
    WHERE p.deactivation_date IS NULL OR p.deactivation_date = ''
    GROUP BY p.practice_state
    ORDER BY cnt DESC
""").fetchall()
print('State providers:', result)

conn.close()