# US Healthcare Data Engineering Experiment — Sprint Plan

## Project Overview

Build a reproducible public-data pipeline that models the U.S. healthcare system and explains why appointment access is hard despite millions of providers.

**Core question:** There are millions of healthcare providers and thousands of hospitals. Why can it still be difficult to get an appointment?

**Approach:** Build the national data model first, then produce a Connecticut-focused analysis as the concrete story. The project expands nationally after the pipeline is proven.

**Stack:** Python + DuckDB/Polars for ingestion and profiling, BigQuery for the analytical warehouse, dbt for transformations/tests, Streamlit or Looker Studio for visualization.

**First milestone:** A single reproducible chart — "The healthcare provider funnel in Connecticut." If that chart is analytically sound, the rest of the project has a strong foundation.

---

## Sprint 0 — Foundation & Reproducible Environment

**Goal:** A fresh clone can run one command and get a working environment with source tracking.

### Tasks

1. Create repository structure
   - `README.md` — project overview, setup instructions, known limitations
   - `pyproject.toml` — Python dependencies (polars, duckdb, dbt, streamlit, etc.)
   - `Makefile` — `make setup`, `make validate-sources`, `make ingest`, `make transform`, `make analyze`
   - `.env.example` — BigQuery project ID, dataset names, paths

2. Create config files
   - `config/sources.yml` — source registry with URLs, versions, expected schemas, file patterns
   - `config/geography.yml` — ZIP-to-county, county-to-state mappings, Census geography config
   - `config/analysis.yml` — parameter store (default target state = CT, snapshot dates, specialty filters)

3. Create ingestion manifest templates
   - `manifests/source_manifest_schema.csv` — columns: source, url, retrieval_timestamp, dataset_version, file_checksum, rows_loaded, rows_rejected, transformation_version
   - `manifests/data_quality_schema.csv` — columns: source, snapshot, rows_loaded, rows_rejected, null_rate, duplicate_rate, checksum

4. Create raw directory structure
   - `raw/nppes/` — NPI file, practice locations, other names, endpoints
   - `raw/cms/` — clinicians, facility affiliation, hospital general, utilization
   - `raw/census/` — ACS 5-year, TIGER/Line ZCTA
   - `raw/marketplace/` — plan PUF, service area PUF, network PUF, MR URL PUF

5. Implement Make targets
   - `make setup` — create raw/, staging/, core/, mart/, outputs/, manifests/ directories
   - `make validate-sources` — check all URLs in sources.yml are reachable, print expected file sizes

### Deliverable

Running `git clone` + `make setup` + `make validate-sources` produces a working local structure with source catalog.

### Acceptance Criteria

- A new contributor can set up in under 5 minutes from the README
- `make validate-sources` confirms all P0 URLs are reachable
- Directory structure matches the planned raw/staging/core/mart layout

---

## Sprint 1 — NPPES Backbone + Census Geography

**Goal:** Build the provider/location/specialty spine and answer "how many providers are there, really?"

### Why this sprint first

NPPES is the master provider registry. Every other source joins back to NPI. Get this right and everything downstream has a stable key.

### Tasks

1. **Download NPPES V2**
   - Fetch monthly V2 file (~1.1 GB compressed) from https://download.cms.gov/nppes/NPI_Files.html
   - Fetch practice location reference file
   - Fetch other names reference file
   - Fetch endpoints reference file
   - Record source URL, retrieval timestamp, dataset version, file checksum in `source_manifest.csv`

2. **Ingest NPPES to DuckDB**
   - Load raw files into `raw/nppes/` without modification
   - Create DuckDB database at `db/nppes_raw.duckdb`

3. **Stage NPPES data**
   - `stg_npi` — one row per NPI, normalized 10-char NPI string, entity type, legal business name, enumeration/deactivation dates, primary taxonomy
   - `stg_npi_location` — exploded practice locations (primary + reference), each with NPI, address fields, location type
   - Split Type 1 (individual) and Type 2 (organization) into separate logical views

4. **Load Census geography**
   - Fetch Census ACS 5-year estimates (population by ZCTA/county)
   - Fetch Census TIGER/Line ZCTA geometries (for mapping)
   - Load to `raw/census/`
   - Create `stg_population` and `stg_geography` staging tables

