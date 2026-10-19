-- Staging: Marketplace Business Rules
-- One row per issuer product with business rules
-- Source: CMS Marketplace Business Rules PUF (PY2026)

CREATE OR REPLACE TABLE staging.stg_marketplace_business_rules AS
SELECT
    "BusinessYear"::INTEGER AS business_year,
    "StateCode" AS state_code,
    "IssuerId"::VARCHAR AS issuer_id,
    "MedicalDentalBoth" = 'Medical and Dental' AS medical_dental_both,
    "ProductId" AS product_id,
    "StandardComponentId" AS standard_component_id,
    "MedicalDentalIndicator" AS medical_dental_indicator,
    NULLIF("MaximumUnderageDependent", 'Not Applicable')::INTEGER AS max_underage_dependent,
    "DependentMaximumAgRule" AS dependent_max_age_rule,
    "AgeDeterminationRule" AS age_determination_rule,
    NULLIF("MinimumTobaccoFreeMonthsRule", 'Not Applicable')::INTEGER AS min_tobacco_free_months_rule,
    "CohabitationRule" AS cohabitation_rule,
    "MarketCoverage" AS market_coverage,
    "DentalOnlyPlan"::BOOLEAN AS dental_only_plan,
    "SourceName" AS source_name,
    "ImportDate"::DATE AS import_date
FROM marketplace_raw.raw_business_rules
WHERE "StandardComponentId" IS NOT NULL
  AND "StandardComponentId" <> '';