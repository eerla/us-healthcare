-- Core: Specialty Dimension
-- One row per taxonomy code from NPPES data

CREATE OR REPLACE TABLE core.dim_specialty AS
WITH taxonomies AS (
    SELECT taxonomy_code_1 AS taxonomy_code, taxonomy_group_1 AS taxonomy_group, primary_taxonomy_switch_1 AS is_primary
    FROM staging.stg_npi
    WHERE taxonomy_code_1 IS NOT NULL AND TRIM(taxonomy_code_1) <> ''
    UNION ALL
    SELECT taxonomy_code_2, taxonomy_group_2, primary_taxonomy_switch_2
    FROM staging.stg_npi
    WHERE taxonomy_code_2 IS NOT NULL AND TRIM(taxonomy_code_2) <> ''
    UNION ALL
    SELECT taxonomy_code_3, taxonomy_group_3, primary_taxonomy_switch_3
    FROM staging.stg_npi
    WHERE taxonomy_code_3 IS NOT NULL AND TRIM(taxonomy_code_3) <> ''
    UNION ALL
    SELECT taxonomy_code_4, taxonomy_group_4, primary_taxonomy_switch_4
    FROM staging.stg_npi
    WHERE taxonomy_code_4 IS NOT NULL AND TRIM(taxonomy_code_4) <> ''
    UNION ALL
    SELECT taxonomy_code_5, taxonomy_group_5, primary_taxonomy_switch_5
    FROM staging.stg_npi
    WHERE taxonomy_code_5 IS NOT NULL AND TRIM(taxonomy_code_5) <> ''
    UNION ALL
    SELECT taxonomy_code_6, taxonomy_group_6, primary_taxonomy_switch_6
    FROM staging.stg_npi
    WHERE taxonomy_code_6 IS NOT NULL AND TRIM(taxonomy_code_6) <> ''
    UNION ALL
    SELECT taxonomy_code_7, taxonomy_group_7, primary_taxonomy_switch_7
    FROM staging.stg_npi
    WHERE taxonomy_code_7 IS NOT NULL AND TRIM(taxonomy_code_7) <> ''
    UNION ALL
    SELECT taxonomy_code_8, taxonomy_group_8, primary_taxonomy_switch_8
    FROM staging.stg_npi
    WHERE taxonomy_code_8 IS NOT NULL AND TRIM(taxonomy_code_8) <> ''
    UNION ALL
    SELECT taxonomy_code_9, taxonomy_group_9, primary_taxonomy_switch_9
    FROM staging.stg_npi
    WHERE taxonomy_code_9 IS NOT NULL AND TRIM(taxonomy_code_9) <> ''
    UNION ALL
    SELECT taxonomy_code_10, taxonomy_group_10, primary_taxonomy_switch_10
    FROM staging.stg_npi
    WHERE taxonomy_code_10 IS NOT NULL AND TRIM(taxonomy_code_10) <> ''
    UNION ALL
    SELECT taxonomy_code_11, taxonomy_group_11, primary_taxonomy_switch_11
    FROM staging.stg_npi
    WHERE taxonomy_code_11 IS NOT NULL AND TRIM(taxonomy_code_11) <> ''
    UNION ALL
    SELECT taxonomy_code_12, taxonomy_group_12, primary_taxonomy_switch_12
    FROM staging.stg_npi
    WHERE taxonomy_code_12 IS NOT NULL AND TRIM(taxonomy_code_12) <> ''
    UNION ALL
    SELECT taxonomy_code_13, taxonomy_group_13, primary_taxonomy_switch_13
    FROM staging.stg_npi
    WHERE taxonomy_code_13 IS NOT NULL AND TRIM(taxonomy_code_13) <> ''
    UNION ALL
    SELECT taxonomy_code_14, taxonomy_group_14, primary_taxonomy_switch_14
    FROM staging.stg_npi
    WHERE taxonomy_code_14 IS NOT NULL AND TRIM(taxonomy_code_14) <> ''
    UNION ALL
    SELECT taxonomy_code_15, taxonomy_group_15, primary_taxonomy_switch_15
    FROM staging.stg_npi
    WHERE taxonomy_code_15 IS NOT NULL AND TRIM(taxonomy_code_15) <> ''
),
deduped AS (
    SELECT
        taxonomy_code,
        MAX(taxonomy_group) AS taxonomy_group,
        MAX(CASE WHEN is_primary = 'Y' THEN true ELSE false END) AS is_primary
    FROM taxonomies
    GROUP BY taxonomy_code
)
SELECT
    ROW_NUMBER() OVER (ORDER BY taxonomy_code) AS specialty_sk,
    taxonomy_code,
    taxonomy_group AS taxonomy_description,
    CASE
        WHEN taxonomy_group ILIKE '%family%' OR taxonomy_group ILIKE '%internal medicine%' OR taxonomy_group ILIKE '%pediatrics%' OR taxonomy_group ILIKE '%general practice%' THEN 'Primary Care'
        WHEN taxonomy_group ILIKE '%cardio%' THEN 'Cardiology'
        WHEN taxonomy_group ILIKE '%dermatology%' THEN 'Dermatology'
        WHEN taxonomy_group ILIKE '%psychiatry%' THEN 'Psychiatry'
        WHEN taxonomy_group ILIKE '%orthopedic%' THEN 'Orthopedics'
        ELSE 'Other'
    END AS specialty_group,
    is_primary
FROM deduped;