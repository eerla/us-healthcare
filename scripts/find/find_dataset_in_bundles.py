import requests
import re

# Fetch the marketplace page and look for dataset IDs in JS bundles
url = 'https://data.cms.gov/provider-data/dataset/marketplace-plan'
resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)

# Find JS bundles
js_bundles = re.findall(r'src="([^"]*\.js)"', resp.text)
for bundle in js_bundles:
    if 'chunk' in bundle or 'bundle' in bundle or 'main' in bundle:
        print(f'JS Bundle: {bundle}')
        bundle_url = 'https://data.cms.gov' + bundle if bundle.startswith('/') else bundle
        try:
            bundle_resp = requests.get(bundle_url, timeout=15)
            dataset_ids = re.findall(r'[a-z0-9]{4}-[a-z0-9]{4}', bundle_resp.text)
            for ds in set(dataset_ids):
                if ds not in ['ogle-site', 'prop-type', 'eact-stat', 'tial-scal', 'icon-16x1', 'down-runt', 'lazy-load', 'heme-colo', 'icon-32x3', 'vice-widt', 'ider-data', 'lium-tags']:
                    print(f'Found dataset ID in {bundle}: {ds}')
        except:
            pass