-- Bridge: Provider × Location
-- Many-to-many relationship between providers and locations

CREATE OR REPLACE TABLE core.bridge_provider_location AS
WITH provider_locations AS (
    -- Primary practice locations
    SELECT
        p.provider_sk,
        l.location_sk,
        'nppes_primary' AS source,
        true AS is_primary,
        p.enumeration_date AS effective_date,
        p.deactivation_date AS end_date
    FROM core.dim_provider p
    JOIN core.dim_location l
        ON l.address1 = p.practice_address1
        AND COALESCE(l.address2, '') = COALESCE(p.practice_address2, '')
        AND l.city = p.practice_city
        AND l.state = p.practice_state
        AND l.zip5 = LEFT(COALESCE(p.practice_zip, ''), 5)
    WHERE p.practice_address1 IS NOT NULL
      AND TRIM(p.practice_address1) <> ''

    UNION ALL

    -- Secondary practice locations from stg_npi_location
    SELECT
        p.provider_sk,
        l.location_sk,
        'nppes_secondary' AS source,
        false AS is_primary,
        p.enumeration_date AS effective_date,
        p.deactivation_date AS end_date
    FROM core.dim_provider p
    JOIN staging.stg_npi_location sl ON p.npi = sl.npi
    JOIN core.dim_location l
        ON l.address1 = sl.address1
        AND COALESCE(l.address2, '') = COALESCE(sl.address2, '')
        AND l.city = sl.city
        AND l.state = sl.state
        AND l.zip5 = LEFT(COALESCE(sl.zip_code, ''), 5)
    WHERE sl.location_type = 'secondary'

    UNION ALL

    -- Mailing addresses (not primary)
    SELECT
        p.provider_sk,
        l.location_sk,
        'nppes_mailing' AS source,
        false AS is_primary,
        p.enumeration_date AS effective_date,
        p.deactivation_date AS end_date
    FROM core.dim_provider p
    JOIN core.dim_location l
        ON l.address1 = p.mailing_address1
        AND COALESCE(l.address2, '') = COALESCE(p.mailing_address2, '')
        AND l.city = p.mailing_city
        AND l.state = p.mailing_state
        AND l.zip5 = LEFT(COALESCE(p.mailing_zip, ''), 5)
    WHERE p.mailing_address1 IS NOT NULL
      AND TRIM(p.mailing_address1) <> ''
      AND NOT EXISTS (
          SELECT 1 FROM core.dim_location l2
          WHERE l2.address1 = p.practice_address1
            AND COALESCE(l2.address2, '') = COALESCE(p.practice_address2, '')
            AND l2.city = p.practice_city
            AND l2.state = p.practice_state
            AND l2.zip5 = LEFT(COALESCE(p.practice_zip, ''), 5)
      )
)
SELECT
    provider_sk,
    location_sk,
    source,
    is_primary,
    effective_date,
    end_date
FROM provider_locations;