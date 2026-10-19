-- Analysis 8.1: Unique NPIs by entity type
-- Count of unique NPIs split by entity type (1=Individual, 2=Organization)

COPY (
    SELECT
        entity_type_code,
        CASE entity_type_code
            WHEN '1' THEN 'Individual'
            WHEN '2' THEN 'Organization'
            ELSE 'Unknown'
        END AS entity_type,
        COUNT(*) AS npi_count
    FROM core.dim_provider
    WHERE deactivation_date IS NULL OR deactivation_date = ''
    GROUP BY entity_type_code
    ORDER BY entity_type_code
) TO 'outputs/tables/analysis_8_1_npi_by_entity_type.csv' WITH (HEADER, DELIMITER ',');