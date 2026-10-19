import requests
url = 'https://data.cms.gov/provider-data/api/1/datastore/query/mj5m-pzi6/0?limit=10&offset=0'
resp = requests.get(url, timeout=30)
print('Status:', resp.status_code)
print('Content-Type:', resp.headers.get('Content-Type'))
print('First 500 chars:', resp.text[:500])