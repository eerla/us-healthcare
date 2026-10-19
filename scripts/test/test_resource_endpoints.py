import requests

# Test different resource endpoints
patterns = [
    'marketplace-plan',
    'marketplace-service-area', 
    'marketplace-network',
    'marketplace-mr-url',
    'exchange-plan',
    'exchange-service-area',
    'exchange-network',
    'marketplace-plan-puf',
    'marketplace-service-area-puf',
    'marketplace-network-puf',
    'marketplace-mr-url-puf',
]

for pattern in patterns:
    url = f'https://data.cms.gov/resource/{pattern}.json'
    try:
        resp = requests.get(url, timeout=15)
        ct = resp.headers.get('Content-Type', '')
        print(f'{pattern}: {resp.status_code} | {ct[:40]}')
    except Exception as e:
        print(f'{pattern}: ERROR - {e}')