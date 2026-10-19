-- Staging: Marketplace Service Area
-- One row per issuer service area (state, county, zip)
-- Source: CMS Marketplace Service Area PUF (PY2026)

CREATE OR REPLACE TABLE staging.stg_marketplace_service_area AS
SELECT
    "BusinessYear"::INTEGER AS business_year,
    "StateCode" AS state_code,
    "IssuerId"::VARCHAR AS issuer_id,
    "ServiceAreaId" AS service_area_id,
    "ServiceAreaName" AS service_area_name,
    "CoverEntireState"::BOOLEAN AS cover_entire_state,
    "County" AS county,
    "PartialCounty"::BOOLEAN AS partial_county,
    "ZipCodes" AS zip_codes,
    "PartialCountyJustification" AS partial_county_justification,
    "MarketCoverage" AS market_coverage,
    "DentalOnlyPlan"::BOOLEAN AS dental_only_plan,
    "SourceName" AS source_name,
    "ImportDate"::DATE AS import_date
FROM marketplace_raw.raw_service_area
WHERE "ServiceAreaId" IS NOT NULL
  AND "ServiceAreaId" <> '';