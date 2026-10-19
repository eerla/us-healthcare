-- Core: Provider Dimension
-- One current provider/entity per NPI
-- Optimized: filter active first, then deduplicate

CREATE OR REPLACE TABLE core.dim_provider AS
WITH active AS (
    SELECT
        npi,
        entity_type_code,
        legal_business_name,
        last_name,
        first_name,
        middle_name,
        name_prefix,
        name_suffix,
        credential_text,
        enumeration_date,
        deactivation_date,
        reactivation_date,
        sex_code,
        taxonomy_code_1 AS primary_taxonomy_code,
        primary_taxonomy_switch_1 AS is_primary_taxonomy_1,
        taxonomy_group_1 AS primary_taxonomy_group,
        CONCAT_WS(',',
            NULLIF(taxonomy_code_1, ''),
            NULLIF(taxonomy_code_2, ''),
            NULLIF(taxonomy_code_3, ''),
            NULLIF(taxonomy_code_4, ''),
            NULLIF(taxonomy_code_5, ''),
            NULLIF(taxonomy_code_6, ''),
            NULLIF(taxonomy_code_7, ''),
            NULLIF(taxonomy_code_8, ''),
            NULLIF(taxonomy_code_9, ''),
            NULLIF(taxonomy_code_10, ''),
            NULLIF(taxonomy_code_11, ''),
            NULLIF(taxonomy_code_12, ''),
            NULLIF(taxonomy_code_13, ''),
            NULLIF(taxonomy_code_14, ''),
            NULLIF(taxonomy_code_15, '')
        ) AS taxonomy_list,
        is_sole_proprietor,
        is_org_subpart,
        parent_org_lbn,
        parent_org_tin,
        practice_address1,
        practice_address2,
        practice_city,
        practice_state,
        practice_zip,
        mailing_address1,
        mailing_address2,
        mailing_city,
        mailing_state,
        mailing_zip,
        last_update_date AS source_updated_at
    FROM staging.stg_npi
    WHERE npi IS NOT NULL
      AND (deactivation_date IS NULL OR deactivation_date = '')
),
deduped AS (
    SELECT DISTINCT ON (npi) *
    FROM active
    ORDER BY npi, source_updated_at DESC
)
SELECT
    ROW_NUMBER() OVER (ORDER BY npi) AS provider_sk,
    npi,
    entity_type_code,
    CASE WHEN entity_type_code = '1' THEN first_name ELSE NULL END AS first_name,
    CASE WHEN entity_type_code = '1' THEN last_name ELSE NULL END AS last_name,
    legal_business_name,
    enumeration_date,
    deactivation_date,
    primary_taxonomy_code,
    taxonomy_list,
    primary_taxonomy_group AS specialty_group,
    practice_address1,
    practice_address2,
    practice_city,
    practice_state,
    practice_zip,
    mailing_address1,
    mailing_address2,
    mailing_city,
    mailing_state,
    mailing_zip,
    parent_org_lbn,
    parent_org_tin,
    source_updated_at
FROM (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY npi ORDER BY source_updated_at DESC) AS rn
    FROM deduped
) ranked
WHERE rn = 1;