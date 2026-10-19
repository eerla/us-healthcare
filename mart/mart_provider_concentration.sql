-- Mart: Provider Concentration
-- Top provider/provider-group concentration metrics with utilization
-- Shows whether care is dominated by a few organizations

CREATE OR REPLACE TABLE mart.mart_provider_concentration AS
WITH org_providers AS (
    SELECT
        COALESCE(NULLIF(TRIM(p.parent_org_lbn), ''), 'Independent Providers') AS organization_name,
        p.practice_state AS state,
        COUNT(DISTINCT p.provider_sk) AS provider_count,
        COUNT(DISTINCT CASE WHEN p.entity_type_code = '1' THEN p.provider_sk END) AS individual_count,
        COUNT(DISTINCT CASE WHEN p.entity_type_code = '2' THEN p.provider_sk END) AS org_count,
        -- Utilization metrics
        SUM(CAST(fu.total_services AS BIGINT)) AS total_medicare_services,
        SUM(CAST(fu.total_beneficiaries AS BIGINT)) AS total_medicare_beneficiaries,
        AVG(CAST(fu.total_services AS DOUBLE)) AS avg_services_per_provider
    FROM core.dim_provider p
    LEFT JOIN core.fact_provider_utilization fu
        ON p.provider_sk = fu.provider_sk
        AND fu.year = 2023
    WHERE p.deactivation_date IS NULL OR p.deactivation_date = ''
    GROUP BY p.parent_org_lbn, p.practice_state
),
ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (ORDER BY provider_count DESC) AS rank_provider_count,
        ROW_NUMBER() OVER (ORDER BY total_medicare_services DESC NULLS LAST) AS rank_services,
        SUM(provider_count) OVER () AS total_providers,
        SUM(total_medicare_services) OVER () AS total_services,
        SUM(provider_count) OVER (ORDER BY provider_count DESC) AS cumulative_providers,
        SUM(total_medicare_services) OVER (ORDER BY total_medicare_services DESC NULLS LAST) AS cumulative_services
    FROM org_providers
)
SELECT
    organization_name,
    state,
    provider_count,
    individual_count,
    org_count,
    ROUND(provider_count * 100.0 / total_providers, 2) AS pct_of_total_providers,
    ROUND(cumulative_providers * 100.0 / total_providers, 2) AS cumulative_pct_providers,
    total_medicare_services,
    total_medicare_beneficiaries,
    avg_services_per_provider,
    ROUND(total_medicare_services * 100.0 / total_services, 2) AS pct_of_total_services,
    ROUND(cumulative_services * 100.0 / total_services, 2) AS cumulative_pct_services,
    CASE
        WHEN cumulative_providers * 100.0 / total_providers <= 1 THEN 'Top 1%'
        WHEN cumulative_providers * 100.0 / total_providers <= 5 THEN 'Top 5%'
        WHEN cumulative_providers * 100.0 / total_providers <= 10 THEN 'Top 10%'
        ELSE 'Other'
    END AS provider_concentration_tier,
    CASE
        WHEN cumulative_services * 100.0 / total_services <= 1 THEN 'Top 1%'
        WHEN cumulative_services * 100.0 / total_services <= 5 THEN 'Top 5%'
        WHEN cumulative_services * 100.0 / total_services <= 10 THEN 'Top 10%'
        ELSE 'Other'
    END AS utilization_concentration_tier
FROM ranked
ORDER BY provider_count DESC;