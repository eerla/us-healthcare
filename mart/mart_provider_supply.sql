-- Mart: Provider Supply
-- Provider counts by state, entity type, specialty group with utilization
-- Adds Medicare utilization metrics per provider

CREATE OR REPLACE TABLE mart.mart_provider_supply AS
SELECT
    p.practice_state AS state,
    p.entity_type_code,
    COALESCE(s.specialty_group, 'Unknown') AS specialty_group,
    COUNT(DISTINCT p.provider_sk) AS provider_count,
    COUNT(DISTINCT CASE WHEN p.entity_type_code = '1' THEN p.provider_sk END) AS individual_count,
    COUNT(DISTINCT CASE WHEN p.entity_type_code = '2' THEN p.provider_sk END) AS organization_count,
    -- Utilization metrics (2023 Medicare)
    SUM(CAST(fu.total_beneficiaries AS BIGINT)) AS total_medicare_beneficiaries,
    SUM(CAST(fu.total_services AS BIGINT)) AS total_medicare_services,
    AVG(CAST(fu.total_services AS DOUBLE)) AS avg_services_per_provider,
    SUM(CAST(fu.total_beneficiaries AS DOUBLE)) / NULLIF(COUNT(DISTINCT p.provider_sk), 0) AS avg_beneficiaries_per_provider
FROM core.dim_provider p
LEFT JOIN core.dim_specialty s
    ON p.primary_taxonomy_code = s.taxonomy_code
LEFT JOIN core.fact_provider_utilization fu
    ON p.provider_sk = fu.provider_sk
    AND fu.year = 2023
WHERE (p.deactivation_date IS NULL OR p.deactivation_date = '')  -- Active providers only
  AND p.practice_state IS NOT NULL AND p.practice_state <> ''
GROUP BY p.practice_state, p.entity_type_code, s.specialty_group
ORDER BY p.practice_state, provider_count DESC;