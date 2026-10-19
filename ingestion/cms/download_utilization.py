"""
Medicare Utilization download script.

Downloads CMS Medicare Physician & Other Practitioners utilization data
using the new CMS API (data-api/v1/dataset/{uuid}/data).
"""

import csv
import hashlib
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import requests

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

RAW_DIR = PROJECT_ROOT / "raw" / "cms"
MANIFEST_PATH = PROJECT_ROOT / "manifests" / "source_manifest.csv"

# Medicare Utilization datasets with UUIDs from CMS catalog
UTILIZATION_DATASETS = {
    "cms_utilization_provider_2023": {
        "name": "Medicare Physician & Other Practitioners by Provider (2023)",
        "url": "https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners/medicare-physician-other-practitioners-by-provider",
        "uuid": "8ba584c6-a43a-4b0b-a35a-eb9a59e3a571",
        "description": "Medicare utilization by provider (NPI-level, 2023)",
        "priority": "P0",
        "filename": "Medicare_Physician_Other_Practitioners_by_Provider_2023.csv",
    },
    "cms_utilization_service_2023": {
        "name": "Medicare Physician & Other Practitioners by Provider and Service (2023)",
        "url": "https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners/medicare-physician-other-practitioners-by-provider-and-service",
        "uuid": "0e9f2f2b-7bf9-451a-912c-e02e654dd725",
        "description": "Medicare utilization by provider and service (HCPCS-level, 2023)",
        "priority": "P0",
        "filename": "Medicare_Physician_Other_Practitioners_by_Provider_and_Service_2023.csv",
    },
    "cms_utilization_provider_2024": {
        "name": "Medicare Physician & Other Practitioners by Provider (2024)",
        "url": "https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners/medicare-physician-other-practitioners-by-provider",
        "uuid": "8889d81e-2ee7-448f-8713-f071038289b5",
        "description": "Medicare utilization by provider (NPI-level, 2024)",
        "priority": "P0",
        "filename": "Medicare_Physician_Other_Practitioners_by_Provider_2024.csv",
    },
    "cms_utilization_service_2024": {
        "name": "Medicare Physician & Other Practitioners by Provider and Service (2024)",
        "url": "https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners/medicare-physician-other-practitioners-by-provider-and-service",
        "uuid": "92396110-2aed-4d63-a6a2-5d6207d46a29",
        "description": "Medicare utilization by provider and service (HCPCS-level, 2024)",
        "priority": "P0",
        "filename": "Medicare_Physician_Other_Practitioners_by_Provider_and_Service_2024.csv",
    },
}

API_BASE = "https://data.cms.gov/data-api/v1/dataset"
PAGE_SIZE = 5000  # CMS API max page size


def compute_md5(file_path: Path) -> str:
    """Compute MD5 checksum of a file."""
    md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            md5.update(chunk)
    return md5.hexdigest()


def record_manifest(source: str, url: str, version: str, checksum: str,
                    rows_loaded: int, rows_rejected: int, notes: str = ""):
    """Append a row to the source manifest."""
    timestamp = datetime.utcnow().isoformat() + "Z"
    row = f"{source},{url},{timestamp},{version},{checksum},{rows_loaded},{rows_rejected},1.0,{notes}\n"
    with open(MANIFEST_PATH, "a") as f:
        f.write(row)
    print(f"  Manifest recorded: {source}")


def download_json_to_csv(api_url: str, dest: Path, limit: int = None) -> bool:
    """Download JSON array from CMS API with pagination and convert to CSV."""
    print(f"  Downloading from CMS API...")
    print(f"  URL: {api_url}")

    all_rows = []
    offset = 0
    total_rows = 0

    while True:
        params = {
            "size": PAGE_SIZE,
            "offset": offset,
        }
        try:
            resp = requests.get(api_url, params=params, timeout=300)
            if resp.status_code != 200:
                print(f"  HTTP {resp.status_code}: {resp.text[:300]}")
                return False

            data = resp.json()
            if not data:
                break

            all_rows.extend(data)
            total_rows += len(data)
            offset += PAGE_SIZE

            print(f"  Fetched {len(data)} rows (total: {total_rows:,})")

            if limit and total_rows >= limit:
                all_rows = all_rows[:limit]
                break

            if len(data) < PAGE_SIZE:
                break

        except Exception as e:
            print(f"  ERROR: {e}")
            return False

    if not all_rows:
        print("  ERROR: No data downloaded")
        return False

    # Write CSV
    with open(dest, "w", newline="", encoding="utf-8") as f:
        if all_rows:
            writer = csv.DictWriter(f, fieldnames=all_rows[0].keys())
            writer.writeheader()
            writer.writerows(all_rows)

    print(f"  Saved {total_rows:,} rows to {dest.name} ({dest.stat().st_size:,} bytes)")
    return True


def main():
    """Main download entry point."""
    print("=" * 60)
    print("Medicare Utilization Download (New CMS API)")
    print("=" * 60)

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    success = True

    for dataset_id, info in UTILIZATION_DATASETS.items():
        print(f"\n[1/4] Processing {info['name']}...")

        dest = RAW_DIR / info["filename"]

        if dest.exists():
            print(f"  File already exists: {dest}")
        else:
            api_url = f"{API_BASE}/{info['uuid']}/data"
            if not download_json_to_csv(api_url, dest):
                print(f"  WARNING: Download failed for {dataset_id}")
                success = False
                continue

        # Compute checksum
        checksum = compute_md5(dest)

        # Count rows
        with open(dest, "r", encoding="utf-8") as f:
            row_count = sum(1 for _ in f) - 1  # minus header

        # Record manifest
        record_manifest(
            source=dataset_id,
            url=info["url"],
            version="2024",
            checksum=checksum,
            rows_loaded=row_count,
            rows_rejected=0,
            notes=f"{info['description']}, {row_count:,} rows"
        )

    if success:
        print("\nMedicare Utilization download complete.")
    else:
        print("\nMedicare Utilization download completed with errors.")
        sys.exit(1)


if __name__ == "__main__":
    main()