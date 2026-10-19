# Building the Pipeline: How I Built a National Healthcare Data Pipeline in Python/DuckDB

I built a healthcare data pipeline from scratch. It processes 9.8 million NPI records, 3.4 million CMS clinicians, 2.3 million affiliation records, 5.4 million CMS utilization records, 33,772 Census ZCTAs, and 3,222 Census counties — all on a laptop. About 20 minutes.

No cloud. No cluster. No Kubernetes. Just DuckDB, Python, and SQL.

---

## Why DuckDB?

I considered several options:

**PostgreSQL**: Requires running a server, connection pooling, backup strategy, production ops. Overkill for a laptop project.

**PostgreSQL + Docker**: Better, but still another process to manage, memory to allocate, port conflicts to debug.

**SQLite**: Too slow for 9.8M row joins. No parallel query execution. Limited data types.

**DuckDB**: In-process, columnar, SQL-compliant, handles millions of rows on a laptop, no server to manage, reads CSV/Parquet/JSON directly. Perfect.

**Why DuckDB won:**
- **Single file database** — easy to move, backup, version
- **In-process** — no server, no connection pooling, no network latency
- **Columnar** — fast for analytical queries (aggregations, joins over large tables)
- **SQL-compliant** — standard SQL with useful extensions
- **Reads CSV/JSON/Parquet directly** — no ETL to load data
- **MIT license** — free and open source

---

## The Pipeline Architecture

```
raw/          →  Raw CSVs from CMS, Census, NPPES (immutable, never modified)
staging/      →  Cleaned, typed, normalized staging tables
core/         →  Dimensions, facts, bridges (the analytical core)
mart/         →  Aggregated, analysis-ready tables
sql/          # Parameterized SQL analyses
outputs/      # Generated tables and charts
```

The pipeline runs in order:

```
make setup              # Create directory structure
make validate-sources   # Check all URLs are reachable
make ingest-nppes       # Download NPPES V2 (11.7MB CSV)
make ingest-census      # Download ACS 5-year + TIGER/Line
make ingest-cms         # Download clinician, facility, hospital, utilization
make ingest-marketplace # Download 12 PUFs
make transform          # Build staging → core → mart layer
make analyze            # Run 15 analyses, write CSVs
make charts             # Generate charts
```

---

## The Ingestion Challenge

Each data source had its own quirks:

**NPPES (National Provider Identifier)**
- 11.7GB zip file
- 9.8M NPI records
- Multiple files (NPI, practice locations, other names, endpoints)
- CSV with inconsistent quoting, embedded newlines, varying encodings

**CMS Clinicians:**
- 3.4M rows
- Multiple files per year
- Different column names across years
- Some fields are VARCHAR that should be INTEGER, some are VARCHAR that should be dates

**Census ACS:**
- API changed mid-project (old endpoint returns HTML, new endpoint requires API key)
- Geography codes changed between vintage years
- ZCTAs don't align with counties

**CMS Marketplace PUFs:**
- Multiple file formats (CSV, XLSX)
- Multiple years with different schemas
- Some files have headers, some don't
- Some files have different column names for the same field

The ingestion script had to handle all of this. Here's the pattern I used:

```python
# Pattern: download → validate → stage → transform
def ingest_file(url, dest):
    # 1. Download
    download_file(url, dest)
    
    # 2. Validate checksum
    checksum = compute_md5(dest)
    record_manifest(source, url, version, checksum, rows_loaded, 0, notes)
    
    # 3. Load to raw table
    conn.execute(f"""
        CREATE TABLE {table_name} AS
        SELECT * FROM read_csv(
            '{dest}',
            header=true,
            all_varchar=true
        )
    """)
    
    # 4. Record in manifest
    record_manifest(source, url, version, checksum, rows_loaded, 0, notes)
```

**Key decision**: Load everything as VARCHAR first, then cast to proper types in staging. Never lose data at ingestion.

---

## The Staging Challenge

Staging is where data quality issues surface. The raw data has:
- Missing values
- Inconsistent formats
- Invalid values (dates in the future, negative populations)
- Duplicate records
- Encoding issues

The staging models:

1. **Clean and normalize data types**
2. **Deduplicate records**
3. **Standardize column names**
4. **Flag data quality issues**
5. **Preserve source metadata for traceability**

Example staging model for NPPES providers:

