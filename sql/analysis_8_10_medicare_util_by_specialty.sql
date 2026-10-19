-- Analysis 8.10: Medicare utilization per clinician by specialty
-- Average services, beneficiaries, payments per clinician by specialty

COPY (
    SELECT
        s.specialty_group,
        COUNT(DISTINCT fu.provider_sk) AS clinician_count,
        SUM(CAST(fu.total_services AS BIGINT)) AS total_services,
        SUM(CAST(fu.total_beneficiaries AS BIGINT)) AS total_beneficiaries,
        SUM(CAST(fu.total_beneficiaries AS DOUBLE)) * 1.0 / COUNT(DISTINCT fu.provider_sk) AS avg_beneficiaries_per_clinician,
        SUM(CAST(fu.total_services AS DOUBLE)) * 1.0 / COUNT(DISTINCT fu.provider_sk) AS avg_services_per_clinician,
        ROUND(AVG(CAST(fu.avg_medicare_payment_amt AS DOUBLE)), 2) AS avg_medicare_payment_per_service,
        ROUND(SUM(CAST(fu.avg_medicare_payment_amt AS DOUBLE) * CAST(fu.total_services AS DOUBLE)), 2) AS total_medicare_payments,
        ROUND(SUM(CAST(fu.avg_medicare_allowed_amt AS DOUBLE) * CAST(fu.total_services AS DOUBLE)), 2) AS total_medicare_allowed
    FROM core.fact_provider_utilization fu
    JOIN core.dim_provider p ON fu.provider_sk = p.provider_sk
    JOIN core.dim_specialty s
        ON p.primary_taxonomy_code = s.taxonomy_code
    WHERE fu.year = 2023
      AND (p.deactivation_date IS NULL OR p.deactivation_date = '')
      AND p.entity_type_code = '1'  -- Individuals only
    GROUP BY s.specialty_group
    HAVING COUNT(DISTINCT fu.provider_sk) > 0
    ORDER BY total_medicare_payments DESC
) TO 'outputs/tables/analysis_8_10_medicare_util_by_specialty.csv' WITH (HEADER, DELIMITER ',');