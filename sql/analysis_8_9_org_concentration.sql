-- Analysis 8.9: Provider concentration by organization
-- Top organizations by provider count, with individual/org breakdown

COPY (
    SELECT
        bpg.org_pac_id,
        o.legal_business_name,
        o.dba_name,
        o.state,
        COUNT(DISTINCT bpg.provider_sk) AS total_providers,
        COUNT(DISTINCT CASE WHEN p.entity_type_code = '1' THEN bpg.provider_sk END) AS individual_providers,
        COUNT(DISTINCT CASE WHEN p.entity_type_code = '2' THEN bpg.provider_sk END) AS organization_providers,
        COUNT(DISTINCT bpg.enrollment_id) AS enrollment_count,
        ROUND(COUNT(DISTINCT bpg.provider_sk) * 100.0 / SUM(COUNT(DISTINCT bpg.provider_sk)) OVER (), 2) AS pct_of_total_providers
    FROM core.bridge_provider_group bpg
    JOIN core.dim_provider p ON bpg.provider_sk = p.provider_sk
    LEFT JOIN core.dim_organization o ON bpg.org_pac_id = o.org_pac_id
    WHERE (p.deactivation_date IS NULL OR p.deactivation_date = '')
    GROUP BY bpg.org_pac_id, o.legal_business_name, o.dba_name, o.state
    ORDER BY total_providers DESC
) TO 'outputs/tables/analysis_8_9_org_concentration.csv' WITH (HEADER, DELIMITER ',');