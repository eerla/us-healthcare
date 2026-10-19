-- Staging: Census ACS County Population
-- One row per county from ACS 5-year estimates
-- Source: Census API ACS 5-year

CREATE OR REPLACE TABLE staging.stg_population_county AS
SELECT
    NAME AS county_name,
    -- NAME format: "County Name, State FIPS" e.g. "Fairfield County, Connecticut"
    SPLIT_PART(NAME, ',', 1) AS county_name_clean,
    TRIM(SPLIT_PART(NAME, ',', 2)) AS state_name,
    -- County FIPS from geography columns (state, county)
    state || county AS county_fips,
    CAST(B01003_001E AS INTEGER) AS total_population,
    CAST(B19013_001E AS INTEGER) AS median_household_income,
    CAST(B17001_001E AS INTEGER) AS poverty_pop_total,
    CAST(B17001_002E AS INTEGER) AS poverty_pop_below,
    CASE
        WHEN CAST(B17001_001E AS INTEGER) > 0
        THEN ROUND(CAST(B17001_002E AS DOUBLE) / CAST(B17001_001E AS DOUBLE) * 100, 2)
        ELSE NULL
    END AS poverty_rate_pct,
    2023 AS source_year
FROM census_raw.raw_acs_2023_county_population
WHERE B01003_001E IS NOT NULL
  AND B01003_001E != 'N';