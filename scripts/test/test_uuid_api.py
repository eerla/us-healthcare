import requests

uuid = '0e9f2f2b-7bf9-451a-912c-e02e654dd725'  # By Provider & Service 2023
url = f'https://data.cms.gov/data-api/v1/dataset/{uuid}/data?size=10'
resp = requests.get(url, timeout=30)
print(f'By Provider & Service 2023: {resp.status_code}')
print(f'  CT: {resp.headers.get("Content-Type")}')
print(f'  Size: {len(resp.content)}')
if resp.status_code == 200:
    print(f'  First 200 chars: {resp.text[:200]}')