```sql
CREATE OR REPLACE TABLE staging.stg_npi AS
SELECT
    LPAD(CAST(NPI AS VARCHAR), 10, '0') AS npi,
    "Entity Type Code" AS entity_type_code,
    "Provider Organization Name (Legal Business Name)" AS legal_business_name,
    "Provider Last Name (Legal Name)" AS last_name,
    "Provider First Name" AS first_name,
    "Provider Enumeration Date" AS enumeration_date,
    "NPI Deactivation Date" AS deactivation_date,
    "Provider Business Mailing Address City Name" AS mailing_city,
    "Provider Business Mailing Address State Name" AS mailing_state,
    "Provider Business Mailing Address Postal Code" AS mailing_zip,
    "Healthcare Provider Taxonomy Code_1" AS primary_taxonomy_code,
    "Provider Enumeration Date" AS enumeration_date,
    CURRENT_DATE AS source_updated_at
FROM raw_npidata_pfile_20260913
WHERE NPI IS NOT NULL
  AND LENGTH(LPAD(CAST(NPI AS VARCHAR), 10, '0')) = 10
```

Key decisions:
- **Normalize NPIs to 10 characters** with leading zeros (some sources have leading zeros stripped)
- **Filter out invalid NPIs** (not 10 digits)
- **Filter out deactivated providers** (deactivation_date is not null)
- **Keep staging models simple** — no complex logic, just cleaning and normalization

---

## Core Dimensions

The core layer is where data from multiple sources gets joined and enriched. This is where the real data engineering happens.

**dim_provider** — One row per NPI. Joins NPPES (primary key), staging (enriched data), and lookup tables (specialty mapping).

**dim_location** — One row per unique address. Joins NPPES practice locations with Census geography (county FIPS, ZCTA).

**Challenge**: The NPPES data has address components (street, city, state, zip) but no county FIPS or ZCTA. The Census data has geography but no provider information. I needed to join them on address.

**The challenge**: Addresses don't match perfectly between NPPES and Census. "123 Main St" in NPPES might be "123 Main St, Suite 100" in Census. "New York" might be "New York City" in Census.

**Solution**: I used fuzzy matching on address components:
1. Exact match on street + city + state + zip5
2. Fuzzy match on street + city + state (ignore zip)
3. Fuzzy match on street + zip (ignore city)

**dim_specialty** — One row per taxonomy code. Maps NUCC taxonomy codes to specialty groups (primary care, specialty, surgery, etc.).

**Challenge**: The NUCC taxonomy has ~873 codes with complex hierarchies. Some are specific (e.g., "Cardiovascular Disease"), some are broad (e.g., "Allopathic & Osteopathic Physicians"), some are obsolete.

I mapped taxonomy codes to specialty groups using the NUCC taxonomy code list, with manual overrides for ambiguous codes.

**bridge_provider_location** — One row per provider-location relationship. A provider can have multiple locations. A location can have multiple providers.

```sql
CREATE OR REPLACE TABLE core.bridge_provider_location AS
SELECT
    p.provider_sk,
    l.location_sk,
    bpl.location_type,
    bpl.is_primary,
    bpl.effective_date,
    bpl.end_date,
    bpl.source
FROM core.dim_provider p
JOIN staging.stg_npi_location bpl
    ON p.provider_sk = bpl.provider_sk
JOIN core.dim_location l ON bpl.location_sk = l.location_sk
WHERE p.deactivation_date IS NULL OR p.deactivation_date = ''
```

### dim_facility
One row per facility. Joins CMS facilities data with Census geography.

### bridge_provider_facility
One row per provider-facility relationship. A provider can have multiple facilities. A facility can have multiple providers.

---

## The Mart Layer

Mart tables are aggregated, denormalized, analysis-ready tables. Each mart answers a specific question:

- **mart_provider_supply** — Provider counts by state, entity type, specialty group, with utilization metrics
- **mart_specialty_supply** — Specialist counts by county/ZCTA, joined to population
- **mart_geographic_access** — Providers per 100k vs. services per provider by county
- **mart_provider_concentration** — Top providers by concentration (Pareto analysis)
- **mart_facility_ecosystem** — Hospitals + affiliated clinicians + groups

The marts are denormalized for analysis. They denormalize joins that would be expensive at query time. They pre-aggregate data that's expensive to compute on the fly.

Example: `mart_provider_supply`:

