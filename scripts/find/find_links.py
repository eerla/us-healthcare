import requests
import re

url = 'https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners'
resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)

# Look for links to datasets
links = re.findall(r'href="([^"]+)"', resp.text)
for link in links:
    if any(term in link.lower() for term in ['medicare', 'physician', 'utilization', 'provider']):
        print(link)