-- Staging: Marketplace Machine-readable URL
-- One row per issuer with machine-readable URLs
-- Source: CMS Marketplace Machine-readable URL PUF (PY2026)

CREATE OR REPLACE TABLE staging.stg_marketplace_machine_readable_url AS
SELECT
    "State" AS state,
    "Issuer ID"::VARCHAR AS issuer_id,
    "URL Submitted" AS url_submitted,
    "Tech POC Email" AS tech_poc_email
FROM marketplace_raw.raw_machine_readable_url
WHERE "Issuer ID" IS NOT NULL
  AND "Issuer ID" <> 0
  AND CAST("Issuer ID" AS VARCHAR) <> '';