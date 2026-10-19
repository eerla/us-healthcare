import requests
import json

url = 'https://data.cms.gov/data.json'
resp = requests.get(url, headers={'Accept': 'application/json'}, timeout=60)
data = resp.json()

# Search for Medicare Physician & Other Practitioners datasets
if 'dataset' in data:
    print('Number of datasets:', len(data['dataset']))
    for ds in data['dataset']:
        title = ds.get('title', '')
        if 'medicare physician other practitioners' in title.lower() or 'medicare physician other practitioners' in title.lower():
            identifier = ds.get('identifier', '')
            uuid = identifier.split('/')[-2] if 'dataset/' in identifier else identifier
            print(f"UUID: {uuid}")
            print(f"Title: {ds.get('title', '')}")
            print(f"Identifier: {identifier}")
            print()