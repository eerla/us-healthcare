import duckdb

conn = duckdb.connect('db/warehouse.duckdb')
conn.execute("ATTACH 'db/nppes_raw.duckdb' AS nppes_raw (READ_ONLY)")
conn.execute("ATTACH 'db/census_raw.duckdb' AS census_raw (READ_ONLY)")
conn.execute("ATTACH 'db/cms_raw.duckdb' AS cms_raw (READ_ONLY)")
conn.execute("ATTACH 'db/utilization_raw.duckdb' AS utilization_raw (READ_ONLY)")
conn.execute("ATTACH 'db/marketplace_raw.duckdb' AS marketplace_raw (READ_ONLY)")

# Test the query
result = conn.execute("""
    WITH state_providers AS (
        SELECT p.practice_state AS st, COUNT(DISTINCT p.provider_sk) AS provider_count
        FROM core.dim_provider p
        WHERE (p.deactivation_date IS NULL OR p.deactivation_date = '')
          AND p.practice_state IS NOT NULL AND p.practice_state <> ''
        GROUP BY p.practice_state
    ),
    state_pop AS (
        SELECT state_name AS st, SUM(total_population) AS total_population
        FROM staging.stg_population_county
        GROUP BY state_name
    )
    SELECT sp.st AS state, sp.provider_count, pop.total_population,
           ROUND(sp.provider_count * 100000.0 / pop.total_population, 2) AS providers_per_100k
    FROM state_providers sp
    JOIN state_pop pop ON sp.st = pop.st
    WHERE pop.total_population > 0
    ORDER BY providers_per_100k DESC
    LIMIT 10
""").fetchall()
print('Providers per 100k:', result)