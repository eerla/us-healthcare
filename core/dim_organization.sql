-- Core: Organization Dimension
-- One organization per NPI (Type 2 entities)
-- Source: CMS Clinicians (org_pac_id) + NPPES

CREATE OR REPLACE TABLE core.dim_organization AS
WITH org_base AS (
    SELECT
        LPAD(CAST(npi AS VARCHAR), 10, '0') AS npi,
        org_pac_id,
        MAX(CASE WHEN provider_last_name IS NOT NULL AND provider_last_name <> '' THEN provider_last_name END) AS legal_business_name,
        MAX(CASE WHEN provider_first_name IS NOT NULL AND provider_first_name <> '' THEN provider_first_name END) AS dba_name,
        MAX(primary_specialty) AS primary_taxonomy,
        MAX(state) AS state,
        MAX(city) AS city,
        MAX(zip_code) AS zip5,
        CURRENT_DATE AS source_snapshot_date
    FROM staging.stg_clinician
    WHERE org_pac_id IS NOT NULL AND TRIM(org_pac_id) <> ''
      AND npi IS NOT NULL
    GROUP BY npi, org_pac_id
)
SELECT
    ROW_NUMBER() OVER (ORDER BY npi) AS organization_sk,
    npi,
    org_pac_id,
    legal_business_name,
    dba_name,
    primary_taxonomy,
    state,
    city,
    zip5,
    NULL AS address_sk,  -- Will be populated from dim_location
    source_snapshot_date
FROM org_base;