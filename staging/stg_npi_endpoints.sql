-- Staging: NPPES Endpoints
-- API endpoints for electronic services
-- Source: NPPES V2 endpoints reference file

CREATE OR REPLACE TABLE staging.stg_npi_endpoints AS
SELECT
    LPAD(CAST(NPI AS VARCHAR), 10, '0') AS npi,
    "Endpoint Type" AS endpoint_type,
    "Endpoint Type Description" AS endpoint_type_desc,
    "Endpoint" AS endpoint_url,
    "Affiliation" AS affiliation,
    "Endpoint Description" AS endpoint_description,
    "Use Code" AS endpoint_use_code,
    "Use Description" AS endpoint_use_desc,
    "Other Use Description" AS other_use_desc,
    "Content Type" AS content_type,
    "Content Description" AS content_type_desc,
    "Other Content Description" AS other_content_desc,
    "Affiliation Legal Business Name" AS affiliation_lbn,
    "Affiliation Address Line One" AS affiliation_address1,
    "Affiliation Address Line Two" AS affiliation_address2,
    "Affiliation Address City" AS affiliation_city,
    "Affiliation Address State" AS affiliation_state,
    "Affiliation Address Country" AS affiliation_country,
    "Affiliation Address Postal Code" AS affiliation_zip
FROM nppes_raw.raw_endpoint_pfile_20050523_20260913
WHERE NPI IS NOT NULL
  AND "Endpoint" IS NOT NULL
  AND TRIM("Endpoint") <> '';