5. **Build core dimensions**
   - `dim_provider` — one current provider/entity per NPI. Columns: provider_sk (surrogate key), npi, entity_type_code, first_name, last_name, legal_name, enumeration_date, deactivation_date, primary_taxonomy, taxonomy_list, source_updated_at
   - `dim_location` — one normalized location per unique address. Columns: location_sk, address1, address2, city, state, zip5, zip4, county_fips, lat, lon, geocode_quality
   - `dim_specialty` — one row per taxonomy code. Columns: specialty_sk, taxonomy_code, taxonomy_description, specialty_group, is_primary
   - `bridge_provider_location` — provider × location. Columns: provider_sk, location_sk, source, is_primary, effective_date, end_date
   - Preserve NPI as STRING throughout. Never cast to integer.

6. **Data quality checks**
   - NPI format: exactly 10 characters, all digits
   - NPI uniqueness: one row in dim_provider per NPI
   - Entity type: validate only '1' or '2'
   - ZIP format: ZIP5 is 5 characters
   - Row reconciliation: raw rows = accepted + rejected; rejected rows have a reason

7. **Build marts**
   - `mart_provider_supply` — provider counts by state, entity type, specialty group
   - `mart_specialty_supply` — specialty counts by county/ZIP, joined to population
   - Include `providers_per_100k` calculation

8. **Implement analyses (from section 8 of handoff)**
   - 8.1: Unique NPIs by entity type
   - 8.2: Individual clinicians by specialty
   - 8.5: Provider concentration by state (providers, locations, organizations)
   - 8.6: Providers with multiple practice locations

9. **Create first chart**
   - "The Healthcare Provider Funnel in Connecticut"
   - NPI → individuals → with specialty → with practice location → Medicare-enrolled (after Sprint 2)
   - Save to `outputs/charts/ct_provider_funnel.png`

### Deliverable

- DuckDB database with NPPES + Census fully staged and modeled
- 4 analyses producing validated outputs
- First chart: CT provider funnel

### Acceptance Criteria

- `make ingest-nppes` downloads, checksums, and loads without manual intervention
- `make transform` builds all core and mart tables
- `make analyze` runs analyses 8.1, 8.2, 8.5, 8.6 and writes CSVs to `outputs/tables/`
- CT provider funnel chart renders from versioned SQL
- Every number in the chart has a traceable source snapshot in `source_manifest.csv`

---

## Sprint 2 — CMS Clinicians + Facilities + Hospitals

**Goal:** Connect providers to groups, facilities, and hospitals. Answer "who is actually enrolled and where do they work?"

### Why this sprint second

CMS clinicians and facility data join to NPI. Without `dim_provider` from Sprint 1, these sources have no anchor.

### Tasks

1. **Download CMS datasets**
   - CMS Doctors & Clinicians National Downloadable File (~3.4M rows, 31 cols)
   - CMS Facility Affiliation Data (~2.2M rows)
   - CMS Hospital General Information (~5,419 rows, 38 cols)
   - Record all source metadata in `source_manifest.csv`

2. **Ingest to DuckDB**
   - Load raw files to `raw/cms/`
   - Create DuckDB database at `db/cms_raw.duckdb`

3. **Stage CMS data**
   - `stg_clinician` — one row per clinician/enrollment/group/address record. Preserve source grain. Do NOT deduplicate yet.
   - `stg_affiliation` — clinician-to-facility relationships
   - `stg_hospital` — hospital universe with CCN, type, address, ratings

4. **Entity resolution**
   - Join `stg_clinician` to `dim_provider` on NPI (high confidence)
   - Deduplicate clinician rows at correct analytical grain — document the grain explicitly
   - Match hospitals to facilities: prefer CCN (facility identifier), fall back to normalized name + address
   - Create match-quality columns: `facility_match_method` (exact_id, name_address, inferred), `facility_match_confidence`

5. **Build core dimensions and bridges**
   - `dim_organization` — one organization NPI. Columns: organization_sk, npi, legal_business_name, dba_name, taxonomy, address_sk
   - `dim_facility` — one facility. Columns: facility_sk, ccn, facility_name, facility_type, address_sk, state, source
   - `bridge_provider_group` — clinician × group/enrollment. Columns: provider_sk, org_pac_id, group_assignment, enrollment_id, source_snapshot
   - `bridge_provider_facility` — clinician × facility. Columns: provider_sk, facility_sk or facility_match_key, affiliation_type, source_snapshot

6. **Critical engineering rule**
   - Do not infer relationships from names when a source identifier exists
   - Keep source IDs and create explicit match-quality fields when inference is necessary

