-- Analysis 8.3: Primary care supply per 100k population by state
-- Uses NPPES primary care providers + Census population

COPY (
    WITH pc_providers AS (
        SELECT
            p.practice_state AS state,
            COUNT(DISTINCT p.provider_sk) AS pc_provider_count
        FROM core.dim_provider p
        JOIN core.dim_specialty s
            ON p.primary_taxonomy_code = s.taxonomy_code
        WHERE (p.deactivation_date IS NULL OR p.deactivation_date = '')
          AND s.is_primary = true
          AND p.practice_state IS NOT NULL AND p.practice_state <> ''
        GROUP BY p.practice_state
    ),
    state_pop AS (
        SELECT
            state_name AS state,
            SUM(total_population) AS total_population
        FROM staging.stg_population_county
        GROUP BY state_name
    )
    SELECT
        pc.state,
        pc.pc_provider_count,
        sp.total_population,
        ROUND(pc.pc_provider_count * 100000.0 / sp.total_population, 2) AS pc_per_100k
    FROM pc_providers pc
    JOIN state_pop sp ON pc.state = sp.state
    ORDER BY pc_per_100k DESC
) TO 'outputs/tables/analysis_8_3_primary_care_per_100k.csv' WITH (HEADER, DELIMITER ',');