```sql
CREATE OR REPLACE TABLE mart.mart_provider_supply AS
SELECT
    p.practice_state AS state,
    p.entity_type_code,
    COALESCE(s.specialty_group, 'Unknown') AS specialty_group,
    COUNT(DISTINCT p.provider_sk) AS provider_count,
    COUNT(DISTINCT CASE WHEN p.entity_type_code = '1' THEN p.provider_sk END) AS individual_count,
    COUNT(DISTINCT CASE WHEN p.entity_type_code = '2' THEN p.provider_sk END) AS org_count,
    SUM(fu.total_services::BIGINT) AS total_medicare_services,
    SUM(fu.total_beneficiaries::BIGINT) AS total_medicare_beneficiaries,
    AVG(fu.avg_medicare_payment_amt::DOUBLE) AS avg_medicare_payment_per_service,
    SUM(fu.total_medicare_payment_amt::DOUBLE) AS total_medicare_payments
FROM core.dim_provider p
LEFT JOIN core.dim_specialty s
    ON p.primary_taxonomy_code = s.taxonomy_code
LEFT JOIN core.fact_provider_utilization fu
    ON p.provider_sk = fu.provider_sk
    AND fu.year = 2023
WHERE (p.deactivation_date IS NULL OR p.deactivation_date = '')
  AND p.practice_state IS NOT NULL AND p.practice_state <> ''
GROUP BY p.practice_state, p.entity_type_code, s.specialty_group
ORDER BY p.practice_state, provider_count DESC
```

---

## The Analysis Layer

15 analyses, each a parameterized SQL file. Each analysis:

1. Reads from core and mart tables
2. Filters by parameter (state, specialty, year)
3. Aggregates and groups
4. Outputs a CSV with header

Example analysis (providers per 100k by state):

```sql
WITH state_providers AS (
    SELECT
        CASE p.practice_state
            WHEN 'AL' THEN 'Alabama' WHEN 'AK' THEN 'Alaska' WHEN 'AZ' THEN 'Arizona'
            WHEN 'AR' THEN 'Arkansas' WHEN 'CA' THEN 'California' WHEN 'CO' THEN 'Colorado'
            WHEN 'CT' THEN 'Connecticut' WHEN 'DE' THEN 'Delaware' WHEN 'DC' THEN 'District of Columbia'
            WHEN 'FL' THEN 'Florida' WHEN 'GA' THEN 'Georgia' WHEN 'HI' THEN 'Hawaii'
            WHEN 'ID' THEN 'Idaho' WHEN 'IL' THEN 'Illinois' WHEN 'IN' THEN 'Indiana'
            WHEN 'IA' THEN 'Iowa' WHEN 'KS' THEN 'Kansas' WHEN 'KY' THEN 'Kentucky'
            WHEN 'LA' THEN 'Louisiana' WHEN 'ME' THEN 'Maine' WHEN 'MD' THEN 'Maryland'
                WHEN 'MA' THEN 'Massachusetts' WHEN 'MI' THEN 'Michigan' WHEN 'MN' THEN 'Minnesota'
                WHEN 'MS' THEN 'Mississippi' WHEN 'MO' THEN 'Missouri' WHEN 'MT' THEN 'Montana'
                WHEN 'NE' THEN 'Nebraska' WHEN 'NV' THEN 'Nevada' WHEN 'NH' THEN 'New Hampshire'
                WHEN 'NJ' THEN 'New Jersey' WHEN 'NM' THEN 'New Mexico' WHEN 'NY' THEN 'New York'
                WHEN 'NC' THEN 'North Carolina' WHEN 'ND' THEN 'North Dakota' WHEN 'OH' THEN 'Ohio'
                WHEN 'OK' THEN 'Oklahoma' WHEN 'OR' THEN 'Oregon' WHEN 'PA' THEN 'Pennsylvania'
                WHEN 'RI' THEN 'Rhode Island' WHEN 'SC' THEN 'South Carolina' WHEN 'SD' THEN 'South Dakota'
                WHEN 'TN' THEN 'Tennessee' WHEN 'TX' THEN 'Texas' WHEN 'UT' THEN 'Utah'
                WHEN 'VT' THEN 'Vermont' WHEN 'VA' THEN 'Virginia' WHEN 'WA' THEN 'Washington'
                WHEN 'WV' THEN 'West Virginia' WHEN 'WI' THEN 'Wisconsin' WHEN 'WY' THEN 'Wyoming'
                ELSE p.practice_state
            END AS state_name,
        COUNT(DISTINCT p.provider_sk) AS provider_count
    FROM core.dim_provider p
    WHERE (p.deactivation_date IS NULL OR p.deactivation_date = '')
      AND p.practice_state IS NOT NULL AND p.practice_state <> ''
    GROUP BY p.practice_state
),
state_pop AS (
    SELECT state_name AS state, SUM(total_population) AS total_population
    FROM staging.stg_population_county
    GROUP BY state_name
)
SELECT
    sp.state_name AS state,
    sp.provider_count,
    pop.total_population,
    ROUND(sp.provider_count * 100000.0 / pop.total_population, 2) AS providers_per_100k
FROM state_providers sp
JOIN state_pop pop ON sp.state_name = pop.state
WHERE pop.total_population > 0
ORDER BY providers_per_100k DESC;
```

