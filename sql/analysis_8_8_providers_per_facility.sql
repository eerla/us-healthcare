-- Analysis 8.8: Providers per facility
-- Count of unique providers affiliated with each facility

COPY (
    SELECT
        bpf.facility_sk,
        f.facility_name,
        f.ccn,
        f.facility_type,
        f.city,
        f.state,
        COUNT(DISTINCT bpf.provider_sk) AS unique_providers,
        COUNT(DISTINCT CASE WHEN p.entity_type_code = '1' THEN bpf.provider_sk END) AS individual_providers,
        COUNT(DISTINCT CASE WHEN p.entity_type_code = '2' THEN bpf.provider_sk END) AS organization_providers,
        COUNT(*) AS affiliation_rows,
        COUNT(DISTINCT bpf.facility_match_method) AS match_methods_used
    FROM core.bridge_provider_facility bpf
    JOIN core.dim_facility f ON bpf.facility_sk = f.facility_sk
    JOIN core.dim_provider p ON bpf.provider_sk = p.provider_sk
    WHERE (p.deactivation_date IS NULL OR p.deactivation_date = '')
    GROUP BY bpf.facility_sk, f.facility_name, f.ccn, f.facility_type, f.city, f.state
    ORDER BY unique_providers DESC
) TO 'outputs/tables/analysis_8_8_providers_per_facility.csv' WITH (HEADER, DELIMITER ',');