import requests

# Test marketplace endpoints
urls = [
    'https://data.cms.gov/provider-data/api/1/datastore/query/4hxv-ghmx/0/download?format=csv',
    'https://data.cms.gov/provider-data/api/1/datastore/query/9f8x-7a6e/0/download?format=csv',
    'https://data.cms.gov/provider-data/api/1/datastore/query/8f8x-7a6e/0/download?format=csv',
]

for url in urls:
    resp = requests.get(url, timeout=30, allow_redirects=True)
    print(f'{url[:60]}... -> {resp.status_code} | {resp.headers.get("Content-Type", "")[:40]}')
    if resp.status_code == 200:
        print(f'  First 200: {resp.text[:200]}')