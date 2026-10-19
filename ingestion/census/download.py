"""
Census ACS 5-Year download and ingest script.

Downloads Census ACS 5-year population estimates by ZCTA and county.
Uses the Census API with a key from .env or environment.
"""

import csv
import hashlib
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Manual .env parsing (no dependency on python-dotenv)
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ[key.strip()] = value.strip()

import requests

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

RAW_DIR = PROJECT_ROOT / "raw" / "census"
MANIFEST_PATH = PROJECT_ROOT / "manifests" / "source_manifest.csv"

CENSUS_API_BASE = "https://api.census.gov/data"

CENSUS_API_KEY = os.environ.get("CENSUS_API_KEY", "")

ACS_YEAR = 2023
ACS_SURVEY = "acs5"

ACS_VARIABLES = [
    "B01003_001E",  # Total population
    "B19013_001E",  # Median household income
    "B17001_001E",  # Total population for poverty determination
    "B17001_002E",  # Income below poverty level
]


def build_url(variables: list, geography: str, year: int = ACS_YEAR) -> str:
    """Build a Census API URL with key."""
    var_str = ",".join(["NAME"] + variables)
    key_param = f"&key={CENSUS_API_KEY}" if CENSUS_API_KEY else ""
    return f"{CENSUS_API_BASE}/{year}/acs/{ACS_SURVEY}?get={var_str}&for={geography}{key_param}"


def download_json_to_csv(url: str, dest: Path) -> bool:
    """Download JSON array from Census API and convert to CSV."""
    print(f"  URL: {url[:120]}...")
    try:
        resp = requests.get(url, timeout=120)
        if resp.status_code != 200:
            print(f"  HTTP {resp.status_code}: {resp.text[:300]}")
            return False

        # Census API returns JSON array: [["NAME","B01003_001E",...], ["Autauga County...", "59285", ...]]
        data = resp.json()
        if not isinstance(data, list) or len(data) < 2:
            print(f"  ERROR: Unexpected response format. First 300 chars: {resp.text[:300]}")
            return False

        # First row is header, rest are data
        headers = data[0]
        rows = data[1:]

        with open(dest, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)

        print(f"  Downloaded {dest.name} ({dest.stat().st_size:,} bytes, {len(rows):,} rows)")
        return True
    except json.JSONDecodeError:
        print(f"  ERROR: Response is not valid JSON. First 300 chars: {resp.text[:300]}")
        return False
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


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


def download_zcta_population():
    """Download ACS population estimates by ZCTA."""
    print("\n[1/2] Downloading ZCTA-level population estimates...")
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    url = build_url(ACS_VARIABLES, "zip+code+tabulation+area:*")
    dest = RAW_DIR / f"acs_{ACS_YEAR}_zcta_population.csv"

    if download_json_to_csv(url, dest):
        with open(dest, "r", encoding="utf-8") as f:
            row_count = sum(1 for _ in f) - 1
        checksum = compute_md5(dest)
        record_manifest(
            source="census_acs_zcta_population",
            url=url,
            version=f"{ACS_YEAR}-{ACS_SURVEY}",
            checksum=checksum,
            rows_loaded=row_count,
            rows_rejected=0,
            notes=f"ACS {ACS_YEAR} 5-year population by ZCTA"
        )
        return True
    return False


def download_county_population():
    """Download ACS population estimates by county."""
    print("\n[2/2] Downloading county-level population estimates...")

    url = build_url(ACS_VARIABLES, "county:*")
    dest = RAW_DIR / f"acs_{ACS_YEAR}_county_population.csv"

    if download_json_to_csv(url, dest):
        with open(dest, "r", encoding="utf-8") as f:
            row_count = sum(1 for _ in f) - 1
        checksum = compute_md5(dest)
        record_manifest(
            source="census_acs_county_population",
            url=url,
            version=f"{ACS_YEAR}-{ACS_SURVEY}",
            checksum=checksum,
            rows_loaded=row_count,
            rows_rejected=0,
            notes=f"ACS {ACS_YEAR} 5-year population by county"
        )
        return True
    return False


def main():
    """Main download entry point."""
    print("=" * 60)
    print("Census ACS Download")
    print("=" * 60)

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    if not CENSUS_API_KEY:
        print("FATAL: No CENSUS_API_KEY found. Set it in .env or environment.")
        sys.exit(1)

    print(f"  Using Census API key: {CENSUS_API_KEY[:8]}...")

    success = True
    success &= download_zcta_population()
    success &= download_county_population()

    if success:
        print("\nCensus download complete.")
    else:
        print("\nCensus download completed with errors.")
        sys.exit(1)


if __name__ == "__main__":
    main()