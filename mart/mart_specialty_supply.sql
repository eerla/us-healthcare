-- Mart: Specialty Supply
-- Specialty counts by county/ZIP, joined to population

CREATE OR REPLACE TABLE mart.mart_specialty_supply AS
WITH provider_specialty AS (
    SELECT
        p.provider_sk,
        p.npi,
        p.practice_state AS state,
        COALESCE(s.specialty_group, 'Other') AS specialty_group,
        CAST(l.county_fips AS VARCHAR) AS county_fips,
        l.zip5
    FROM core.dim_provider p
    LEFT JOIN core.dim_specialty s
        ON p.primary_taxonomy_code = s.taxonomy_code
    LEFT JOIN core.bridge_provider_location bpl
        ON p.provider_sk = bpl.provider_sk
        AND bpl.is_primary = true
    LEFT JOIN core.dim_location l
        ON bpl.location_sk = l.location_sk
    WHERE p.deactivation_date IS NULL OR p.deactivation_date = ''
),
county_specialty AS (
    SELECT
        'county' AS geo_type,
        COALESCE(county_fips, state) AS geo_id,
        specialty_group,
        COUNT(DISTINCT provider_sk) AS provider_count
    FROM provider_specialty
    GROUP BY county_fips, state, specialty_group
),
zip_specialty AS (
    SELECT
        'zcta' AS geo_type,
        zip5 AS geo_id,
        specialty_group,
        COUNT(DISTINCT provider_sk) AS provider_count
    FROM provider_specialty
    WHERE zip5 IS NOT NULL AND zip5 <> ''
    GROUP BY zip5, specialty_group
),
all_specialty AS (
    SELECT * FROM county_specialty
    UNION ALL
    SELECT * FROM zip_specialty
)
SELECT
    a.geo_type,
    a.geo_id,
    a.specialty_group,
    a.provider_count,
    COALESCE(pop.population, 0) AS population,
    CASE
        WHEN pop.population > 0
        THEN ROUND(a.provider_count * 100000.0 / pop.population, 2)
        ELSE NULL
    END AS providers_per_100k
FROM all_specialty a
LEFT JOIN core.fact_population pop
    ON pop.geo_type = a.geo_type
    AND pop.geo_id = a.geo_id
    AND pop.year = 2023
ORDER BY a.geo_type, a.geo_id, a.provider_count DESC;