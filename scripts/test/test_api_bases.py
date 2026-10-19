import requests

base_urls = [
    'https://data.cms.gov/provider-data/api/1/datastore/query/',
    'https://data.cms.gov/provider-data/api/2/datastore/query/',
    'https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners/api/1/datastore/query/',
    'https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners/api/2/datastore/query/',
    'https://api.cms.gov/api/1/datastore/query/',
    'https://data.cms.gov/api/1/datastore/query/',
    'https://data.cms.gov/api/2/datastore/query/',
]

dataset_id = 'rvsv-8xg5'

for base in base_urls:
    url = f'{base}{dataset_id}/0/download?format=csv'
    resp = requests.get(url, timeout=15)
    ct = resp.headers.get('Content-Type', '')
    size = len(resp.content)
    is_csv = 'text/csv' in ct
    if is_csv and size > 10000:
        print(f'FOUND: {base}')
        print(f'  Status: {resp.status_code} | CT: {resp.headers.get("Content-Type")} | Size: {len(resp.content)}')
        print(f'  First 100: {resp.text[:100]}')
    else:
        print(f'  {base}: {resp.status_code} | {ct[:30]} | {len(resp.content)} bytes')