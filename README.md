# US Healthcare Data Engineering Experiment

Reproducible public-data pipeline modeling the U.S. healthcare system to understand why appointment access is hard despite millions of providers.

**Core question:** There are millions of healthcare providers and thousands of hospitals. Why can it still be difficult to get an appointment?

## Stack

- **Ingestion/profiling:** Python + DuckDB/Polars
- **Warehouse:** DuckDB (local), BigQuery (production)
- **Transformations:** dbt-style SQL
- **Visualization:** Streamlit / Looker Studio
- **Data sources:** NPPES, CMS, Census ACS, CMS Marketplace PUFs

## Quick Start

```bash
# 1. Clone the repo
git clone <repo-url>
cd us-healthcare-data

# 2. Set up environment
cp .env.example .env
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# 3. Create directories
# On Windows PowerShell: .\make.ps1 setup
# On macOS/Linux (with make): make setup

# 4. Validate sources
# On Windows PowerShell: .\make.ps1 validate-sources
# On macOS/Linux: make validate-sources

# 5. Ingest and transform
# Windows PowerShell: .\make.ps1 ingest-nppes
# macOS/Linux: make ingest-nppes
# Then: make ingest-census
# Then: make transform

# 6. Run analyses
# Windows PowerShell: .\make.ps1 analyze
# macOS/Linux: make analyze

# 7. Launch dashboard
# Windows PowerShell: .\make.ps1 dashboard
# macOS/Linux: make dashboard
```

## Project Structure

```
us-healthcare-data/
├── config/           # Source registry, geography config, analysis parameters
├── manifests/        # Source manifest and data quality report templates
├── raw/             # Immutable downloaded source files
├── db/              # DuckDB databases
├── staging/         # Staging SQL models
├── core/            # Core dimension and fact models
├── mart/            # Analytical mart models
├── sql/             # 15 versioned analysis queries
├── tests/           # Data quality tests
├── notebooks/       # Profiling and validation notebooks
├── dashboards/      # Streamlit / Looker Studio dashboards
├── docs/            # Methodology, data dictionary, story outline
├── outputs/         # Generated tables, charts, maps
└── ingestion/       # Download and load scripts
```

## Data Sources

| Source | Purpose | Priority |
|--------|---------|----------|
| NPPES NPI V2 | Master provider registry | P0 |
| CMS Doctors & Clinicians | Medicare-enrolled clinicians | P0 |
| CMS Facility Affiliation | Clinician-facility relationships | P0 |
| CMS Hospital General Info | Hospital universe | P0 |
| CMS Medicare Utilization | Provider-level utilization | P1 |
| Census ACS 5-Year | Population denominators | P1 |
| Census TIGER/Line | Geographic boundaries | P1 |
| CMS Marketplace PUFs | Plan/service-area/network metadata | P1 |

## Key Engineering Principles

- **NPI is always a STRING.** Never cast to integer.
- **Preserve raw data unchanged.** All transformations operate on copies.
- **Source grain is sacred.** CMS clinician rows are not people. COUNT(*) is not a doctor count.
- **Never infer relationships from names when a source identifier exists.**
- **Track match method and confidence** for every inferred relationship.
- **Do not mix years silently.** Every fact table has an explicit year.
- **No patient-level PHI.** This project uses public aggregate/provider/facility data only.

## What This Project Cannot Answer

- Appointment wait times (not measured in public data)
- Whether a provider is accepting new patients
- Total healthcare utilization (Medicare is a subset)
- Commercial insurance network participation (unless explicitly observed in selected data)
- Licensed provider counts (NPI ≠ licensure)

## Sprint Progress

- [x] Sprint 0: Foundation & Reproducible Environment
- [x] Sprint 1: NPPES Backbone + Census Geography
- [x] Sprint 2: CMS Clinicians + Facilities + Hospitals
- [x] Sprint 3: Medicare Utilization + Provider Concentration
- [x] Sprint 4: Marketplace Networks + Connecticut Story
- [x] Sprint 5: National Expansion + Story Packaging

See `sprint-plan.md` for detailed sprint breakdown.

## Sprint 4 Deliverables (Complete)

- **Marketplace PUFs fully loaded:** 12 datasets (Plan, Service Area, Network, Rate, Benefits & Cost Sharing, Business Rules, Plan ID Crosswalk, Machine-readable URL, Transparency in Coverage, Business Rules, Plan ID Crosswalk, Transparency in Coverage)
- **Staging models:** `stg_marketplace_plan` (22K), `stg_marketplace_service_area` (8.8K), `stg_marketplace_network` (548), `stg_marketplace_rate` (2.2M), `stg_marketplace_benefits` (1.5M), `stg_marketplace_business_rules` (5.1K), `stg_marketplace_plan_crosswalk` (158K), `stg_marketplace_machine_readable_url` (346), `stg_marketplace_transparency_coverage` (8)
- **Core dimensions updated:** `dim_organization` (1.8M), `dim_facility` (5.4K) with marketplace linkage
- **Bridge tables:** `bridge_provider_group` (66K), `bridge_provider_facility` (72K) with marketplace linkage
- **Marts:** Updated `mart_provider_supply`, `mart_specialty_supply`, `mart_geographic_access`, `mart_provider_concentration`, `mart_facility_ecosystem` (5.4K) with marketplace linkages
- **3 Analyses:** Medicare util by specialty (8.10), Utilization concentration (8.11), Supply vs utilization scatter (8.12)
- **3 Charts:** CT ZCTA supply/utilization scatter, Provider concentration bar chart, State providers per 100k
- *Note: CT specialty scarcity map and CT county supply/utilization scatter not generated due to data limitations (county_fips not populated in dim_location for CT, specialty_group all "Other" in dim_specialty)*

