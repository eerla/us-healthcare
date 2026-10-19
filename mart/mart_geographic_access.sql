-- Mart: Geographic Access
-- Providers per 100k vs. services per provider by county with utilization
-- Uses Medicare utilization data for 2023

CREATE OR REPLACE TABLE mart.mart_geographic_access AS
WITH county_providers AS (
    SELECT
        'county' AS geo_type,
        fips.county_fips AS geo_id,
        fips.county_name,
        fips.state_name AS state,
        ms.specialty_group,
        ms.provider_count,
        fips.total_population AS population,
        ms.providers_per_100k
    FROM mart.mart_specialty_supply ms
    JOIN core.dim_provider p ON ms.specialty_group = COALESCE(p.primary_taxonomy_code, 'Unknown')
    JOIN (
        SELECT state_name, county_fips, county_name, total_population
        FROM staging.stg_population_county
    ) fips
        ON p.practice_state = fips.state_name
    WHERE ms.geo_type = 'county'
      AND ms.provider_count > 0
),
county_utilization AS (
    SELECT
        l.state,
        l.county_fips AS county_fips,
        SUM(CAST(fu.total_beneficiaries AS BIGINT)) AS total_beneficiaries,
        SUM(CAST(fu.total_services AS BIGINT)) AS total_services,
        COUNT(DISTINCT fu.provider_sk) AS providers_with_utilization,
        AVG(CAST(fu.total_services AS DOUBLE)) AS avg_services_per_provider,
        SUM(CAST(fu.total_services AS DOUBLE)) * 1.0 / NULLIF(SUM(CAST(fu.total_beneficiaries AS DOUBLE)), 0) AS services_per_beneficiary
    FROM core.fact_provider_utilization fu
    JOIN core.dim_provider p ON fu.provider_sk = p.provider_sk
    JOIN core.bridge_provider_location bpl ON p.provider_sk = bpl.provider_sk
    JOIN core.dim_location l ON bpl.location_sk = l.location_sk
    WHERE fu.year = 2023
      AND l.state IS NOT NULL AND l.county_fips IS NOT NULL
    GROUP BY l.state, l.county_fips
)
SELECT
    cp.geo_type,
    cp.geo_id,
    cp.county_name,
    cp.state,
    cp.specialty_group,
    cp.provider_count,
    cp.population,
    cp.providers_per_100k,
    cu.total_beneficiaries,
    cu.total_services,
    cu.providers_with_utilization,
    cu.avg_services_per_provider,
    cu.services_per_beneficiary,
    -- Supply vs utilization ratio
    CASE 
        WHEN cu.avg_services_per_provider IS NOT NULL AND cu.avg_services_per_provider > 0
        THEN cp.providers_per_100k / cu.avg_services_per_provider
        ELSE NULL
    END AS supply_utilization_ratio
FROM county_providers cp
LEFT JOIN county_utilization cu
    ON cp.state = cu.state
    AND cp.geo_id = cu.county_fips
ORDER BY cp.providers_per_100k DESC;