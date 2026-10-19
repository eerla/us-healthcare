import requests
import re

url = 'https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners/medicare-physician-other-practitioners-by-provider'
resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)

patterns = [
    r'"dataset[_-]?id"?\s*[:=]\s*"([a-z0-9\-]{4,})',
    r'"resource[_-]?id"?\s*[:=]\s*"([a-z0-9\-]{4,})',
    r'data-dataset-id=["\s]*([a-z0-9\-]{4,})',
    r'data-id=["\s]*([a-z0-9\-]{4,})',
    r'"id"?\s*[:=]\s*"([a-z0-9\-]{4,})',
]

text = resp.text
for pattern in patterns:
    matches = re.findall(pattern, text, re.IGNORECASE)
    if matches:
        print(f'Pattern: {pattern}')
        for m in set(matches):
            if len(m) > 4 and m not in ['ogle-site', 'heme-colo', 'icon-32x3']:
                print(f'  {m}')