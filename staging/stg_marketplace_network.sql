-- Staging: Marketplace Network
-- One row per issuer network
-- Source: CMS Marketplace Network PUF (PY2026)

CREATE OR REPLACE TABLE staging.stg_marketplace_network AS
SELECT
    "BusinessYear"::INTEGER AS business_year,
    "StateCode" AS state_code,
    "IssuerId"::VARCHAR AS issuer_id,
    "NetworkName" AS network_name,
    "NetworkId" AS network_id,
    "NetworkURL" AS network_url,
    "MarketCoverage" AS market_coverage,
    "DentalOnlyPlan"::BOOLEAN AS dental_only_plan,
    "SourceName" AS source_name,
    "ImportDate"::DATE AS import_date
FROM marketplace_raw.raw_network
WHERE "NetworkId" IS NOT NULL
  AND "NetworkId" <> '';