import requests

# Try the Socrata API with different base URLs
base_urls = [
    'https://data.cms.gov/api/1/datastore/query/',
    'https://data.cms.gov/provider-data/api/1/datastore/query/',
    'https://data.cms.gov/provider-data/api/1/datastore/query/',
    'https://data.cms.gov/provider-summary-by-type-of-service/api/1/datastore/query/',
]

# Try the clinician dataset ID pattern for marketplace
test_ids = [
    'mj5m-pzi6',  # known clinician ID
    'rvsv-8xg5',  # known utilization ID
    'x3ux-5c9v',  # known utilization ID
]

for base in base_urls:
    for ds in test_ids:
        url = f'{base}{ds}/0/download?format=csv'
        try:
            resp = requests.get(url, timeout=15)
            ct = resp.headers.get('Content-Type', '')
            size = len(resp.content)
            is_csv = 'text/csv' in ct
            if is_csv and size > 10000:
                print(f'FOUND: {base}{ds} -> {resp.status_code} | {ct} | {size} bytes')
                print(f'  First 100 chars: {resp.text[:100]}')
            elif size > 1000:
                print(f'  {base}{ds}: {resp.status_code} | {ct} | {size} bytes')
        except Exception as e:
            print(f'  {base}{ds}: ERROR - {e}')