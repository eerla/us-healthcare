-- Analysis 8.5: Provider concentration by state
-- Providers, locations, and organizations by state

COPY (
    SELECT
        p.practice_state AS state,
        COUNT(DISTINCT p.provider_sk) AS total_providers,
        COUNT(DISTINCT CASE WHEN p.entity_type_code = '1' THEN p.provider_sk END) AS individual_providers,
        COUNT(DISTINCT CASE WHEN p.entity_type_code = '2' THEN p.provider_sk END) AS organization_providers,
        COUNT(DISTINCT bpl.location_sk) AS practice_locations,
        ROUND(COUNT(DISTINCT bpl.location_sk) * 1.0 / NULLIF(COUNT(DISTINCT p.provider_sk), 0), 2) AS locations_per_provider
    FROM core.dim_provider p
    LEFT JOIN core.bridge_provider_location bpl
        ON p.provider_sk = bpl.provider_sk
    WHERE p.deactivation_date IS NULL OR p.deactivation_date = ''
      AND p.practice_state IS NOT NULL
    GROUP BY p.practice_state
    ORDER BY total_providers DESC
) TO 'outputs/tables/analysis_8_5_provider_concentration_by_state.csv' WITH (HEADER, DELIMITER ',');