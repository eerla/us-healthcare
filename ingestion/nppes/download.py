"""
NPPES download and ingest script.

Downloads the monthly NPPES V2 file and reference files from CMS.
Records source metadata in the ingestion manifest.
"""

import hashlib
import os
import sys
import zipfile
import yaml
from datetime import datetime
from pathlib import Path
import requests

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

RAW_DIR = PROJECT_ROOT / "raw" / "nppes"
MANIFEST_PATH = PROJECT_ROOT / "manifests" / "source_manifest.csv"

NPPES_BASE_URL = "https://download.cms.gov/nppes"

# Current known file (from CMS page as of October 2026)
MONTHLY_FILE = "NPPES_Data_Dissemination_September_2026_V2.zip"
DEACTIVATION_FILE = "NPPES_Deactivated_NPI_Report_091426_V2.zip"


def compute_md5(file_path: Path) -> str:
    """Compute MD5 checksum of a file."""
    md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            md5.update(chunk)
    return md5.hexdigest()


def download_file(url: str, dest: Path, timeout: int = 300) -> bool:
    """Download a file with progress reporting."""
    print(f"Downloading {url} -> {dest}")
    try:
        response = requests.get(url, stream=True, timeout=timeout)
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
    print(f"Extracting {zip_path.name}...")
    extracted = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.namelist():
            print(f"  - {member}")
            zf.extract(member, dest_dir)
            extracted.append(dest_dir / member)
    return extracted


def record_manifest(source: str, url: str, version: str, checksum: str,
                    rows_loaded: int, rows_rejected: int, notes: str = ""):
    """Append a row to the source manifest."""
    timestamp = datetime.utcnow().isoformat() + "Z"
    row = f"{source},{url},{timestamp},{version},{checksum},{rows_loaded},{rows_rejected},1.0,{notes}\n"
    with open(MANIFEST_PATH, "a") as f:
        f.write(row)
    print(f"  Manifest recorded: {source}")


def main():
    """Main download and ingest entry point."""
    print("=" * 60)
    print("NPPES Download & Ingest")
    print("=" * 60)

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Download monthly V2 file
    monthly_url = f"{NPPES_BASE_URL}/{MONTHLY_FILE}"
    monthly_dest = RAW_DIR / MONTHLY_FILE

    if not monthly_dest.exists():
        print(f"\n[1/3] Downloading monthly V2 file ({MONTHLY_FILE})...")
        if not download_file(monthly_url, monthly_dest):
            print("FATAL: Could not download monthly file")
            sys.exit(1)
    else:
        print(f"\n[1/3] Monthly file already exists: {monthly_dest}")

    # 2. Compute checksum and extract
    print(f"\n[2/3] Computing checksum and extracting...")
    checksum = compute_md5(monthly_dest)
    print(f"  MD5: {checksum}")

    extracted = extract_zip(monthly_dest, RAW_DIR)

    # 3. Record manifest
    print(f"\n[3/3] Recording manifest...")
    # Row count will be determined during ingestion
    record_manifest(
        source="nppes_monthly_v2",
        url=monthly_url,
        version="2026-09",
        checksum=checksum,
        rows_loaded=0,  # Will be updated after ingestion
        rows_rejected=0,
        notes=f"Monthly V2 file, extracted {len(extracted)} files"
    )

    print("\nNPPES download complete.")
    print(f"Files extracted to: {RAW_DIR}")


if __name__ == "__main__":
    main()