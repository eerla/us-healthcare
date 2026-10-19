-- Analysis 8.7: Clinician rows per NPI (the "rows ≠ people" chart)
-- Shows why COUNT(*) from CMS clinician file ≠ number of doctors

COPY (
    WITH clinician_npi AS (
        SELECT
            npi_normalized AS npi,
            COUNT(*) AS clinician_rows
        FROM staging.stg_clinician
        GROUP BY npi_normalized
    ),
    provider_base AS (
        SELECT
            npi,
            entity_type_code,
            primary_taxonomy_code,
            practice_state
        FROM core.dim_provider
        WHERE deactivation_date IS NULL OR deactivation_date = ''
    )
    SELECT
        cn.npi,
        cn.clinician_rows,
        pb.entity_type_code,
        pb.primary_taxonomy_code,
        pb.practice_state,
        CASE WHEN pb.npi IS NOT NULL THEN 1 ELSE 0 END AS in_dim_provider
    FROM clinician_npi cn
    LEFT JOIN provider_base pb ON cn.npi = pb.npi
    ORDER BY cn.clinician_rows DESC
) TO 'outputs/tables/analysis_8_7_clinician_rows_per_npi.csv' WITH (HEADER, DELIMITER ',');