import requests

# Test all four key utilization datasets
datasets = [
    ('0e9f2f2b-7bf9-451a-912c-e02e654dd725', 'By Provider & Service 2023'),
    ('8ba584c6-a43a-4b0b-a35a-eb9a59e3a571', 'By Provider 2023'),
    ('92396110-2aed-4d63-a6a2-5d6207d46a29', 'By Provider & Service 2024'),
    ('8889d81e-2ee7-448f-8713-f071038289b5', 'By Provider 2024'),
]

for uuid, name in datasets:
    url = f'https://data.cms.gov/data-api/v1/dataset/{uuid}/data?size=5'
    resp = requests.get(url, timeout=30)
    print(f'{name} ({uuid}): {resp.status_code}')
    print(f'  CT: {resp.headers.get("Content-Type")}')
    print(f'  Size: {len(resp.content)}')
    if resp.status_code == 200:
        print(f'  First 200 chars: {resp.text[:200]}')
    print()