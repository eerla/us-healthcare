-- Mart: Facility Ecosystem
-- Hospitals + affiliated clinicians + groups
-- Shows the ecosystem around each hospital

CREATE OR REPLACE TABLE mart.mart_facility_ecosystem AS
WITH hospital_base AS (
    SELECT
        h.facility_sk,
        h.ccn,
        h.facility_name,
        h.facility_type,
        h.city,
        h.state,
        h.zip5,
        h.county_name,
        h.hospital_type,
        h.hospital_ownership,
        h.overall_rating
    FROM core.dim_facility h
    WHERE h.ccn IS NOT NULL
      AND TRIM(h.ccn) <> ''
),
clinician_affiliation AS (
    SELECT
        bpf.facility_sk,
        COUNT(DISTINCT p.provider_sk) AS affiliated_clinicians,
        COUNT(DISTINCT CASE WHEN p.entity_type_code = '1' THEN p.provider_sk END) AS individual_clinicians,
        COUNT(DISTINCT CASE WHEN p.entity_type_code = '2' THEN p.provider_sk END) AS org_clinicians,
        COUNT(DISTINCT bpg.org_pac_id) AS affiliated_groups
    FROM core.bridge_provider_facility bpf
    JOIN core.dim_provider p ON bpf.provider_sk = p.provider_sk
    LEFT JOIN core.bridge_provider_group bpg ON bpf.provider_sk = bpg.provider_sk
    WHERE p.deactivation_date IS NULL OR p.deactivation_date = ''
    GROUP BY bpf.facility_sk
),
org_affiliation AS (
    SELECT
        bpf.facility_sk,
        COUNT(DISTINCT o.organization_sk) AS affiliated_organizations
    FROM core.bridge_provider_facility bpf
    JOIN core.dim_provider p ON bpf.provider_sk = p.provider_sk
    JOIN core.dim_organization o ON p.npi = o.npi
    WHERE o.organization_sk IS NOT NULL
    GROUP BY bpf.facility_sk
),
utilization_agg AS (
    SELECT
        bpf.facility_sk,
        SUM(fu.total_services::BIGINT) AS total_services,
        SUM(fu.total_beneficiaries::BIGINT) AS total_beneficiaries,
        AVG(fu.avg_medicare_payment_amt::DOUBLE) AS avg_medicare_payment
    FROM core.fact_provider_utilization fu
    JOIN core.dim_provider p ON fu.provider_sk = p.provider_sk
    JOIN core.bridge_provider_facility bpf ON p.provider_sk = bpf.provider_sk
    WHERE fu.year = 2023
      AND bpf.facility_sk IS NOT NULL
    GROUP BY bpf.facility_sk
)
SELECT
    h.facility_sk,
    h.ccn,
    h.facility_name,
    h.facility_type,
    h.city,
    h.state,
    h.zip5,
    h.county_name,
    h.hospital_type,
    h.hospital_ownership,
    h.overall_rating,
    NULL AS emergency_services,
    COALESCE(ca.affiliated_clinicians, 0) AS affiliated_clinicians,
    COALESCE(ca.individual_clinicians, 0) AS individual_clinicians,
    COALESCE(ca.org_clinicians, 0) AS org_clinicians,
    COALESCE(ca.affiliated_groups, 0) AS affiliated_groups,
    COALESCE(oa.affiliated_organizations, 0) AS affiliated_organizations,
    COALESCE(ua.total_services, 0) AS total_medicare_services,
    COALESCE(ua.total_beneficiaries, 0) AS total_medicare_beneficiaries,
    ua.avg_medicare_payment
FROM hospital_base h
LEFT JOIN clinician_affiliation ca ON h.facility_sk = ca.facility_sk
LEFT JOIN org_affiliation oa ON h.facility_sk = oa.facility_sk
LEFT JOIN utilization_agg ua ON h.facility_sk = ua.facility_sk
ORDER BY h.facility_name;