-- Core: Facility Dimension
-- One facility per CCN/name/address
-- Source: CMS Hospital General Information + CMS Affiliation

CREATE OR REPLACE TABLE core.dim_facility AS
WITH hospital_base AS (
    SELECT
        ccn,
        facility_name,
        hospital_type AS facility_type,
        address_line_1,
        NULL AS address_line_2,
        city,
        state,
        zip_code AS zip5,
        county_name,
        phone_number,
        hospital_type,
        hospital_ownership,
        overall_rating,
        'hospital_general' AS source,
        CURRENT_DATE AS source_snapshot_date
    FROM staging.stg_hospital
    WHERE ccn IS NOT NULL AND TRIM(ccn) <> ''
      AND facility_name IS NOT NULL AND TRIM(facility_name) <> ''
),
affiliation_facilities AS (
    SELECT
        'AFFIL_' || ROW_NUMBER() OVER () AS ccn,
        'Affiliation Facility' AS facility_name,
        facility_type,
        NULL AS address_line_1,
        NULL AS address_line_2,
        NULL AS city,
        NULL AS state,
        NULL AS zip5,
        NULL AS county_name,
        NULL AS phone_number,
        facility_type AS hospital_type,
        NULL AS hospital_ownership,
        NULL AS overall_rating,
        'affiliation' AS source,
        CURRENT_DATE AS source_snapshot_date
    FROM staging.stg_affiliation
    WHERE facility_type IS NOT NULL AND TRIM(facility_type) <> ''
),
all_facilities AS (
    SELECT * FROM hospital_base
    UNION ALL
    SELECT * FROM affiliation_facilities
),
deduped AS (
    SELECT
        *,
        MD5(CONCAT(
            COALESCE(UPPER(TRIM(facility_name)), ''),
            '|', COALESCE(UPPER(TRIM(address_line_1)), ''),
            '|', COALESCE(UPPER(TRIM(city)), ''),
            '|', COALESCE(UPPER(TRIM(state)), ''),
            '|', COALESCE(UPPER(TRIM(zip5)), '')
        )) AS facility_hash
    FROM all_facilities
),
ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY facility_hash ORDER BY
            CASE source WHEN 'hospital_general' THEN 1 ELSE 2 END,
            ccn
        ) AS rn
    FROM deduped
)
SELECT
    ROW_NUMBER() OVER (ORDER BY facility_hash) AS facility_sk,
    ccn,
    facility_name,
    facility_type,
    address_line_1,
    address_line_2,
    city,
    state,
    zip5,
    county_name,
    phone_number,
    hospital_type,
    hospital_ownership,
    overall_rating,
    source,
    source_snapshot_date,
    facility_hash
FROM ranked
WHERE rn = 1;