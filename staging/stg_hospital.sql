-- Staging: CMS Hospital General Information
-- Hospital universe with CCN, type, address, ratings
-- Source: CMS Hospital General Information

CREATE OR REPLACE TABLE staging.stg_hospital AS
SELECT
    "Facility ID" AS ccn,
    "Facility Name" AS facility_name,
    "Address" AS address_line_1,
    "City/Town" AS city,
    "State" AS state,
    "ZIP Code" AS zip_code,
    "County/Parish" AS county_name,
    "Telephone Number" AS phone_number,
    "Hospital Type" AS hospital_type,
    "Hospital Ownership" AS hospital_ownership,
    "Emergency Services" AS emergency_services,
    "Hospital overall rating" AS overall_rating,
    'Hospital_General_Information.csv' AS source_file,
    CURRENT_DATE AS source_snapshot_date
FROM cms_raw.raw_hospital_general_information
WHERE "Facility ID" IS NOT NULL
  AND TRIM("Facility ID") <> '';