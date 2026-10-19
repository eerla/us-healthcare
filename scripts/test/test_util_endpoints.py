import requests

urls = [
    'https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners/api/1/datastore/query/rvsv-8xg5/0/download?format=csv',
    'https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners/api/1/datastore/query/x3ux-5c9v/0/download?format=csv',
    'https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners/api/1/datastore/query/rvsv-8xg5/0?format=csv',
    'https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners/api/1/datastore/query/rvsv-8xg5/0/download?format=csv&attachment=true',
]

for url in urls:
    resp = requests.get(url, timeout=30, allow_redirects=True)
    ct = resp.headers.get('Content-Type', '')
    size = len(resp.content)
    is_csv = 'text/csv' in ct
    print(f'URL: {url}')
    print(f'  Status: {resp.status_code} | CT: {ct} | Size: {len(resp.content)} | CSV: {is_csv}')
    if is_csv:
        print(f'  First 100: {resp.text[:100]}')
    print()