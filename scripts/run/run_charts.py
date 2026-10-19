import duckdb
import time

conn = duckdb.connect('db/warehouse.duckdb')
conn.execute("ATTACH 'db/nppes_raw.duckdb' AS nppes_raw (READ_ONLY)")
conn.execute("ATTACH 'db/census_raw.duckdb' AS census_raw (READ_ONLY)")
conn.execute("ATTACH 'db/cms_raw.duckdb' AS cms_raw (READ_ONLY)")
conn.execute("ATTACH 'db/utilization_raw.duckdb' AS utilization_raw (READ_ONLY)")
conn.execute("ATTACH 'db/marketplace_raw.duckdb' AS marketplace_raw (READ_ONLY)")

charts = [
    ('ct_provider_funnel.png', 'generate_funnel_chart.py'),
    ('ct_specialty_scarcity.png', 'generate_ct_specialty_scarcity.py'),
    ('ct_supply_util_scatter.png', 'generate_ct_supply_util_scatter.py'),
    ('provider_concentration.png', 'generate_concentration_chart.py'),
    ('state_providers_per_100k.png', 'generate_state_providers_per_100k.py'),
    ('ct_zcta_supply_util_scatter.png', 'generate_ct_zcta_supply_util_scatter.py'),
]

for name, script in [
    ('ct_provider_funnel.png', 'generate_funnel_chart.py'),
    ('ct_specialty_scarcity.png', 'generate_ct_specialty_scarcity.py'),
    ('ct_supply_util_scatter.png', 'generate_ct_supply_util_scatter.py'),
    ('provider_concentration.png', 'generate_concentration_chart.py'),
    ('state_providers_per_100k.png', 'generate_state_providers_per_100k.py'),
    ('ct_zcta_supply_util_scatter.png', 'generate_ct_zcta_supply_util_scatter.py'),
]:
    try:
        import subprocess
        subprocess.run(['.venv\\Scripts\\python.exe', script], cwd='C:\\Users\\gurub\\projects\\us-healthcare', timeout=120)
        print(f'{name}: OK')
    except Exception as e:
        print(f'{name}: ERROR - {e}')