-- Core: Population Fact
-- Joins Census ACS ZCTA population to provider locations by ZIP
-- Source: Census ACS 5-year estimates (2023)

CREATE OR REPLACE TABLE core.fact_population AS
SELECT
    ROW_NUMBER() OVER (ORDER BY z.zcta5) AS population_sk,
    'zcta' AS geo_type,
    z.zcta5 AS geo_id,
    z.zcta5 AS zip5,
    z.zcta_name,
    z.total_population AS population,
    z.median_household_income,
    z.poverty_rate_pct,
    z.source_year AS year,
    -- Count providers in this ZIP
    COUNT(DISTINCT l.location_sk) AS provider_locations,
    COUNT(DISTINCT p.provider_sk) AS providers_in_zip,
    -- Providers per 100k population
    CASE
        WHEN z.total_population > 0
        THEN ROUND(COUNT(DISTINCT p.provider_sk) * 100000.0 / z.total_population, 2)
        ELSE NULL
    END AS providers_per_100k
FROM staging.stg_population_zcta z
LEFT JOIN core.dim_location l
    ON l.zip5 = z.zcta5
LEFT JOIN core.bridge_provider_location b
    ON l.location_sk = b.location_sk
LEFT JOIN core.dim_provider p
    ON b.provider_sk = p.provider_sk
GROUP BY z.zcta5, z.zcta_name, z.total_population, z.median_household_income, z.poverty_rate_pct, z.source_year
ORDER BY z.zcta5;