# The Geography Problem: Why Where You Live Determines Your Care

In the previous post, I wrote about the provider funnel — how 9.8 million NPIs narrow to roughly 750,000 actively practicing clinicians.

But there's another layer to the access problem: **where those providers are located.**

The data tells a stark story. Providers don't distribute evenly across the country. They cluster in urban centers, affluent suburbs, and areas with hospital systems. Rural counties often have zero specialists of certain types. Some counties have zero cardiologists. Zero psychiatrists. Zero dermatologists.

But here's the part no one tells you: **the Census data I needed to map this didn't exist in a usable form.** I had to build it myself.

---

## The Data Problem: Census Geography Isn't Ready-Made

When I started this project, I assumed Census geography data would be straightforward. Download a shapefile, join it to provider data, map it. Done.

It wasn't that simple.

The Census Bureau publishes TIGER/Line shapefiles and ACS (American Community Survey) data, but they don't come pre-joined. You have to:

1. Download the TIGER/Line shapefiles (geographic boundaries)
2. Download the ACS 5-year estimates (population data)
3. Join them by GEOID (geographic identifier)
4. Handle mismatches between Census vintage years
5. Handle boundary changes between years

And here's the part no one tells you: **the Census API changed mid-project.** The old endpoints that every tutorial references? They return HTML error pages now. The new API requires a free API key, different URL parameters, and different pagination.

I spent days debugging API calls that returned HTML error pages instead of JSON. The documentation was outdated. The examples didn't work. I had to reverse-engineer the correct URL format by trial and error.

```python
# What the old tutorials show (doesn't work):
url = "https://api.census.gov/data/2023/acs5?get=NAME,B01003_001E&for=zip+code+tabulation+area:*"

# What actually works:
url = "https://api.census.gov/data/2023/acs/acs5?get=NAME,B01003_001E&for=zip+code+tabulation+area:*&key=YOUR_KEY"
```

The Census API changed its URL structure mid-project. The old endpoint returns HTML error pages instead of JSON. The new endpoint requires an API key, different URL parameters, and different pagination.

I spent days debugging API calls that returned HTML error pages instead of JSON. The documentation was outdated. The examples didn't work. I had to reverse-engineer the correct URL format by trial and error.

---

## The ZCTA Problem: ZIP Codes Aren't Counties

Here's something most people don't know: **ZIP codes aren't geographic areas.** They're mail delivery routes. A single ZIP code can span multiple counties. A single county can have multiple ZIP codes.

The Census Bureau created ZCTAs (ZIP Code Tabulation Areas) as a workaround — approximations of ZIP code service areas that align with census block boundaries. But even ZCTAs don't perfectly align with counties or provider locations.

When I tried to join provider locations to Census population data by ZCTA, I found:

- Some ZCTAs span multiple counties
- Some counties have multiple ZCTAs
- Some ZCTAs cross state lines
- Some ZCTAs have no population (PO boxes, business parks)

This means any analysis that joins providers to population by ZIP code is inherently approximate. The error rate varies by geography — rural areas with large ZCTAs have more error than urban areas with small, dense ZCTAs.

---

## The Provider Distribution Problem

![State Provider Count](/outputs/charts/state_provider_count.png)

When you look at providers per 100,000 population by state, the variation is stark:

- Massachusetts: 435 providers per 100k
- Mississippi: 134 providers per 100k
- District of Columbia: 7,849 per 100k (geographic artifact of a small, dense jurisdiction)

But even within states, the distribution is uneven. California has 1.18 million providers — but they're concentrated in Los Angeles, San Francisco, and San Diego. Rural California counties have far fewer providers per capita.

![Providers per 100k](/outputs/charts/state_providers_per_100k.png)

The map shows a clear pattern: provider density correlates with population density and wealth. Urban coastal areas have high provider density. Rural interior counties have few providers per capita.

---

## The Real Problem: Distribution, Not Supply

Here's what the data actually shows:

**The US doesn't have a provider shortage. It has a distribution problem.**

9.8 million NPIs. 1.3 million clinicians billing Medicare. 5,400 hospitals. But they're not where the patients are. They're where the hospitals are, where the medical schools are, where the affluent suburbs are.

Rural counties have fewer providers per capita. Rural patients travel farther for care. Rural hospitals close more often. Rural patients delay care longer.

But here's the part no one talks about: **even within urban areas, there are provider deserts.** Neighborhoods with no primary care providers. Neighborhoods with no psychiatrists. Neighborhoods where the nearest dermatologist is 30 miles away.

The data shows this clearly when you look at ZCTA-level data.

![CT ZCTA Supply/Utilization Scatter](/outputs/charts/ct_zcta_supply_util_scatter.png)

The ZCTA scatter shows an interesting pattern: some ZIP codes have high provider density but low utilization (potential oversupply), others have low density but high utilization (capacity strain). The outliers are worth investigating — they're often areas with hospital systems drawing patients from surrounding regions.

---

## What This Means

The provider shortage isn't a simple numbers problem. It's a distribution problem. It's an access problem. It's an insurance network problem. It's a poverty problem.

The data shows:

1. **Providers concentrate where patients can pay** — affluent areas, urban areas, areas with good insurance coverage
2. **Providers avoid where patients can't pay** — rural areas, high-poverty areas, areas with high uninsured rates
3. **Insurance networks exacerbate the problem** — even when providers exist, insurance networks may not include them
4. **Geography determines access** — where you live determines what care you can get, not just what you need

---

## What's Next

The pipeline is done. The charts are generated. The analyses are versioned in `sql/` and the outputs are in `outputs/`.

But the questions remain:

- **How do we measure panel capacity?** Medicare utilization gives us a lower bound. Commercial claims data would help but isn't public.
- **How do we measure access?** Distance to provider is a proxy. Network adequacy standards exist for Medicare Advantage and Medicaid but aren't enforced for commercial plans.
- **What about the uninsured?** The 26 million uninsured Americans don't show up in Medicare utilization data at all.

The data pipeline is reproducible. The code is on GitHub. The charts are in `outputs/charts/`. The analyses are in `sql/analysis_*.sql`.

If you want to run this for your state, change `target_state` in `config/analysis.yml` and run `make all`.

The paradox remains: 9.8 million providers on paper, 26-day average wait for an appointment. The data explains *where* the gaps are. Fixing them requires policy, not just better queries.

---

**Charts referenced in this post:**
- State Provider Count: `outputs/charts/state_provider_count.png`
- Providers per 100k: `outputs/charts/state_providers_per_100k.png`
- CT ZCTA Supply/Utilization: `outputs/charts/ct_zcta_supply_util_scatter.png`

*All charts generated from versioned SQL in `sql/` and Python scripts in `scripts/generate/`.*

---

*Next: Building the pipeline — how I built a national healthcare data pipeline in Python/DuckDB, what I learned, and what I'd do differently.*