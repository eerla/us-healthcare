import requests
import json

url = 'https://data.cms.gov/data.json'
resp = requests.get(url, headers={'Accept': 'application/json'}, timeout=60)
data = resp.json()

# Search for physician datasets with broader terms
if 'dataset' in data:
    print('Number of datasets:', len(data['dataset']))
    for ds in data['dataset']:
        title = ds.get('title', '').lower()
        if any(term in title for term in ['physician', 'practitioner', 'provider and service', 'by provider', 'by provider and service']):
            identifier = ds.get('identifier', '')
            uuid = identifier.split('/')[-2] if 'dataset/' in identifier else identifier
            print(f"UUID: {uuid}")
            print(f"Title: {ds.get('title', '')}")
            print(f"Identifier: {identifier}")
            print()