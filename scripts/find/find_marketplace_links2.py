import requests
import re

# Try the CMS marketplace page on data.cms.gov
url = 'https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners/medicare-physician-other-practitioners-by-provider'
resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
print('Status:', resp.status_code)

# Look for marketplace links
links = re.findall(r'href="([^"]*)"', resp.text)
for link in links:
    if 'marketplace' in link.lower() or 'exchange' in link.lower():
        print(f'  Link: {link}')