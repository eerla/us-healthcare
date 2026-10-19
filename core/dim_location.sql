-- Core: Location Dimension
-- One normalized location per unique address

CREATE OR REPLACE TABLE core.dim_location AS
WITH all_locations AS (
    -- Primary practice locations from stg_npi
    SELECT
        npi AS source_npi,
        'primary' AS source_type,
        practice_address1 AS address1,
        practice_address2 AS address2,
        practice_city AS city,
        practice_state AS state,
        practice_zip AS zip5,
        NULL AS zip4,
        practice_country AS country,
        practice_phone AS phone,
        practice_fax AS fax,
        'nppes_primary' AS source
    FROM staging.stg_npi
    WHERE practice_address1 IS NOT NULL AND TRIM(practice_address1) <> ''

    UNION ALL

    -- Secondary practice locations from stg_npi_location
    SELECT
        npi AS source_npi,
        'secondary' AS source_type,
        address1,
        address2,
        city,
        state,
        zip_code AS zip5,
        NULL AS zip4,
        country_code AS country,
        phone,
        fax,
        'nppes_secondary' AS source
    FROM staging.stg_npi_location
    WHERE address1 IS NOT NULL AND TRIM(address1) <> ''

    UNION ALL

    -- Mailing addresses
    SELECT
        npi AS source_npi,
        'mailing' AS source_type,
        mailing_address1 AS address1,
        mailing_address2 AS address2,
        mailing_city AS city,
        mailing_state AS state,
        mailing_zip AS zip5,
        NULL AS zip4,
        mailing_country AS country,
        mailing_phone AS phone,
        mailing_fax AS fax,
        'nppes_mailing' AS source
    FROM staging.stg_npi
    WHERE mailing_address1 IS NOT NULL AND TRIM(mailing_address1) <> ''
),
normalized AS (
    SELECT
        *,
        -- Normalize ZIP to 5-digit
        CASE
            WHEN LENGTH(zip5) >= 5 THEN LEFT(zip5, 5)
            ELSE LPAD(zip5, 5, '0')
        END AS zip5_normalized,
        -- Create a hash for deduplication
        MD5(CONCAT(
            COALESCE(UPPER(TRIM(address1)), ''),
            '|', COALESCE(UPPER(TRIM(address2)), ''),
            '|', COALESCE(UPPER(TRIM(city)), ''),
            '|', COALESCE(UPPER(TRIM(state)), ''),
            '|', COALESCE(UPPER(TRIM(zip5_normalized)), ''),
            '|', COALESCE(UPPER(TRIM(country)), '')
        )) AS address_hash
    FROM all_locations
),
deduped AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY address_hash ORDER BY
            CASE source_type WHEN 'primary' THEN 1 WHEN 'mailing' THEN 2 ELSE 3 END,
            source_npi
        ) AS rn
    FROM normalized
)
SELECT
    ROW_NUMBER() OVER (ORDER BY address_hash) AS location_sk,
    address1,
    address2,
    city,
    state,
    zip5_normalized AS zip5,
    zip4,
    NULL AS county_fips,  -- Will be populated from Census geography
    NULL AS lat,
    NULL AS lon,
    'unverified' AS geocode_quality,
    address_hash,
    source_npi,
    source_type,
    source
FROM deduped
WHERE rn = 1;