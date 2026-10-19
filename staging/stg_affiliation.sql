-- Staging: CMS Facility Affiliation
-- Clinician-to-facility relationships
-- Source: CMS Facility Affiliation Data

CREATE OR REPLACE TABLE staging.stg_affiliation AS
SELECT
    "NPI" AS npi,
    LPAD(CAST("NPI" AS VARCHAR), 10, '0') AS npi_normalized,
    "Ind_PAC_ID" AS ind_pac_id,
    "Provider Last Name" AS provider_last_name,
    "Provider First Name" AS provider_first_name,
    "Provider Middle Name" AS provider_middle_name,
    "suff" AS suffix,
    "facility_type" AS facility_type,
    "Facility Affiliations Certification Number" AS facility_affiliation_cert_num,
    "Facility Type Certification Number" AS facility_type_cert_num,
    'Facility_Affiliation_Data.csv' AS source_file,
    CURRENT_DATE AS source_snapshot_date
FROM cms_raw.raw_facility_affiliation_data
WHERE "NPI" IS NOT NULL
  AND LENGTH(LPAD(CAST("NPI" AS VARCHAR), 10, '0')) = 10;