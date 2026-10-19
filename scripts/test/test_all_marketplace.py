import duckdb
import time

conn = duckdb.connect('db/warehouse.duckdb')
conn.execute("ATTACH 'db/nppes_raw.duckdb' AS nppes_raw (READ_ONLY)")
conn.execute("ATTACH 'db/census_raw.duckdb' AS census_raw (READ_ONLY)")
conn.execute("ATTACH 'db/cms_raw.duckdb' AS cms_raw (READ_ONLY)")
conn.execute("ATTACH 'db/utilization_raw.duckdb' AS utilization_raw (READ_ONLY)")
conn.execute("ATTACH 'db/marketplace_raw.duckdb' AS marketplace_raw (READ_ONLY)")

# Test all marketplace staging tables
tables = [
    'staging/stg_marketplace_plan.sql',
    'staging/stg_marketplace_service_area.sql',
    'staging/stg_marketplace_network.sql',
    'staging/stg_marketplace_rate.sql',
    'staging/stg_marketplace_benefits.sql',
    'staging/stg_marketplace_business_rules.sql',
    'staging/stg_marketplace_plan_crosswalk.sql',
    'staging/stg_marketplace_machine_readable_url.sql',
    'staging/stg_marketplace_transparency_coverage.sql',
]

for sql_file in tables:
    start = time.time()
    try:
        conn.execute(open(sql_file).read())
        print(f'{sql_file}: {time.time()-start:.1f}s OK')
    except Exception as e:
        print(f'{sql_file}: ERROR - {e}')

# Check counts
tables_to_check = [
    'stg_marketplace_plan',
    'stg_marketplace_service_area',
    'stg_marketplace_network',
    'stg_marketplace_rate',
    'stg_marketplace_benefits',
    'stg_marketplace_business_rules',
    'stg_marketplace_plan_crosswalk',
    'stg_marketplace_machine_readable_url',
    'stg_marketplace_transparency_coverage',
]
for table in tables_to_check:
    cnt = conn.execute(f'SELECT COUNT(*) FROM staging.{table}').fetchone()[0]
    print(f'{table}: {cnt:,} rows')

conn.close()