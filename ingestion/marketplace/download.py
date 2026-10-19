"""
CMS Marketplace PUFs download script.

Downloads CMS Marketplace PUFs for plan year 2026.
Direct download from https://download.cms.gov/marketplace-puf/
"""
import csv
import hashlib
import os
import sys
from pathlib import Path
from datetime import datetime
import requests

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

RAW_DIR = PROJECT_ROOT / "raw" / "marketplace"
MANIFEST_PATH = PROJECT_ROOT / "manifests" / "source_manifest.csv"

# 2026 Marketplace PUF URLs
MARKETPLACE_DATASETS = {
    "marketplace_plan": {
        "name": "Plan Attributes PUF",
        "url": "https://download.cms.gov/marketplace-puf/2026/plan-attributes-puf.zip",
        "description": "Plan-level data on attributes, metal level, network, service area, formulary",
        "priority": "P0",
        "filename": "plan-attributes-puf.zip",
    },
    "marketplace_service_area": {
        "name": "Service Area PUF",
        "url": "https://download.cms.gov/marketplace-puf/2026/service-area-puf.zip",
        "description": "Issuer-level service area data by state, county, zip code",
        "priority": "P0",
        "filename": "service-area-puf.zip",
    },
    "marketplace_network": {
        "name": "Network PUF",
        "url": "https://download.cms.gov/marketplace-puf/2026/network-puf.zip",
        "description": "Issuer-level network names, IDs, URLs",
        "priority": "P0",
        "filename": "network-puf.zip",
    },
    "marketplace_machine_readable_url": {
        "name": "Machine-readable URL PUF",
        "url": "https://download.cms.gov/marketplace-puf/2026/machine-readable-url-puf.zip",
        "description": "Issuer-level URLs for machine-readable provider directories and formularies",
        "priority": "P1",
        "filename": "machine-readable-url-puf.zip",
    },
    "marketplace_business_rules": {
        "name": "Business Rules PUF",
        "url": "https://download.cms.gov/marketplace-puf/2026/business-rules-puf.zip",
        "description": "Plan-level business rules (dependent age, tobacco rules, market coverage)",
        "priority": "P1",
        "filename": "business-rules-puf.zip",
    },
    "marketplace_rate": {
        "name": "Rate PUF",
        "url": "https://download.cms.gov/marketplace-puf/2026/rate-puf.zip",
        "description": "Plan-level rates by age, tobacco, rating area, family tier",
        "priority": "P0",
        "filename": "rate-puf.zip",
    },
    "marketplace_benefits_cost_sharing": {
        "name": "Benefits & Cost Sharing PUF",
        "url": "https://download.cms.gov/marketplace-puf/2026/benefits-and-cost-sharing-puf.zip",
        "description": "Plan-level benefits, copays, coinsurance, EHB indicators",
        "priority": "P0",
        "filename": "benefits-and-cost-sharing-puf.zip",
    },
    "marketplace_plan_id_crosswalk": {
        "name": "Plan ID Crosswalk PUF",
        "url": "https://download.cms.gov/marketplace-puf/2026/plan-id-crosswalk-puf.zip",
        "description": "Plan ID crosswalk between plan years",
        "priority": "P1",
        "filename": "plan-id-crosswalk-puf.zip",
    },
    "marketplace_transparency_coverage": {
        "name": "Transparency in Coverage PUF",
        "url": "https://download.cms.gov/marketplace-puf/2026/transparency-in-coverage-puf.zip",
        "description": "Transparency in Coverage disclaimer data",
        "priority": "P2",
        "filename": "transparency-in-coverage-puf.zip",
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


def download_file(url: str, dest: Path) -> bool:
    """Download a file with progress reporting."""
    print(f"  Downloading {dest.name}...")
    try:
        resp = requests.get(url, stream=True, timeout=300)
        resp.raise_for_status()
        total_size = int(resp.headers.get("content-length", 0))
        downloaded = 0
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
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


def main():
    """Main download entry point."""
    print("=" * 60)
    print("CMS Marketplace PUFs Download (PY2026)")
    print("=" * 60)

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    success = True
    for dataset_id, info in MARKETPLACE_DATASETS.items():
        print(f"\nProcessing {info['name']}...")

        dest = RAW_DIR / info["filename"]

        if dest.exists():
            print(f"  File already exists: {dest}")
        else:
            if not download_file(info["url"], dest):
                print(f"  WARNING: Download failed for {dataset_id}")
                success = False
                continue

        # Compute checksum
        checksum = compute_md5(dest)

        # Count rows
        with zipfile.ZipFile(dest) as z:
            for name in z.namelist():
                if name.endswith('.csv'):
                    with z.open(name) as f:
                        row_count = sum(1 for _ in f) - 1  # minus header
                elif name.endswith('.xlsx'):
                    import pandas as pd
                    with zipfile.ZipFile(dest) as z:
                        df = pd.read_excel(z.open(name))
                        row_count = len(df)
                    break

        # Record manifest
        record_manifest(
            source=dataset_id,
            url=info["url"],
            version="2026",
            checksum=checksum,
            rows_loaded=row_count,
            rows_rejected=0,
            notes=f"{info['description']}, {row_count:,} rows"
        )

    if success:
        print("\nMarketplace download complete.")
    else:
        print("\nMarketplace download completed with errors.")
        sys.exit(1)


if __name__ == "__main__":
    import hashlib
    import zipfile
    import pandas as pd
    main()