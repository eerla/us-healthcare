-- Analysis 8.2: Individual clinicians by specialty
-- Count of individual providers (entity_type=1) by specialty group

COPY (
    SELECT
        COALESCE(s.specialty_group, 'Unknown') AS specialty_group,
        COUNT(DISTINCT p.provider_sk) AS provider_count
    FROM core.dim_provider p
    LEFT JOIN core.dim_specialty s
        ON p.primary_taxonomy_code = s.taxonomy_code
    WHERE p.deactivation_date IS NULL OR p.deactivation_date = ''
      AND p.entity_type_code = '1'
    GROUP BY s.specialty_group
    ORDER BY provider_count DESC
) TO 'outputs/tables/analysis_8_2_individuals_by_specialty.csv' WITH (HEADER, DELIMITER ',');