import requests

# Try different API endpoint formats
urls = [
    'https://api.census.gov/data/2023/acs/acs5?get=NAME,B01003_001E&for=zip+code+tabulation+area:*',
    'https://api.census.gov/data/2023/acs/acs5?get=NAME,B01003_001E&for=zip+code+tabulation+area:*',
    'https://api.census.gov/data/2023/acs/acs5/profile?get=NAME,DP05_0001E&for=zip+code+tabulation+area:*',
]

for url in urls:
    print('Testing:', url[:80] + '...')
    resp = requests.get(url, timeout=30)
    print('  Status:', resp.status_code)
    ct = resp.headers.get('Content-Type', '')
    print('  CT:', ct)
    print('  First 200:', resp.text[:200])
    print()