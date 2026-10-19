import requests

# Try the Socrata export endpoint
datasets = [
    ('mj5m-pzi6', 'Doctors and Clinicians'),
    ('27ea-46a8', 'Facility Affiliation'),
    ('xubh-q36u', 'Hospital General'),
]

for dataset_id, name in datasets:
    # Try export endpoint
    url = f'https://data.cms.gov/provider-data/api/1/datastore/query/{dataset_id}/0/download?format=csv'
    resp = requests.get(url, timeout=60, allow_redirects=True)
    print(f'{name} ({dataset_id}): {resp.status_code}')
    print(f'  Content-Type: {resp.headers.get("Content-Type")}')
    print(f'  Content-Length: {resp.headers.get("Content-Length")}')
    print(f'  Final URL: {resp.url}')
    if 'csv' in resp.headers.get('Content-Type', ''):
        print(f'  First 200 chars: {resp.text[:200]}')
    print()