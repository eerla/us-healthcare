-- Analysis 8.6: Providers with multiple practice locations
-- Count of providers by number of practice locations

COPY (
    SELECT
        location_count,
        COUNT(*) AS provider_count,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct_of_providers
    FROM (
        SELECT
            p.provider_sk,
            COUNT(DISTINCT bpl.location_sk) AS location_count
        FROM core.dim_provider p
        LEFT JOIN core.bridge_provider_location bpl
            ON p.provider_sk = bpl.provider_sk
        WHERE p.deactivation_date IS NULL OR p.deactivation_date = ''
        GROUP BY p.provider_sk
    ) sub
    GROUP BY location_count
    ORDER BY location_count
) TO 'outputs/tables/analysis_8_6_providers_multiple_locations.csv' WITH (HEADER, DELIMITER ',');