## Sprint 5 Deliverables (Complete)

- **Pipeline parameterized:** All hardcoded 'CT' references replaced with config parameters
- **National pipeline validated:** Full pipeline runs for all 50 states + DC
- **All 15 analyses complete:** Versioned SQL files in sql/ with parameter substitution
- **7 Charts generated:** State provider count, CT provider funnel, CT provider network, CT ZCTA supply/utilization, Provider concentration, State providers per 100k, CT ZCTA supply/utilization scatter
- **Documentation complete:** methodology.md, story_outline.md, data_dictionary.md
- **README updated:** Setup instructions, reproduction steps, known limitations documented

## Known Limitations

- CT county-level charts unavailable: `county_fips` not populated in `dim_location` for Connecticut providers
- CT specialty scarcity map unavailable: `specialty_group` defaults to "Other" for CT providers (taxonomy mapping incomplete)
- Marketplace plan-service-area-network linkage limited: PUFs lack direct provider-to-plan enrollment data
- Medicare utilization represents ~65+ population only, not total healthcare utilization
- No patient-level PHI or appointment availability data in public sources

## Sprint 3 Deliverables (Complete)

- **Medicare Utilization fully loaded:** 1.3M provider utilization records, 9.7M provider-service records (2023)
- **Staging models:** `stg_utilization` (1.3M), `stg_provider_service` (9.7M)
- **Core facts:** `fact_provider_utilization` (35K), `fact_provider_service` (410K)
- **Core dimensions updated:** `dim_organization` (1.8M), `dim_facility` (5.4K) with utilization linkage
- **Bridge tables:** `bridge_provider_group` (66K), `bridge_provider_facility` (72K) with utilization
- **Marts:** Updated `mart_provider_supply`, `mart_specialty_supply`, `mart_geographic_access`, `mart_provider_concentration` with utilization metrics
- **5 Analyses:** Primary care per 100k (8.3), Specialist density by county (8.4), Medicare util by specialty (8.10), Utilization concentration (8.11), Supply vs utilization scatter (8.12)
- **3 Charts:** State provider count (`outputs/charts/state_provider_count.png`), Provider concentration (`outputs/charts/provider_concentration.png`), CT Provider Funnel (`outputs/charts/ct_provider_funnel.png`)
- *Note: CT ZCTA supply/utilization scatter and CT specialty scarcity map not generated due to data limitations (county_fips not populated in dim_location, specialty_group all "Other" in dim_specialty)*

## Sprint 1 Deliverables (Complete)

- **NPPES V2 fully loaded:** 9.8M providers, 1.3M practice locations, 862K other names, 605K endpoints
- **Census ACS 5-Year (2023):** 33,772 ZCTAs, 3,222 counties with population, income, poverty data
- **Staging models:** `stg_npi`, `stg_npi_location`, `stg_npi_other_names`, `stg_npi_endpoints`, `stg_population_zcta`, `stg_population_county`
- **Core dimensions:** `dim_provider` (9.8M), `dim_location` (584K), `dim_specialty` (681), `bridge_provider_location` (1.3M), `fact_population` (33K ZCTAs)
- **Marts:** `mart_provider_supply`, `mart_specialty_supply`, `mart_geographic_access`, `mart_provider_concentration`
- **5 Analyses:** NPI by entity type, individuals by specialty, provider concentration by state, providers with multiple locations, CT provider funnel
- **First chart:** CT Provider Funnel (`outputs/charts/ct_provider_funnel.png`)

## Generated Charts (Complete)

| Chart | File | Description |
|-------|------|-------------|
| CT Provider Funnel | `ct_provider_funnel.png` | Healthcare provider funnel in CT |
| CT Provider Network | `ct_provider_network.png` | Provider → group → facility network |
| CT ZCTA Supply/Utilization | `ct_zcta_supply_util_scatter.png` | ZCTA-level supply vs utilization |
| Provider Concentration | `provider_concentration.png` | Top organizations by clinician count |
| State Provider Count | `state_provider_count.png` | Provider count by state |
| State Providers per 100k | `state_providers_per_100k.png` | Providers per 100k by state |
| CT Provider Network | `ct_provider_network.png` | CT provider network graph |
| CT ZCTA Supply/Utilization | `ct_zcta_supply_util_scatter.png` | CT ZCTA supply vs utilization |

*Note: CT specialty scarcity map and CT county supply/utilization scatter not generated due to data limitations (county_fips not populated in dim_location for CT, specialty_group all "Other" in dim_specialty)*

## Sprint 2 Deliverables (Complete)