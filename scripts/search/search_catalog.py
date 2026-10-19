import requests
import json

url = 'https://data.cms.gov/data.json'
resp = requests.get(url, headers={'Accept': 'application/json'}, timeout=60)
print('Status:', resp.status_code)
data = resp.json()
print('Keys:', data.keys())
if 'dataset' in data:
    print('Number of datasets:', len(data['dataset']))
    for ds in data['dataset']:
        title = ds.get('title', '')
        if any(term in title.lower() for term in ['medicare', 'physician', 'utilization', 'provider']):
            print(f"  UUID: {ds.get('identifier')}")
            print(f"  Title: {title}")
            print()