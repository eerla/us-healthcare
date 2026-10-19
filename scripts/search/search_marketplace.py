import requests

# Search CMS catalog for marketplace datasets
url = 'https://data.cms.gov/api/1/catalog'
params = {'q': 'marketplace', 'limit': 20}
headers = {'Accept': 'application/json'}
resp = requests.get(url, params=params, headers=headers, timeout=30)
print('Status:', resp.status_code)
print('Content-Type:', resp.headers.get('Content-Type'))
print('First 500 chars:', resp.text[:500])