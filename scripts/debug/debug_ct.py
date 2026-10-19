import duckdb

conn = duckdb.connect('db/warehouse.duckdb')

# Check ct_providers
print("CT Providers:")
result = conn.execute("""
    SELECT
        l.county_fips AS county,
        l.state,
        COUNT(DISTINCT p.provider_sk) AS provider_count
    FROM core.dim_provider p
    JOIN core.bridge_provider_location bpl
        ON p.provider_sk = bpl.provider_sk
    JOIN core.dim_location l
        ON bpl.location_sk = l.location_sk
    WHERE (p.deactivation_date IS NULL OR p.deactivation_date = '')
      AND l.state = 'CT'
      AND l.county_fips IS NOT NULL
    GROUP BY l.county_fips, l.state
""").fetchall()
for row in result:
    print(f"  {row[0]} ({row[1]}): {row[2]}")

# Check county_pop
print("\nCounty Pop:")
result = conn.execute("""
    SELECT
        county_fips AS county,
        state_name AS state,
        SUM(total_population) AS total_population
    FROM staging.stg_population_county
    WHERE state_name = 'CT'
    GROUP BY county_fips, state_name
""").fetchall()
for row in result[:5]:
    print(f"  {row[0]} ({row[1]}): {row[2]}")

# Check join
print("\nJoin test:")
result = conn.execute("""
    WITH ct_providers AS (
        SELECT
            l.county_fips AS county,
            l.state,
            COUNT(DISTINCT p.provider_sk) AS provider_count
        FROM core.dim_provider p
        JOIN core.bridge_provider_location bpl
            ON p.provider_sk = bpl.provider_sk
        JOIN core.dim_location l
            ON bpl.location_sk = l.location_sk
        WHERE (p.deactivation_date IS NULL OR p.deactivation_date = '')
          AND l.state = 'CT'
          AND l.county_fips IS NOT NULL
        GROUP BY l.county_fips, l.state
    ),
    county_pop AS (
        SELECT
            county_fips AS county,
            state_name AS state,
            SUM(total_population) AS total_population
        FROM staging.stg_population_county
        WHERE state_name = 'CT'
        GROUP BY county_fips, state_name
    )
    SELECT cp.county, cp.state, cp.provider_count, pop.total_population
    FROM ct_providers cp
    JOIN county_pop pop
        ON cp.county = pop.county AND cp.state = pop.state
    WHERE pop.total_population > 0
    ORDER BY cp.county
""").fetchall()
for row in result:
    print(f"  {row[0]} ({row[1]}): {row[2]} providers, pop={row[3]}")

conn.close()