-- Core: Bridge Provider Facility
-- Clinician × facility relationship with match quality
-- Source: CMS Affiliation (links via certification number) + Hospital match

CREATE OR REPLACE TABLE core.bridge_provider_facility AS
WITH matched AS (
    SELECT
        a.npi_normalized AS npi,
        a.facility_type AS affiliation_facility_type,
        a.facility_affiliation_cert_num AS cert_number,
        f.facility_sk,
        f.ccn,
        f.facility_name AS matched_facility_name,
        f.state AS matched_state,
        f.city AS matched_city,
        CASE
            WHEN f.ccn IS NOT NULL THEN 'exact_id'
            ELSE 'unmatched'
        END AS facility_match_method,
        CASE
            WHEN f.ccn IS NOT NULL THEN 'HIGH'
            ELSE 'LOW'
        END AS facility_match_confidence,
        'affiliation' AS affiliation_type,
        p.provider_sk,
        CURRENT_DATE AS source_snapshot
    FROM staging.stg_affiliation a
    JOIN core.dim_provider p
        ON a.npi_normalized = p.npi
    LEFT JOIN core.dim_facility f
        ON f.ccn = a.facility_affiliation_cert_num
    WHERE a.npi IS NOT NULL
      AND a.facility_affiliation_cert_num IS NOT NULL
      AND TRIM(a.facility_affiliation_cert_num) <> ''
)
SELECT
    ROW_NUMBER() OVER (ORDER BY npi, facility_match_method) AS bridge_facility_sk,
    provider_sk,
    facility_sk,
    facility_match_method,
    facility_match_confidence,
    affiliation_type,
    source_snapshot
FROM matched;