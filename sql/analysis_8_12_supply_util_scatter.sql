-- Analysis 8.12: Providers per 100k vs. utilization scatter (county level)
-- Supply vs utilization scatter plot data for CT counties

COPY (
    WITH county_supply AS (
        SELECT
            'county' AS geo_type,
            fips.state_name || fips.county_name_clean AS geo_id,
            fips.state_name AS state,
            fips.county_name_clean AS county,
            fips.county_name AS county_name,
            SUM(ms.provider_count) AS total_providers,
            SUM(fips.total_population) AS total_population,
            ROUND(SUM(ms.provider_count) * 100000.0 / SUM(fips.total_population), 2) AS providers_per_100k
        FROM mart.mart_specialty_supply ms
        JOIN staging.stg_population_county fips
            ON ms.geo_id = fips.state_name || fips.county_name_clean
        WHERE ms.geo_type = 'county'
        GROUP BY fips.state_name, fips.county_name_clean, fips.county_name, fips.state_name || fips.county_name_clean
    ),
    county_util AS (
        SELECT
            l.state || l.county_fips AS county_fips,
            COUNT(DISTINCT fu.provider_sk) AS providers_with_util,
            SUM(CAST(fu.total_services AS BIGINT)) AS total_services,
            SUM(CAST(fu.total_beneficiaries AS BIGINT)) AS total_beneficiaries,
            AVG(CAST(fu.total_services AS DOUBLE)) AS avg_services_per_provider,
            SUM(CAST(fu.total_services AS DOUBLE)) * 1.0 / NULLIF(SUM(CAST(fu.total_beneficiaries AS DOUBLE)), 0) AS services_per_beneficiary
        FROM core.fact_provider_utilization fu
        JOIN core.dim_provider p ON fu.provider_sk = p.provider_sk
        JOIN core.bridge_provider_location bpl ON p.provider_sk = bpl.provider_sk
        JOIN core.dim_location l ON bpl.location_sk = l.location_sk
        WHERE fu.year = 2023
          AND l.state IS NOT NULL AND l.county_fips IS NOT NULL
        GROUP BY l.state || l.county_fips
    )
    SELECT
        cs.geo_type,
        cs.geo_id,
        cs.state,
        cs.county,
        cs.county_name,
        cs.total_providers,
        cs.total_population,
        cs.providers_per_100k,
        cu.providers_with_util,
        cu.total_services,
        cu.total_beneficiaries,
        cu.avg_services_per_provider,
        cu.services_per_beneficiary,
        -- Supply vs utilization gap
        ROUND(cs.providers_per_100k / NULLIF(cu.avg_services_per_provider, 0), 2) AS supply_util_ratio
    FROM county_supply cs
    LEFT JOIN county_util cu
        ON cs.geo_id = cu.county_fips
    WHERE cs.total_population > 0
    ORDER BY cs.providers_per_100k DESC
) TO 'outputs/tables/analysis_8_12_supply_util_scatter.csv' WITH (HEADER, DELIMITER ',');