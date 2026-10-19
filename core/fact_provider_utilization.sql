-- Core: Provider Utilization Fact
-- One row per provider per year from Medicare utilization data
-- Source: CMS Medicare Physician & Other Practitioners by Provider

CREATE OR REPLACE TABLE core.fact_provider_utilization AS
SELECT
    ROW_NUMBER() OVER (ORDER BY s.npi_normalized, s.source_year) AS utilization_sk,
    p.provider_sk,
    s.source_year AS year,
    s.total_beneficiaries,
    s.total_services,
    s.avg_medicare_allowed_amt,
    s.avg_medicare_payment_amt,
    s.avg_medicare_standardized_amt,
    s.medicare_participation_ind_1 AS medicare_participation_ind,
    s.provider_type_1 AS provider_type,
    'cms_medicare_physician' AS source
FROM staging.stg_utilization s
JOIN core.dim_provider p
    ON s.npi_normalized = p.npi
WHERE p.deactivation_date IS NULL OR p.deactivation_date = '';