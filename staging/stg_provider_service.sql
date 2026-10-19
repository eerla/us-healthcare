-- Staging: Medicare Utilization by Provider and Service
-- One row per provider per HCPCS per year
-- Source: CMS Medicare Physician & Other Practitioners by Provider and Service

CREATE OR REPLACE TABLE staging.stg_provider_service AS
SELECT
    "Rndrng_NPI" AS npi,
    LPAD(CAST("Rndrng_NPI" AS VARCHAR), 10, '0') AS npi_normalized,
    "Rndrng_Prvdr_Last_Org_Name" AS provider_last_name,
    "Rndrng_Prvdr_First_Name" AS provider_first_name,
    "Rndrng_Prvdr_MI" AS provider_middle_initial,
    "Rndrng_Prvdr_Crdntls" AS provider_credentials,
    "Rndrng_Prvdr_Ent_Cd" AS entity_type_code,
    "Rndrng_Prvdr_St1" AS address_line_1,
    "Rndrng_Prvdr_St2" AS address_line_2,
    "Rndrng_Prvdr_City" AS city,
    "Rndrng_Prvdr_State_Abrvtn" AS state,
    "Rndrng_Prvdr_State_FIPS" AS state_fips,
    "Rndrng_Prvdr_Zip5" AS zip5,
    "Rndrng_Prvdr_RUCA" AS ruca_code,
    "Rndrng_Prvdr_RUCA_Desc" AS ruca_desc,
    "Rndrng_Prvdr_Cntry" AS country,
    "Rndrng_Prvdr_Type" AS provider_type,
    "Rndrng_Prvdr_Mdcr_Prtcptg_Ind" AS medicare_participation_ind,
    "HCPCS_Cd" AS hcpcs_code,
    "HCPCS_Desc" AS hcpcs_description,
    "HCPCS_Drug_Ind" AS hcpcs_drug_indicator,
    "Place_Of_Srvc" AS place_of_service,
    "Tot_Benes" AS total_beneficiaries,
    "Tot_Srvcs" AS total_services,
    "Tot_Bene_Day_Srvcs" AS total_bene_day_services,
    "Avg_Sbmtd_Chrg" AS avg_submitted_charge,
    "Avg_Mdcr_Alowd_Amt" AS avg_medicare_allowed_amt,
    "Avg_Mdcr_Pymt_Amt" AS avg_medicare_payment_amt,
    "Avg_Mdcr_Stdzd_Amt" AS avg_medicare_standardized_amt,
    2023 AS source_year
FROM utilization_raw.raw_medicare_physician_other_practitioners_by_provider_and_service_2023
WHERE "Rndrng_NPI" IS NOT NULL
  AND LENGTH(LPAD(CAST("Rndrng_NPI" AS VARCHAR), 10, '0')) = 10
  AND "HCPCS_Cd" IS NOT NULL;