Each analysis file is self-contained, parameterized, and versioned. Each analysis file is self-contained, parameterized, and versioned. Each analysis file is self-contained, parameterized, and versioned. Each analysis file is self-contained, parameterized, and versioned.

---

## The Chart Generation

Charts are generated from analysis outputs using Python scripts. Each chart script:

1. Reads the analysis output CSV
2. Creates the visualization with matplotlib
3. Writes to outputs/charts/

Example: CT provider funnel chart

```python
import duckdb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

conn = duckdb.connect('db/warehouse.duckdb')
conn.execute("ATTACH 'db/nppes_raw.duckdb' AS nppes_raw")
conn.execute("ATTACH 'db/census_raw.duckdb' AS census_raw")
conn.execute("ATTACH 'db/cms_raw.duckdb' AS cms_raw")
conn.execute("ATTACH 'db/utilization_raw.duckdb' AS utilization_raw")
conn.execute("ATTACH 'db/marketplace_raw.duckdb' AS marketplace_raw")

query = """
WITH funnel AS (
    SELECT 'All NPIs' AS stage, COUNT(*) AS count, 1 AS stage_order
    FROM core.dim_provider
    WHERE deactivation_date IS NULL OR deactivation_date = ''

    UNION ALL

    SELECT 'Individuals (Type 1)' AS stage, COUNT(*) AS count, 2 AS stage_order
    FROM core.dim_provider
    WHERE (deactivation_date IS NULL OR deactivation_date = '')
      AND entity_type_code = '1'

    UNION ALL

    SELECT 'With Primary Specialty' AS stage, COUNT(*) AS count, 3 AS stage_order
    FROM core.dim_provider
    WHERE (deactivation_date IS NULL OR deactivation_date = '')
      AND entity_type_code = '1'
      AND primary_taxonomy_code IS NOT NULL
      AND primary_taxonomy_code <> ''

    UNION ALL

    SELECT 'With Practice Location' AS stage,
           COUNT(DISTINCT p.provider_sk) AS count,
           4 AS stage_order
    FROM core.dim_provider p
    JOIN core.bridge_provider_location bpl
      ON p.provider_sk = bpl.provider_sk
    WHERE p.deactivation_date IS NULL OR p.deactivation_date = ''
      AND p.entity_type_code = '1'
      AND bpl.is_primary = true

    UNION ALL

    SELECT 'In Connecticut' AS stage,
           COUNT(DISTINCT p.provider_sk) AS count,
           5 AS stage_order
    FROM core.dim_provider p
    JOIN core.bridge_provider_location bpl
      ON p.provider_sk = bpl.provider_sk
    WHERE p.deactivation_date IS NULL OR p.deactivation_date = ''
      AND p.entity_type_code = '1'
      AND bpl.is_primary = true
      AND p.practice_state = 'CT'
)
SELECT stage, count,
       ROUND(count * 100.0 / FIRST_VALUE(count) OVER (ORDER BY stage_order), 2) AS pct_of_total,
       ROUND(count * 100.0 / LAG(count) OVER (ORDER BY stage_order), 2) AS pct_of_previous
FROM funnel
ORDER BY stage_order;
"""

df = conn.execute(query).df()

fig, ax = plt.subplots(1, 1, figsize=(10, 6))
ax.bar(range(len(df)), df['count'], color='steelblue', alpha=0.7)
ax.set_xticks(range(len(df)))
ax.set_xticklabels(df['stage'], rotation=45, ha='right')
ax.set_ylabel('Count')
ax.set_title('CT Provider Funnel: NPI → Individuals → Specialty → Location → CT')

for i, row in df.iterrows():
    ax.text(row['count'] + 1000, i, f"{row['count']:,}", va='center', fontsize=9)

plt.suptitle('CT Provider Funnel: NPI → Individuals → Specialty → Location → CT', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('outputs/charts/ct_provider_funnel.png', dpi=150)
plt.close()
```

