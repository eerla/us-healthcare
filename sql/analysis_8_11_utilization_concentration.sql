-- Analysis 8.11: Utilization concentration (top 1%, 5%, 10%)
-- Share of Medicare services/beneficiaries by top provider percentiles

COPY (
    WITH ranked_providers AS (
        SELECT
            fu.provider_sk,
            CAST(fu.total_services AS BIGINT) AS total_services,
            CAST(fu.total_beneficiaries AS BIGINT) AS total_beneficiaries,
            ROW_NUMBER() OVER (ORDER BY CAST(fu.total_services AS BIGINT) DESC) AS rank_services,
            ROW_NUMBER() OVER (ORDER BY CAST(fu.total_beneficiaries AS BIGINT) DESC) AS rank_beneficiaries,
            COUNT(*) OVER () AS total_providers
        FROM core.fact_provider_utilization fu
        JOIN core.dim_provider p ON fu.provider_sk = p.provider_sk
        WHERE fu.year = 2023
          AND (p.deactivation_date IS NULL OR p.deactivation_date = '')
    ),
    totals AS (
        SELECT
            SUM(total_services) AS total_services,
            SUM(total_beneficiaries) AS total_beneficiaries,
            COUNT(*) AS total_providers
        FROM ranked_providers
    ),
    concentration AS (
        SELECT
            rp.*,
            t.total_services,
            t.total_beneficiaries,
            t.total_providers,
            ROUND(rp.rank_services * 100.0 / t.total_providers, 2) AS pct_rank_services,
            ROUND(rp.rank_beneficiaries * 100.0 / t.total_providers, 2) AS pct_rank_beneficiaries,
            SUM(rp.total_services) OVER (ORDER BY rp.rank_services) AS cum_services,
            SUM(rp.total_beneficiaries) OVER (ORDER BY rp.rank_beneficiaries) AS cum_beneficiaries
        FROM ranked_providers rp
        CROSS JOIN totals t
    )
    SELECT
        'Top 1%' AS tier,
        SUM(CASE WHEN pct_rank_services <= 1 THEN total_services ELSE 0 END) AS services_top_1pct,
        SUM(CASE WHEN pct_rank_beneficiaries <= 1 THEN total_beneficiaries ELSE 0 END) AS beneficiaries_top_1pct,
        ROUND(SUM(CASE WHEN pct_rank_services <= 1 THEN total_services ELSE 0 END) * 100.0 / MAX(total_services), 2) AS pct_of_total_services_1,
        ROUND(SUM(CASE WHEN pct_rank_beneficiaries <= 1 THEN total_beneficiaries ELSE 0 END) * 100.0 / MAX(total_beneficiaries), 2) AS pct_of_total_beneficiaries_1
    FROM concentration
    WHERE pct_rank_services <= 1 OR pct_rank_beneficiaries <= 1

    UNION ALL

    SELECT
        'Top 5%' AS tier,
        SUM(CASE WHEN pct_rank_services <= 5 THEN total_services ELSE 0 END),
        SUM(CASE WHEN pct_rank_beneficiaries <= 5 THEN total_beneficiaries ELSE 0 END),
        ROUND(SUM(CASE WHEN pct_rank_services <= 5 THEN total_services ELSE 0 END) * 100.0 / MAX(total_services), 2),
        ROUND(SUM(CASE WHEN pct_rank_beneficiaries <= 5 THEN total_beneficiaries ELSE 0 END) * 100.0 / MAX(total_beneficiaries), 2)
    FROM concentration
    WHERE pct_rank_services <= 5 OR pct_rank_beneficiaries <= 5

    UNION ALL

    SELECT
        'Top 10%' AS tier,
        SUM(CASE WHEN pct_rank_services <= 10 THEN total_services ELSE 0 END),
        SUM(CASE WHEN pct_rank_beneficiaries <= 10 THEN total_beneficiaries ELSE 0 END),
        ROUND(SUM(CASE WHEN pct_rank_services <= 10 THEN total_services ELSE 0 END) * 100.0 / MAX(total_services), 2),
        ROUND(SUM(CASE WHEN pct_rank_beneficiaries <= 10 THEN total_beneficiaries ELSE 0 END) * 100.0 / MAX(total_beneficiaries), 2)
    FROM concentration
    WHERE pct_rank_services <= 10 OR pct_rank_beneficiaries <= 10
) TO 'outputs/tables/analysis_8_11_utilization_concentration.csv' WITH (HEADER, DELIMITER ',');