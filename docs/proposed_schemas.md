# Proposed Warehouse Schemas

This document outlines the target table schemas for the US Healthcare data warehouse.
These are the proposed schemas; they will be refined after source profiling in Sprint 1.

## Core Dimensions

### dim_provider
One current provider/entity per NPI.

| Column | Type | Description |
|--------|------|-------------|
| provider_sk | INTEGER | Surrogate key |
| npi | STRING(10) | NPI (10-digit string, never integer) |
| entity_type_code | STRING(1) | '1' = individual, '2' = organization |
| first_name | STRING | Individual's first name |
| last_name | STRING | Individual's last name |
| legal_name | STRING | Legal business name |
| enumeration_date | DATE | NPI enumeration date |
| deactivation_date | DATE | NPI deactivation date (null if active) |
| primary_taxonomy | STRING | Primary taxonomy code |
| taxonomy_list | STRING | Comma-separated taxonomy codes |
| source_updated_at | TIMESTAMP | Source record last updated |

### dim_organization
One organization NPI.

| Column | Type | Description |
|--------|------|-------------|
| organization_sk | INTEGER | Surrogate key |
| npi | STRING(10) | Organization NPI |
| legal_business_name | STRING | Legal business name |
| dba_name | STRING | Doing-business-as name |
| taxonomy | STRING | Organization taxonomy |
| address_sk | INTEGER | FK to dim_location |

### dim_location
One normalized location per unique address.

| Column | Type | Description |
|--------|------|-------------|
| location_sk | INTEGER | Surrogate key |
| address1 | STRING | Street address |
| address2 | STRING | Address line 2 |
| city | STRING | City |
| state | STRING(2) | State abbreviation |
| zip5 | STRING(5) | 5-digit ZIP |
| zip4 | STRING(4) | ZIP+4 (if available) |
| county_fips | STRING(5) | 5-digit county FIPS |
| lat | FLOAT64 | Latitude |
| lon | FLOAT64 | Longitude |
| geocode_quality | STRING | Quality of geocoding match |

### dim_specialty
One taxonomy/specialty.

| Column | Type | Description |
|--------|------|-------------|
| specialty_sk | INTEGER | Surrogate key |
| taxonomy_code | STRING | Taxonomy code |
| taxonomy_description | STRING | Description |
| specialty_group | STRING | Broader grouping (e.g., Primary Care) |
| is_primary | BOOLEAN | Whether this is a primary taxonomy |

### dim_facility
One facility.

| Column | Type | Description |
|--------|------|-------------|
| facility_sk | INTEGER | Surrogate key |
| ccn | STRING | CMS Certification Number |
| facility_name | STRING | Facility name |
| facility_type | STRING | Hospital, CAH, etc. |
| address_sk | INTEGER | FK to dim_location |
| state | STRING(2) | State |
| source | STRING | Source dataset name |

### dim_plan
One marketplace plan/version.

| Column | Type | Description |
|--------|------|-------------|
| plan_sk | INTEGER | Surrogate key |
| plan_id | STRING | Plan ID |
| issuer_id | STRING | Issuer ID |
| state | STRING(2) | State |
| plan_year | INTEGER | Plan year |
| plan_type | STRING | Plan type (HMO, PPO, etc.) |

## Bridge Tables

### bridge_provider_location
Provider × location (many-to-many).

| Column | Type | Description |
|--------|------|-------------|
| provider_sk | INTEGER | FK to dim_provider |
| location_sk | INTEGER | FK to dim_location |
| source | STRING | Source dataset |
| is_primary | BOOLEAN | Whether this is the primary location |
| effective_date | DATE | Start of validity |
| end_date | DATE | End of validity (null = current) |

### bridge_provider_group
Clinician × group/enrollment.

| Column | Type | Description |
|--------|------|-------------|
| provider_sk | INTEGER | FK to dim_provider |
| org_pac_id | STRING | Organization PAC ID |
| group_assignment | STRING | Group assignment type |
| enrollment_id | STRING | Enrollment ID |
| source_snapshot | DATE | Source snapshot date |

### bridge_provider_facility
Clinician × facility affiliation.

| Column | Type | Description |
|--------|------|-------------|
| provider_sk | INTEGER | FK to dim_provider |
| facility_sk | INTEGER | FK to dim_facility (or null if inferred) |
| facility_match_key | STRING | Match key used if facility_sk is null |
| affiliation_type | STRING | Type of affiliation |
| source_snapshot | DATE | Source snapshot date |

### bridge_plan_service_area
Plan × geography.

| Column | Type | Description |
|--------|------|-------------|
| plan_sk | INTEGER | FK to dim_plan |
| state | STRING(2) | State |
| county_fips | STRING(5) | County FIPS |
| zip5 | STRING(5) | ZIP code |
| service_area_source | STRING | Source PUF |

## Fact Tables

### fact_provider_utilization
NPI × year.

| Column | Type | Description |
|--------|------|-------------|
| provider_sk | INTEGER | FK to dim_provider |
| year | INTEGER | Data year |
| services | INTEGER | Number of services |
| beneficiaries | INTEGER | Number of beneficiaries |
| allowed_amount | FLOAT64 | Medicare allowed amount |
| medicare_payment | FLOAT64 | Medicare payment amount |
| submitted_charges | FLOAT64 | Submitted charges |
| source | STRING | Source dataset |

### fact_provider_service
NPI × HCPCS × year.

| Column | Type | Description |
|--------|------|-------------|
| provider_sk | INTEGER | FK to dim_provider |
| year | INTEGER | Data year |
| hcpcs | STRING | HCPCS code |
| place_of_service | STRING | Place of service |
| services | INTEGER | Number of services |
| beneficiaries | INTEGER | Number of beneficiaries |
| allowed_amount | FLOAT64 | Medicare allowed amount |
| payment | FLOAT64 | Medicare payment |

### fact_population
Geography × year.

| Column | Type | Description |
|--------|------|-------------|
| geo_type | STRING | 'zcta', 'county', 'state' |
| geo_id | STRING | Geography identifier |
| year | INTEGER | Data year |
| population | INTEGER | Population count |
| source | STRING | Source dataset |

## Analytical Marts

### mart_provider_supply
Provider counts by geography, entity type, specialty.

### mart_specialty_supply
Specialty counts by county/ZIP, joined to population.

### mart_geographic_access
Providers per 100k vs. services per provider by county.

### mart_provider_network
Plan-level network metadata summary.

### mart_provider_concentration
Top provider/provider-group concentration metrics.

### mart_facility_ecosystem
Hospitals + affiliated clinicians + groups.

### mart_access_pressure
Accessible pool funnel: all providers → specialty → geography → Medicare-enrolled → network-matched.

## Grain Rules

1. **NPPES:** One row per NPI in dim_provider. Multiple rows per NPI in bridge tables for locations.
2. **CMS Clinicians:** Source grain is clinician/enrollment/group/address. NOT person-grain.
3. **CMS Hospital:** One row per facility (CCN).
4. **Utilization:** NPI × year in fact_provider_utilization. NPI × HCPCS × year in fact_provider_service.
5. **Population:** Geography × year.
