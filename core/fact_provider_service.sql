-- Core: Provider Service Fact
-- One row per provider per HCPCS per year from Medicare utilization data
-- Source: CMS Medicare Physician & Other Practitioners by Provider and Service

CREATE OR REPLACE TABLE core.fact_provider_service AS
SELECT
    ROW_NUMBER() OVER (ORDER BY s.npi_normalized, s.hcpcs_code, s.source_year) AS service_sk,
    p.provider_sk,
    s.source_year AS year,
    s.hcpcs_code,
    s.hcpcs_description,
    s.hcpcs_drug_indicator,
    s.place_of_service,
    s.total_beneficiaries,
    s.total_services,
    s.total_bene_day_services,
    s.avg_submitted_charge,
    s.avg_medicare_allowed_amt,
    s.avg_medicare_payment_amt,
    s.avg_medicare_standardized_amt,
    s.medicare_participation_ind,
    s.provider_type,
    'cms_medicare_physician' AS source
FROM staging.stg_provider_service s
JOIN core.dim_provider p
    ON s.npi_normalized = p.npi
WHERE p.deactivation_date IS NULL OR p.deactivation_date = '';