7. **Key insight chart**
   - "CMS Clinician Rows vs. Unique NPIs" — show why `COUNT(*)` ≠ number of doctors
   - This is the storytelling chart that makes the abstract grain problem concrete

8. **Network graph**
   - Provider → group → facility for one Connecticut metro area (e.g., New Haven or Hartford)
   - Nodes: providers, organizations, facilities
   - Edges: group assignments, facility affiliations
   - Save to `outputs/charts/ct_network_graph.png`

9. **Implement analyses**
   - 8.7: Clinician rows per NPI (the "rows ≠ people" chart)
   - 8.8: Providers per facility
   - 8.9: Provider concentration by organization

### Deliverable

- DuckDB database with CMS clinicians, facilities, and hospitals staged and resolved
- Entity resolution logic with documented match methods
- 3 analyses + 2 charts (CT funnel updated with Medicare enrollment, rows-per-NPI, network graph)

### Acceptance Criteria

- `make ingest-cms` loads all three CMS datasets
- `make transform` builds organization, facility, and bridge tables
- Join from clinician to provider via NPI has no unexpected many-to-many explosion
- Rows-per-NPI chart clearly shows the grain mismatch
- Network graph renders for one CT metro area
- Every inferred relationship has a documented match method and confidence

---

## Sprint 3 — Medicare Utilization + Provider Concentration

**Goal:** Measure actual service volume, not just presence. Answer "do high-supply areas also have high capacity?"

### Why this sprint third

Utilization joins to NPI. You need `dim_provider` and `dim_specialty` stable before loading utilization, because this is where grain mistakes compound.

### Tasks

1. **Download Medicare utilization datasets**
   - CMS Medicare Physician & Other Practitioners by Provider (annual, 2024 latest)
   - CMS Medicare Physician & Other Practitioners by Provider and Service
   - Record source metadata

2. **Ingest to DuckDB**
   - Load to `raw/cms/`
   - Create `db/utilization_raw.duckdb`

3. **Stage utilization data**
   - `stg_utilization` — provider-level utilization. Columns: npi, year, services, beneficiaries, allowed_amount, medicare_payment, submitted_charges
   - `stg_provider_service` — HCPCS-level detail. Columns: npi, year, hcpcs, place_of_service, services, beneficiaries, allowed_amount, payment
   - Preserve source year. Do NOT mix years silently.

4. **Build core facts**
   - `fact_provider_utilization` — NPI × year grain. Columns: provider_sk, year, services, beneficiaries, allowed_amount, medicare_payment, submitted_charges, source
   - `fact_provider_service` — NPI × HCPCS × year grain

5. **Build marts**
   - `mart_provider_supply` — update with utilization joins (services per clinician by specialty)
   - `mart_specialty_supply` — specialty counts + utilization by county
   - `mart_geographic_access` — providers per 100k vs. services per provider by county (the scatter plot)
   - `mart_provider_concentration` — top 1%, 5%, 10% utilization share

6. **Implement analyses**
   - 8.3: Primary care supply per 100k population (by state)
   - 8.4: Specialist density by county
   - 8.10: Medicare utilization per clinician by specialty
   - 8.11: Utilization concentration (top 1%, 5%, 10%)
   - 8.12: Providers per 100k vs. utilization scatter (county level)

7. **Create charts**
   - CT specialty scarcity map — primary care, cardiology, dermatology, psychiatry, orthopedics
   - Provider supply vs. utilization scatter (CT counties)
   - Concentration bar chart — top health systems by clinician count

### Deliverable

- Utilization facts and marts built and validated
- 5 analyses + 3 charts (specialty scarcity map, supply/utilization scatter, concentration bar chart)

### Acceptance Criteria

- `make ingest-utilization` downloads and loads utilization data
- Join from utilization to provider via NPI has no many-to-many explosion
- Year is explicit in every fact table and mart
- CT specialty scarcity map shows clear geographic variation
- Supply vs. utilization scatter identifies counties where supply and capacity diverge
- Concentration chart shows whether local care is dominated by a few organizations

---

## Sprint 4 — Marketplace Networks + Connecticut Story

**Goal:** Add the insurance filter and produce the CT dashboard.

### Why this sprint fourth

Network data is the messiest source. Build it after the core provider/facility/ utilization spine is stable, so the CT story can use everything built so far.

### Tasks

1. **Download CMS Exchange PUFs**
   - Plan PUF
   - Service Area PUF
   - Network PUF
   - MR URL PUF
   - Record source metadata

