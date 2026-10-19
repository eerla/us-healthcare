# Ingestion Plan

This document outlines the ingestion strategy for each source dataset.

## General Principles

1. **Raw data is never modified in place.** All downloads go to `raw/<source>/`.
2. **Every load records metadata:** source URL, retrieval timestamp, dataset version, file checksum, row count, schema.
3. **NPI is always treated as STRING(10).** Never cast to integer.
4. **Source grain is preserved.** Do not silently deduplicate or aggregate.
5. **Years are explicit.** Do not mix vintage years silently.

## NPPES (P0)

**Source:** https://download.cms.gov/nppes/NPI_Files.html

**Files to download:**
- Monthly V2 file (compressed, ~1.1 GB)
- Practice Location Reference File
- Other Names Reference File
- Endpoint Reference File

**Ingestion approach:**
- Load into DuckDB `db/nppes_raw.duckdb`
- Staging views: `stg_npi`, `stg_npi_location`
- Split Type 1 (individual) and Type 2 (organization) into separate logical views
- Taxonomy fields exploded to provider-specialty bridge
- Practice locations exploded to provider-location bridge
- NPI normalized to 10-char string (pad with leading zeros if needed)

**Data quality checks:**
- NPI exactly 10 characters, all digits
- Entity type code is '1' or '2'
- No duplicate NPIs in dim_provider
- ZIP5 is exactly 5 characters

## CMS Doctors & Clinicians (P0)

**Source:** https://data.cms.gov/provider-data/dataset/mj5m-pzi6

**File to download:**
- National Downloadable File (CSV, ~3.4M rows, 31 columns)

**Ingestion approach:**
- Load into DuckDB `db/cms_raw.duckdb`
- Staging: `stg_clinician` — preserve source grain, do NOT deduplicate
- Join to `dim_provider` on NPI (high confidence)
- Create match-quality columns: `npi_match_method` (exact, padded, missing)
- Deduplicate at correct analytical grain; document grain explicitly

**Key insight:** This file is NOT at person grain. COUNT(*) ≠ number of doctors.

## CMS Facility Affiliation (P0)

**Source:** https://data.cms.gov/provider-data/dataset/27ea-468

**File to download:**
- Facility Affiliation Data (~2.2M rows)

**Ingestion approach:**
- Load into DuckDB `db/cms_raw.duckdb`
- Staging: `stg_affiliation`
- Join clinicians to facilities via NPI
- Facility matching: prefer CCN (facility identifier), fall back to normalized name + address
- Create match-quality columns: `facility_match_method`, `facility_match_confidence`

## CMS Hospital General Information (P0)

**Source:** https://data.cms.gov/provider-data/dataset/xubh-q36u

**File to download:**
- Hospital General Information (~5,419 rows, 38 columns)

**Ingestion approach:**
- Load into DuckDB `db/cms_raw.duckdb`
- Staging: `stg_hospital`
- Build `dim_facility` with CCN as stable identifier
- Do NOT equate hospital name with unique corporate entity

## CMS Medicare Utilization (P1)

**Sources:**
- https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners/medicare-physician-other-practitioners-by-provider
- https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners/medicare-physician-other-practitioners-by-provider-and-service

**Files to download:**
- Medicare Physician by Provider (annual, 2024 latest)
- Medicare Physician by Provider and Service

**Ingestion approach:**
- Load into DuckDB `db/utilization_raw.duckdb`
- Staging: `stg_utilization`, `stg_provider_service`
- Join to `dim_provider` on NPI
- Year-snapshot discipline: every row tagged with data year
- Validate no many-to-many explosion on NPI join

**Caveat:** Medicare utilization ≠ total healthcare utilization. Covers Original Medicare fee-for-service Part B only.

## Census ACS 5-Year (P1)

**Source:** https://www.census.gov/data/developers/data-sets/acs-5year.html

**Files to download:**
- ACS 5-year estimates by ZCTA and county

**Ingestion approach:**
- Load into DuckDB `db/cms_raw.duckdb`
- Staging: `stg_population`
- Create `fact_population` with geography × year grain
- Join to provider/specialty marts for per-capita calculations

## Census TIGER/Line (P1)

**Source:** https://www.census.gov/geographies/mapping-files.html

**Files to download:**
- ZCTA shapefiles

**Ingestion approach:**
- Load shapefiles into DuckDB spatial extension or PostGIS
- Create `stg_geography` with normalized county/ZIP mappings
- Support spatial joins for mapping visualizations

## CMS Marketplace Exchange PUFs (P1)

**Source:** https://www.cms.gov/marketplace/resources/data/public-use-files

**Files to download:**
- Plan PUF
- Service Area PUF
- Network PUF
- Machine-Readable URL PUF

**Ingestion approach:**
- Load into DuckDB `db/cms_raw.duckdb`
- Staging: `stg_marketplace`
- Build `dim_plan` and `bridge_plan_service_area`
- Network matching: plan/service-area metadata first (high confidence)
- Provider-level network matching only where provider identifiers are exposed in selected MRFs
- Do NOT invent network participation

**Caveat:** Transparency in Coverage MRFs are large and complex. Treat as Phase 2.

## Source Manifest Schema

Every ingestion run appends a row to `manifests/source_manifest.csv`:

| Column | Description |
|--------|-------------|
| source | Dataset name |
| url | Source URL |
| retrieval_timestamp | ISO-8601 timestamp of download |
| dataset_version | Version or date of the source file |
| file_checksum | MD5 or SHA256 of downloaded file |
| rows_loaded | Rows successfully loaded |
| rows_rejected | Rows rejected by data quality checks |
| transformation_version | Version of transformation code |
| notes | Free text |

## Data Quality Report Schema

Every ingestion run appends a row to `manifests/data_quality_report.csv`:

| Column | Description |
|--------|-------------|
| source | Dataset name |
| snapshot | Snapshot date |
| rows_loaded | Rows successfully loaded |
| rows_rejected | Rows rejected |
| null_rate | Fraction of nulls in key columns |
| duplicate_rate | Fraction of duplicates detected |
| checksum | File checksum |
| validation_errors | Count of validation errors |
| notes | Free text |
