-- Staging: CMS Clinicians
-- One row per clinician/enrollment/group/address record
-- Preserves source grain. Do NOT deduplicate.
-- Source: CMS Doctors & Clinicians National Downloadable File

CREATE OR REPLACE TABLE staging.stg_clinician AS
SELECT
    "NPI" AS npi,
    LPAD(CAST("NPI" AS VARCHAR), 10, '0') AS npi_normalized,
    "Ind_PAC_ID" AS ind_pac_id,
    "Ind_enrl_ID" AS ind_enrl_id,
    "Provider Last Name" AS provider_last_name,
    "Provider First Name" AS provider_first_name,
    "Provider Middle Name" AS provider_middle_name,
    "suff" AS suffix,
    "gndr" AS gender,
    "Cred" AS credential,
    "Med_sch" AS medical_school,
    "Grd_yr" AS graduation_year,
    "pri_spec" AS primary_specialty,
    "sec_spec_1" AS secondary_specialty_1,
    "sec_spec_2" AS secondary_specialty_2,
    "sec_spec_3" AS secondary_specialty_3,
    "sec_spec_4" AS secondary_specialty_4,
    "sec_spec_all" AS all_specialties,
    "Telehlth" AS telehealth,
    "Facility Name" AS facility_name,
    "org_pac_id" AS org_pac_id,
    "num_org_mem" AS num_org_members,
    "adr_ln_1" AS address_line_1,
    "adr_ln_2" AS address_line_2,
    "ln_2_sprs" AS address_line_2_suppressed,
    "City/Town" AS city,
    "State" AS state,
    "ZIP Code" AS zip_code,
    'Doctors_and_Clinicians_National_Downloadable_File.csv' AS source_file,
    CURRENT_DATE AS source_snapshot_date
FROM cms_raw.raw_doctors_and_clinicians_national_downloadable_file
WHERE "NPI" IS NOT NULL
  AND LENGTH(LPAD(CAST("NPI" AS VARCHAR), 10, '0')) = 10;