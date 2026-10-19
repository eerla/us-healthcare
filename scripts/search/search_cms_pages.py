import requests
import re

# Try the CMS marketplace PUFs pages
urls = [
    'https://www.cms.gov/Research-Statistics-Data-and-Systems/Statistics-Trends-and-Reports/Marketplace-Plan-Selection',
    'https://www.cms.gov/Research-Statistics-Data-and-Systems/Statistics-Trends-and-Reports/Marketplace-Enrollment',
    'https://www.cms.gov/Research-Statistics-Data-and-Systems/Statistics-Trends-and-Reports/Marketplace-Plan-Selection',
]

for url in urls:
    resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
    print(f'{url}: {resp.status_code}')
    if resp.status_code == 200:
        # Look for CSV or download links
        csv_links = re.findall(r'href="([^"]*\.csv)"', resp.text)
        for link in csv_links:
            print(f'  CSV link: {link}')
        zip_links = re.findall(r'href="([^"]*\.zip)"', resp.text)
        for link in zip_links:
            print(f'  ZIP link: {link}')