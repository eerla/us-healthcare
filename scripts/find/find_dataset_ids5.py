import requests
import re

# Try to find dataset IDs from marketplace pages
url = 'https://data.cms.gov/provider-data/dataset/marketplace-plan'
resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)

# Look for dataset IDs in various JS patterns
patterns = [
    r'"dataset[_-]?id"?\s*[:=]\s*"([a-z0-9\-]{4,})"',
    r'"resource[_-]?id"?\s*[:=]\s*"([a-z0-9\-]{4,})"',
    r'data-dataset-id=["\s]*([a-z0-9\-]{4,})',
    r'data-id=["\s]*([a-z0-9\-]{4,})',
]

for pattern in patterns:
    matches = re.findall(pattern, resp.text, re.IGNORECASE)
    if matches:
        print(f'Pattern: {pattern}')
        for m in set(matches):
            if m not in ['ogle-site', 'prop-type', 'eact-stat', 'tial-scal', 'icon-16x1', 'down-runt', 'lazy-load', 'heme-colo', 'icon-32x3', 'vice-widt']:
                print(f'  Found: {m}')