-- Staging: Marketplace Transparency in Coverage
-- Disclaimer data from Transparency in Coverage PUF
-- Source: CMS Marketplace Transparency in Coverage PUF (PY2026)

CREATE OR REPLACE TABLE staging.stg_marketplace_transparency_coverage AS
SELECT
    "Disclaimer" AS disclaimer
FROM marketplace_raw.raw_Transparency_in_Coverage_PUF
WHERE "Disclaimer" IS NOT NULL
  AND "Disclaimer" <> '';