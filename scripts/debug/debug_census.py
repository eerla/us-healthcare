import requests

url = 'https://api.census.gov/data/2023/acs5?get=NAME,B01003_001E&for=zip+code+tabulation+area:*'
resp = requests.get(url, timeout=60)
print('Status:', resp.status_code)
print('Content-Type:', resp.headers.get('Content-Type'))
print('First 500 chars:', resp.text[:500])