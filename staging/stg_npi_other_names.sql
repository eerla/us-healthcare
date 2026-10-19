-- Staging: NPPES Other Names
-- Other organization names (aliases, former names) for providers
-- Source: NPPES V2 other names reference file

CREATE OR REPLACE TABLE staging.stg_npi_other_names AS
SELECT
    LPAD(CAST(NPI AS VARCHAR), 10, '0') AS npi,
    "Provider Other Organization Name Type Code" AS name_type_code,
    "Provider Other Organization Name" AS other_name,
    NULL AS name_prefix,
    NULL AS name_suffix,
    NULL AS credential_text,
    "Created Date" AS created_date
FROM nppes_raw.raw_othername_pfile_20050523_20260913
WHERE NPI IS NOT NULL
  AND "Provider Other Organization Name" IS NOT NULL
  AND TRIM("Provider Other Organization Name") <> '';