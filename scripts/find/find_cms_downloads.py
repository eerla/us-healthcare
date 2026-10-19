import requests
import re

# Try the CMS marketplace page
url = 'https://www.cms.gov/Research-Statistics-Data-and-Systems/Statistics-Trends-and-Reports/Marketplace-Plan-Selection'
resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
print('Status:', resp.status_code)

# Look for download links
links = re.findall(r'href="([^"]*\.csv)"', resp.text)
for link in links:
    print(f'CSV link: {link}')

links = re.findall(r'href="([^"]*\.zip)"', resp.text)
for link in links:
    print(f'ZIP link: {link}')