import requests
import re

url = 'https://www.cms.gov/Research-Statistics-Data-and-Systems/Statistics-Trends-and-Reports/Medicare-Provider-Charge-Data/Physician-and-Other-Supplier'
resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)

text = resp.text

patterns = [
    r'dataset[_-]?id[\s]*[:=][\s]*([a-z0-9\-]{4,})',
    r'\"id\"[\s]*:[\s]*\"([a-z0-9\-]{4,})',
    r'data-id=[\"\s]*([a-z0-9\-]{4,})',
    r'data-dataset-id=[\"\s]*([a-z0-9\-]{4,})',
]

for pattern in patterns:
    matches = re.findall(pattern, resp.text, re.IGNORECASE)
    if matches:
        print(f'Pattern: {pattern}')
        for m in set(matches):
            if len(m) > 4:
                print(f'  {m}')