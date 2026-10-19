-- Staging: NPPES Practice Locations
-- Secondary practice locations from reference file
-- Source: NPPES V2 practice location reference file

CREATE OR REPLACE TABLE staging.stg_npi_location AS
SELECT
    LPAD(CAST(NPI AS VARCHAR), 10, '0') AS npi,
    "Provider Secondary Practice Location Address- Address Line 1" AS address1,
    "Provider Secondary Practice Location Address-  Address Line 2" AS address2,
    "Provider Secondary Practice Location Address - City Name" AS city,
    "Provider Secondary Practice Location Address - State Name" AS state,
    "Provider Secondary Practice Location Address - Postal Code" AS zip_code,
    "Provider Secondary Practice Location Address - Country Code (If outside U.S.)" AS country_code,
    "Provider Secondary Practice Location Address - Telephone Number" AS phone,
    "Provider Practice Location Address - Fax Number" AS fax,
    'secondary' AS location_type,
    NULL AS certification_date
FROM nppes_raw.raw_pl_pfile_20050523_20260913
WHERE NPI IS NOT NULL
  AND "Provider Secondary Practice Location Address- Address Line 1" IS NOT NULL
  AND TRIM("Provider Secondary Practice Location Address- Address Line 1") <> '';