2. **Ingest and stage**
   - Load to `raw/marketplace/`
   - `stg_marketplace` — plan, service area, network, MR URL staging tables

3. **Build core dimensions and bridges**
   - `dim_plan` — one plan/version. Columns: plan_sk, plan_id, issuer_id, state, plan_year, plan_type
   - `bridge_plan_service_area` — plan × geography. Columns: plan_sk, state, county_fips, zip5, service_area_source

4. **Build network mart**
   - `mart_provider_network` — plan-level network metadata summary
   - `mart_access_pressure` — the accessible pool funnel

5. **Network matching strategy**
   - Start with plan/service-area metadata (high confidence, high coverage)
   - Provider-level network matching only where provider identifiers are actually exposed in selected MRFs
   - Do NOT invent network participation. If the data isn't there, label the output as a selected-plan case study rather than a national count.

6. **Implement analyses**
   - 8.13: Plan service-area breadth (counties/ZIPs per plan)
   - 8.14: Network metadata coverage by state (plans with network URL, plans with MRF URL)
   - 8.15: Accessible pool funnel — all providers → specialty → geography → Medicare-enrolled → network-matched

7. **Build CT dashboard**
   - Use Streamlit or Looker Studio
   - Include at minimum: provider density map, specialty scarcity map, supply vs. utilization scatter, network funnel, provider concentration bar chart
   - Parameterize by state (default = CT)
   - Include methodology notes and data-quality caveats on every chart

8. **Create final charts**
   - Plan service-area comparison (counties covered by selected plans)
   - Selected-plan network funnel (one CT insurer case study)

### Deliverable

- Marketplace data staged and modeled
- CT dashboard with 5+ charts
- Network funnel with documented caveats

### Acceptance Criteria

- `make ingest-marketplace` loads all PUF files
- `make dashboard` launches the CT dashboard from versioned outputs
- Network funnel clearly labels where data is incomplete
- Every chart has a methodology note
- CT is selected through configuration, not hard-coded SQL

---

## Sprint 5 — National Expansion + Story Packaging

**Goal:** Parameterize everything for national runs and generate Medium-ready outputs.

### Why this sprint last

National scale is the validation step. If CT works, national should work without special cases.

### Tasks

1. **Parameterize everything**
   - Replace hard-coded `'CT'` with `config.analysis.yml` parameters throughout
   - Add `target_state`, `target_county`, `target_specialty`, `target_plan_year` config options
   - Verify pipeline runs for at least 3 different states without code changes

2. **Run national pipeline**
   - Execute full pipeline with `target_state = null` (all states)
   - Validate row counts at every layer: raw → staging → core → mart
   - Check join cardinality: no many-to-many explosions, no unexpected row drops
   - Verify year consistency across all fact tables

3. **Build remaining mart**
   - `mart_facility_ecosystem` — hospitals + affiliated clinicians + groups

4. **Complete all 15 analyses**
   - Ensure every analysis is stored as a versioned SQL file in `sql/`
   - Add methodology comments to each file
   - Run all 15 and save outputs to `outputs/tables/`

5. **Generate all charts and maps**
   - Provider density map (national)
   - Specialty scarcity maps (national)
   - Provider → group → facility network graph (national sample)
   - Provider supply vs. utilization scatter (national)
   - Hospital ecosystem map
   - Plan service-area comparison
   - Selected-plan network funnel

6. **Write documentation**
   - `docs/methodology.md` — data sources, grain definitions, join logic, known limitations
   - `docs/story_outline.md` — Medium article structure, narrative flow, chart captions
   - `docs/data_dictionary.md` — column definitions for every core and mart table

7. **Finalize README**
   - Setup instructions
   - How to run the pipeline
   - How to reproduce every chart
   - Known limitations and what the data cannot answer
   - Data quality caveats

8. **Data quality report**
   - Generate `outputs/data_quality_report.csv` from manifest data
   - Include: source, snapshot, rows_loaded, rows_rejected, null_rate, duplicate_rate, checksum

### Deliverable

- National pipeline running end-to-end
- All 15 analyses producing outputs
- Complete documentation package
- README with reproduction instructions and limitations

### Acceptance Criteria

- `make all` runs the full pipeline (ingest → transform → analyze → chart) without errors
- Every published number has a source snapshot and methodology note
- Connecticut results are reproducible from the same pipeline that produces national results
- Every chart is generated from a versioned query/output
- README explains known limitations clearly
- No invented fields, URLs, identifiers, or relationships
- No patient-level PHI used

