import requests
import re

# Try to find dataset IDs from marketplace pages
urls = [
    'https://data.cms.gov/provider-data/dataset/marketplace-plan',
    'https://data.cms.gov/provider-data/dataset/marketplace-service-area',
    'https://data.cms.gov/provider-data/dataset/marketplace-network',
    'https://data.cms.gov/provider-data/dataset/marketplace-mr-url',
]

for url in urls:
    resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
    
    # Look for dataset IDs in various formats
    patterns = [
        r'"dataset[_-]?id"\s*[:=]\s*"([a-z0-9\-]{4,})"',
        r'data-dataset-id=["\s]*([a-z0-9\-]{4,})',
        r'dataset[_-]?id["\s]*[:=]["\s]*([a-z0-9\-]{4,})',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, resp.text, re.IGNORECASE)
        if matches:
            print(f'{url}: Found IDs with pattern {pattern}: {matches}')