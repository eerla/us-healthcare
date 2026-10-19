import requests
import re

# Try to find API endpoints in the marketplace page
url = 'https://data.cms.gov/provider-data/dataset/marketplace-plan'
resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)

# Look for API endpoints in the JavaScript bundles
api_endpoints = re.findall(r'https?://[^/]+/api/[^\s"\'<>]+', resp.text)
for endpoint in set(api_endpoints):
    print(f'API endpoint: {endpoint}')

# Look for GraphQL or REST API calls
graphql = re.findall(r'https?://[^/]+/graphql', resp.text)
for g in set(graphql):
    print(f'GraphQL: {g}')

rest = re.findall(r'https?://[^/]+/api/v\d+/[^\s"\'<>]+', resp.text)
for r in set(rest):
    print(f'REST API: {r}')