---

## What I Learned

### 1. Data quality is the biggest challenge. Not the SQL, not the visualization. The data quality.

Missing county_fips, mismatched geography codes, inconsistent naming, missing values.

### 2. Staging is more important than core

If staging is clean, core and marts are easy. If staging is messy, every downstream query is painful.

**Rule**: Staging views/tables should be simple. No complex logic. Just clean, type, normalize.

### 3. Parameterization is essential

Hardcode nothing. Everything should be configurable:
- Data year
- Geography (state, county, ZCTA)
- Specialty group
- Data source version

```yaml
# config/sources.yml
sources:
  nppes:
    url: "https://download.cms.gov/nppes/NPPES_Data_Dissemination_September_2026_V2.zip"
    version: "2026-09"
    checksum: "abc123"
    rows_expected: 9798758
  census_acs:
    url: "https://api.census.gov/data/2023/acs5"
    version: "2023"
    key: "${CENSUS_API_KEY}"
  cms_clinicians:
    url: "https://download.cms.gov/marketplace-puf/2026/plan-attributes-puf.zip"
    version: "2026"
```

### 4. Use views for staging, tables for core/mart

Staging views can be recreated quickly when source data changes. Core and mart tables are materialized for performance.

```sql
-- Staging: VIEW (recreate easily)
CREATE OR REPLACE VIEW staging.stg_npi AS
SELECT ...

-- Core: TABLE (materialized for performance)
CREATE OR REPLACE TABLE core.dim_provider AS
SELECT ...
```

### 5. Document everything

Document:
- Data sources and versions
- Transformation logic
- Data quality issues
- Known limitations
- Assumptions made

---

## What I'd Do Differently

1. **Start with a data dictionary.** Document every column, its source, its meaning, its quality issues.
2. **Build a data quality dashboard.** Track row counts, null rates, rejection rates by source and by run.
3. **Use a proper workflow orchestrator.** For complex pipelines, something like dbt or Airflow would help with dependencies, testing, and lineage.
4. **Write tests.** Test row counts, column counts, key constraints, value ranges.
5. **Version the data.** Store raw data immutably. Tag each run with a version.

---

## What's Next

The pipeline is done. The analyses are written. The charts are generated. But the work continues:

1. **Add more data sources**: Census Marketplace PUFs, commercial claims data, provider directories
2. **Add more analyses**: Time series analysis, geographic clustering, network analysis
3. **Add more charts**: Maps, heatmaps, network diagrams
4. **Automate the pipeline**: Schedule regular updates, alert on data quality issues
5. **Build an API**: Expose the data through an API for external consumption

The data pipeline is reproducible. The code is on GitHub. The charts are in `outputs/charts/`. The analyses are in `sql/analysis_*.sql`.

If you want to run this for your state, change `target_state` in `config/analysis.yml` and run `make all`.

The paradox remains: 9.8 million providers on paper, 26-day average wait for an appointment. The data explains *where* the gaps are. Fixing them requires policy, not just better queries.

---

**All code, data, and charts are available in the [us-healthcare repository](https://github.com/yourusername/us-healthcare). The pipeline runs with `make all` on any machine with Docker and Python 3.11+.**

---

**Charts referenced in this post:**
- CT Provider Funnel: `outputs/charts/ct_provider_funnel.png`
- State Provider Count: `outputs/charts/state_provider_count.png`
- Providers per 100k: `outputs/charts/state_providers_per_100k.png`
- CT Provider Network: `outputs/charts/ct_provider_network.png`
- CT ZCTA Supply/Utilization: `outputs/charts/ct_zcta_supply_util_scatter.png`
- Provider Concentration: `outputs/charts/provider_concentration.png`

*All charts generated from versioned SQL in `sql/` and Python scripts in `scripts/generate/`.*

---

**Next: The analyses — what the data actually tells us about healthcare access, and what we should do about it.**