---

## File Structure (Target)

```
us-healthcare-data/
├── README.md
├── pyproject.toml
├── Makefile
├── .env.example
├── config/
│   ├── sources.yml
│   ├── geography.yml
│   └── analysis.yml
├── ingestion/
│   ├── nppes/
│   ├── cms/
│   ├── census/
│   └── marketplace/
├── db/
│   ├── nppes_raw.duckdb
│   ├── cms_raw.duckdb
│   ├── utilization_raw.duckdb
│   └── warehouse.duckdb
├── staging/
│   ├── stg_npi.sql
│   ├── stg_npi_location.sql
│   ├── stg_clinician.sql
│   ├── stg_affiliation.sql
│   ├── stg_hospital.sql
│   ├── stg_utilization.sql
│   ├── stg_population.sql
│   └── stg_marketplace.sql
├── core/
│   ├── dim_provider.sql
│   ├── dim_organization.sql
│   ├── dim_location.sql
│   ├── dim_specialty.sql
│   ├── dim_facility.sql
│   ├── dim_plan.sql
│   ├── bridge_provider_location.sql
│   ├── bridge_provider_group.sql
│   ├── bridge_provider_facility.sql
│   ├── bridge_plan_service_area.sql
│   ├── fact_provider_utilization.sql
│   └── fact_population.sql
├── mart/
│   ├── mart_provider_supply.sql
│   ├── mart_specialty_supply.sql
│   ├── mart_geographic_access.sql
│   ├── mart_provider_network.sql
│   ├── mart_provider_concentration.sql
│   ├── mart_facility_ecosystem.sql
│   └── mart_access_pressure.sql
├── sql/
│   ├── 01_provider_counts.sql
│   ├── 02_specialty_supply.sql
│   ├── ...
│   └── 15_access_funnel.sql
├── tests/
├── notebooks/
│   ├── 01_profile_sources.ipynb
│   ├── 02_entity_resolution.ipynb
│   └── 03_story_validation.ipynb
├── dashboards/
├── docs/
│   ├── data_dictionary.md
│   ├── methodology.md
│   └── story_outline.md
├── manifests/
│   ├── source_manifest.csv
│   └── data_quality_report.csv
└── outputs/
    ├── tables/
    ├── charts/
    └── maps/
```

---

## Dependencies Between Sprints

```
Sprint 0 (Foundation)
    │
    ▼
Sprint 1 (NPPES + Geography) ──→ Sprint 2 (CMS Clinicians + Facilities)
    │                              │
    │                              ▼
    │                         Sprint 3 (Utilization + Concentration)
    │                              │
    └──────────────────────────────→ Sprint 4 (Marketplace + CT Story)
                                        │
                                        ▼
                                   Sprint 5 (National + Packaging)
```

- **Sprint 1 depends on Sprint 0** (config, directory structure, Make targets)
- **Sprint 2 depends on Sprint 1** (needs `dim_provider` for NPI joins)
- **Sprint 3 depends on Sprint 1 + 2** (needs `dim_provider` + `dim_specialty` for utilization joins)
- **Sprint 4 depends on Sprint 1** (needs `dim_provider` for network matching, but can start in parallel with Sprints 2–3 if `dim_provider` is stable)
- **Sprint 5 depends on all previous sprints** (needs everything parameterized and stable)

---

## What "Done" Looks Like

At the end of Sprint 5, you have:

1. A reproducible pipeline that a new contributor can run from scratch
2. A national healthcare data model in BigQuery with documented schemas and quality checks
3. Connecticut as a validated case study with a dashboard and coherent narrative
4. 15 versioned SQL analyses with methodology comments
5. 10+ charts and maps supporting the Medium article
6. Full documentation: methodology, data dictionary, story outline, known limitations
7. A clear answer to the core question, with honest caveats about what public data can and cannot measure

---

## First Task (Before Any Downloads)

Before writing ingestion code, create:

1. `config/sources.yml` — exact URLs, expected file sizes, schemas
2. `docs/data_dictionary.md` — proposed column names and types for every table
3. `manifests/source_manifest_schema.csv` — manifest column definitions
4. `manifests/data_quality_schema.csv` — data quality report column definitions
5. `notebooks/01_profile_sources.ipynb` — peek at each source file: row counts, column names, sample values, null rates

Then pause for human review before beginning large downloads.
