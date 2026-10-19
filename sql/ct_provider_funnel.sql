-- CT Provider Funnel Analysis
-- NPI -> Individuals -> With Specialty -> With Practice Location -> Medicare-enrolled (later)
-- Parameter: ${target_state} (default: CT)

COPY (
    WITH funnel AS (
        SELECT
            'All NPIs' AS stage,
            COUNT(*) AS count,
            1 AS stage_order
        FROM core.dim_provider
        WHERE deactivation_date IS NULL OR deactivation_date = ''

        UNION ALL

        SELECT
            'Individuals (Type 1)' AS stage,
            COUNT(*) AS count,
            2 AS stage_order
        FROM core.dim_provider
        WHERE deactivation_date IS NULL OR deactivation_date = ''
          AND entity_type_code = '1'

        UNION ALL

        SELECT
            'With Primary Specialty' AS stage,
            COUNT(*) AS count,
            3 AS stage_order
        FROM core.dim_provider
        WHERE deactivation_date IS NULL OR deactivation_date = ''
          AND entity_type_code = '1'
          AND primary_taxonomy_code IS NOT NULL
          AND primary_taxonomy_code <> ''

        UNION ALL

        SELECT
            'With Practice Location' AS stage,
            COUNT(DISTINCT p.provider_sk) AS count,
            4 AS stage_order
        FROM core.dim_provider p
        JOIN core.bridge_provider_location bpl
            ON p.provider_sk = bpl.provider_sk
        WHERE p.deactivation_date IS NULL OR p.deactivation_date = ''
          AND p.entity_type_code = '1'
          AND bpl.is_primary = true

        UNION ALL

        SELECT
            'In ${target_state}' AS stage,
            COUNT(DISTINCT p.provider_sk) AS count,
            5 AS stage_order
        FROM core.dim_provider p
        JOIN core.bridge_provider_location bpl
            ON p.provider_sk = bpl.provider_sk
        WHERE p.deactivation_date IS NULL OR p.deactivation_date = ''
          AND p.entity_type_code = '1'
          AND bpl.is_primary = true
          AND p.practice_state = '${target_state}'
    )
    SELECT
        stage,
        count,
        ROUND(count * 100.0 / FIRST_VALUE(count) OVER (ORDER BY stage_order), 2) AS pct_of_total,
        ROUND(count * 100.0 / LAG(count) OVER (ORDER BY stage_order), 2) AS pct_of_previous
    FROM funnel
    ORDER BY stage_order
) TO 'outputs/tables/ct_provider_funnel.csv' WITH (HEADER, DELIMITER ',');