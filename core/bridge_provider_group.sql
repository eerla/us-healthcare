-- Core: Bridge Provider Group
-- Clinician × group/enrollment relationship
-- Source: CMS Clinicians (org_pac_id, ind_enrl_id)

CREATE OR REPLACE TABLE core.bridge_provider_group AS
WITH matched AS (
    SELECT
        c.npi_normalized AS npi,
        c.org_pac_id,
        c.ind_enrl_id AS enrollment_id,
        c.provider_last_name,
        c.provider_first_name,
        c.primary_specialty,
        c.state,
        p.provider_sk
    FROM staging.stg_clinician c
    JOIN core.dim_provider p
        ON c.npi_normalized = p.npi
    WHERE c.org_pac_id IS NOT NULL AND TRIM(c.org_pac_id) <> ''
      AND c.npi IS NOT NULL
)
SELECT
    ROW_NUMBER() OVER (ORDER BY npi, org_pac_id, enrollment_id) AS bridge_group_sk,
    provider_sk,
    org_pac_id,
    enrollment_id,
    'cms_clinicians' AS source_snapshot
FROM matched;