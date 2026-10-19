import requests
import csv
import os
from pathlib import Path

# Test download with small limit
url = 'https://data.cms.gov/data-api/v1/dataset/0e9f2f2b-7bf9-451a-912c-e02e654dd725/data'
params = {'size': 100, 'offset': 0}
resp = requests.get(url, params=params, timeout=60)
ct = resp.headers.get('Content-Type')
print('Status:', resp.status_code)
print('CT:', ct)

data = resp.json()
print('Rows:', len(data))
print('First row keys:', list(data[0].keys()) if data else 'none')

# Write test CSV
dest = Path('raw/cms/test_service_2023.csv')
dest.parent.mkdir(parents=True, exist_ok=True)
with open(dest, 'w', newline='', encoding='utf-8') as f:
    if data:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
print('Written to', dest)