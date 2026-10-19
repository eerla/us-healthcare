"""
CMS Doctors & Clinicians, Facility Affiliation, Hospital General download script.

Downloads three CMS datasets and records source metadata in the ingestion manifest.
"""

import csv
import hashlib
import os
import sys
from pathlib import Path
from datetime import datetime
import requests
import zipfile

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

RAW_DIR = PROJECT_ROOT / "raw" / "cms"
MANIFEST_PATH = PROJECT_ROOT / "manifests" / "source_manifest.csv"

# CMS dataset URLs (from CMS data.gov)
# Note: These are the dataset landing pages; actual download URLs may vary
CMS_DATASETS = {
    "cms_clinicians": {
        "name": "CMS Doctors & Clinicians National Downloadable File",
        "url": "https://data.cms.gov/provider-data/dataset/mj5m-pzi6",
        "download_url": "https://data.cms.gov/provider-data/api/1/datastore/query/mj5m-pzi6/0/download?format=csv",
        "description": "Medicare-enrolled clinician/group/address records",
        "priority": "P0",
        "filename": "Doctors_and_Clinicians_National_Downloadable_File.csv",
    },
    "cms_affiliation": {
        "name": "CMS Facility Affiliation Data",
        "url": "https://data.cms.gov/provider-data/dataset/27ea-46a8",
        "download_url": "https://data.cms.gov/provider-data/api/1/datastore/query/27ea-46a8/0/download?format=csv",
        "description": "Clinician-to-facility relationships",
        "priority": "P0",
        "filename": "Facility_Affiliation_Data.csv",
    },
    "cms_hospital": {
        "name": "CMS Hospital General Information",
        "url": "https://data.cms.gov/provider-data/dataset/xubh-q36u",
        "download_url": "https://data.cms.gov/provider-data/api/1/datastore/query/xubh-q36u/0/download?format=csv",
        "description": "Hospital universe with CCN, type, address, ratings",
        "priority": "P0",
        "filename": "Hospital_General_Information.csv",
    },
}


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


def download_cms_api(api_endpoint: str, dest: Path, limit: int = 1000000) -> bool:
    """Download CSV from CMS API endpoint with pagination."""
    print(f"  Downloading from CMS API...")
    print(f"  URL: {api_endpoint[:100]}...")

    all_rows = []
    offset = 0
    batch_size = 1000  # CMS API limit is 1500

    while offset < limit:
        params = {
            "offset": offset,
            "limit": batch_size,
        }
        try:
            resp = requests.get(api_endpoint, params=params, timeout=300)
            if resp.status_code != 200:
                print(f"  HTTP {resp.status_code}: {resp.text[:300]}")
                return False

            data = resp.json()
            if "results" in data:
                rows = data["results"]
            else:
                rows = data

            if not rows:
                break

            all_rows.extend(rows)
            offset += batch_size
            print(f"  Fetched {len(rows)} rows (total: {len(all_rows)})")

            if len(rows) < batch_size:
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

    print(f"  Saved {len(all_rows):,} rows to {dest.name} ({dest.stat().st_size:,} bytes)")
    return True


def download_file(url: str, dest: Path) -> bool:
    """Download a file with progress reporting."""
    print(f"  Downloading {url} -> {dest}")
    try:
        response = requests.get(url, stream=True, timeout=300)
        response.raise_for_status()
        total_size = int(response.headers.get("content-length", 0))
        downloaded = 0
        with open(dest, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    pct = downloaded / total_size * 100
                    print(f"\r  Progress: {pct:.1f}%", end="", flush=True)
        print(f"\n  Downloaded {downloaded:,} bytes")
        return True
    except Exception as e:
        print(f"\n  ERROR downloading {url}: {e}")
        return False


def extract_zip(zip_path: Path, dest_dir: Path) -> list:
    """Extract a ZIP file and return list of extracted files."""
    print(f"  Extracting {zip_path.name}...")
    extracted = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.namelist():
            print(f"    - {member}")
            zf.extract(member, dest_dir)
            extracted.append(dest_dir / member)
    return extracted


def main():
    """Main download entry point."""
    print("=" * 60)
    print("CMS Data Download")
    print("=" * 60)

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    success = True

    for dataset_id, info in CMS_DATASETS.items():
        print(f"\n[1/3] Processing {info['name']}...")

        dest = RAW_DIR / info["filename"]

        if dest.exists():
            print(f"  File already exists: {dest}")
        else:
            # Use direct download URL for full CSV export
            download_url = info.get("download_url")
            if download_url:
                if not download_file(download_url, dest):
                    print(f"  WARNING: Download failed for {dataset_id}")
                    success = False
                    continue
            else:
                print(f"  ERROR: No download URL for {dataset_id}")
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
        print("\nCMS download complete.")
    else:
        print("\nCMS download completed with errors.")
        sys.exit(1)


if __name__ == "__main__":
    main()