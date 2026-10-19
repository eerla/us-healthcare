import duckdb
import subprocess

# Regenerate charts sequentially
charts = [
    ('ct_specialty_scarcity.png', 'generate_ct_specialty_scarcity.py'),
    ('ct_supply_util_scatter.png', 'generate_ct_supply_util_scatter.py'),
    ('provider_concentration.png', 'generate_concentration_chart.py'),
    ('state_providers_per_100k.png', 'generate_state_providers_per_100k.py'),
    ('ct_zcta_supply_util_scatter.png', 'generate_ct_zcta_supply_util_scatter.py'),
]

for name, script in [
    ('ct_specialty_scarcity.png', 'generate_ct_specialty_scarcity.py'),
    ('ct_supply_util_scatter.png', 'generate_ct_supply_util_scatter.py'),
    ('provider_concentration.png', 'generate_concentration_chart.py'),
    ('state_providers_per_100k.png', 'generate_state_providers_per_100k.py'),
    ('ct_zcta_supply_util_scatter.png', 'generate_ct_zcta_supply_util_scatter.py'),
]:
    try:
        subprocess.run(['.venv\\Scripts\\python.exe', script], cwd='C:\\Users\\gurub\\projects\\us-healthcare', timeout=120, check=True)
        print(f'{name}: OK')
    except Exception as e:
        print(f'{name}: ERROR - {e}')