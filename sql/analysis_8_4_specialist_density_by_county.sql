-- Analysis 8.4: Specialist density by county
-- Specialist providers per 100k population by county

COPY (
    WITH spec_providers AS (
        SELECT
            l.state,
            l.county_fips AS county_fips,
            COUNT(DISTINCT p.provider_sk) AS specialist_count
        FROM core.dim_provider p
        JOIN core.dim_specialty s
            ON p.primary_taxonomy_code = s.taxonomy_code
        JOIN core.bridge_provider_location bpl
            ON p.provider_sk = bpl.provider_sk
        JOIN core.dim_location l
            ON bpl.location_sk = l.location_sk
        WHERE (p.deactivation_date IS NULL OR p.deactivation_date = '')
          AND s.is_primary = false
          AND l.state IS NOT NULL AND l.county_fips IS NOT NULL
        GROUP BY l.state, l.county_fips
    ),
    county_pop AS (
        SELECT
            state_name AS state,
            county_fips,
            county_name,
            total_population
        FROM staging.stg_population_county
    )
    SELECT
        sp.state,
        sp.county_fips AS county,
        sp.county_fips,
        cp.county_name,
        sp.specialist_count,
        cp.total_population,
        ROUND(sp.specialist_count * 100000.0 / cp.total_population, 2) AS specialists_per_100k
    FROM spec_providers sp
    JOIN county_pop cp ON sp.county_fips = cp.county_fips
    WHERE cp.total_population > 0
    ORDER BY specialists_per_100k DESC
) TO 'outputs/tables/analysis_8_4_specialist_density_by_county.csv' WITH (HEADER, DELIMITER ',');