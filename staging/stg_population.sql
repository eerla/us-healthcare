-- Staging: Census ACS ZCTA Population
-- One row per ZCTA from ACS 5-year estimates
-- Source: Census API ACS 5-year

CREATE OR REPLACE TABLE staging.stg_population_zcta AS
SELECT
    NAME AS zcta_name,
    NAME AS zcta_display,
    -- ZCTA code is the last token of NAME (e.g., "ZCTA5 12345" -> "12345")
    SPLIT_PART(NAME, ' ', -1) AS zcta5,
    CAST(B01003_001E AS INTEGER) AS total_population,
    CAST(B19013_001E AS INTEGER) AS median_household_income,
    CAST(B17001_001E AS INTEGER) AS poverty_pop_total,
    CAST(B17001_002E AS INTEGER) AS poverty_pop_below,
    -- Derived: poverty rate (avoid division by zero)
    CASE
        WHEN CAST(B17001_001E AS INTEGER) > 0
        THEN ROUND(CAST(B17001_002E AS DOUBLE) / CAST(B17001_001E AS DOUBLE) * 100, 2)
        ELSE NULL
    END AS poverty_rate_pct,
    2023 AS source_year
FROM census_raw.raw_acs_2023_zcta_population
WHERE B01003_001E IS NOT NULL
  AND B01003_001E != 'N'
  AND LENGTH(SPLIT_PART(NAME, ' ', -1)) = 5;