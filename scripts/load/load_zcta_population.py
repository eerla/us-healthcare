"""
Download ZCTA population from Census ACS API and add to fact_population.
"""
import duckdb
import requests
import pandas as pd
from pathlib import Path
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent
DB_PATH = PROJECT_ROOT / "db" / "warehouse.duckdb"

CENSUS_API_BASE = "https://api.census.gov/data"
ACS_YEAR = 2023
ACS_SURVEY = "acs5"

# Variables: B01003_001E = Total Population
ACS_VARIABLES = ["B01003_001E"]

CENSUS_API_KEY = os.environ.get("CENSUS_API_KEY", "")

def download_zcta_population():
    """Download ZCTA population from Census API."""
    print("Downloading ZCTA population from Census API...")
    
    # ZCTA geography - correct endpoint format
    variables = ["NAME"] + ACS_VARIABLES
    var_str = ",".join(variables)
    url = f"https://api.census.gov/data/{ACS_YEAR}/acs/acs5?get={var_str}&for=zip+code+tabulation+area:*"
    if CENSUS_API_KEY:
        url += f"&key={CENSUS_API_KEY}"
    
    print(f"URL: {url[:120]}...")
    
    resp = requests.get(url, timeout=120)
    if resp.status_code != 200:
        print(f"ERROR: HTTP {resp.status_code}: {resp.text[:300]}")
        return None
    
    # Check if response is JSON
    content_type = resp.headers.get('Content-Type', '')
    if 'json' not in resp.headers.get('Content-Type', '').lower():
        print(f"ERROR: Response is not JSON. Content-Type: {resp.headers.get('Content-Type')}")
        print(f"First 500 chars: {resp.text[:500]}")
        return None
    
    data = resp.json()
    if not data or len(data) < 2:
        print("ERROR: No data returned")
        return None
    
    # Parse CSV
    headers = data[0]
    rows = data[1:]
    
    df = pd.DataFrame(rows, columns=headers)
    print(f"Downloaded {len(df)} ZCTA records")
    print(f"Columns: {df.columns.tolist()}")
    print(f"Sample: {df.head()}")
    
    return df

def load_to_fact_population(df):
    """Load ZCTA data into fact_population table."""
    if df is None or len(df) == 0:
        return 0
    
    # The API returns: NAME, B01003_001E, zip code tabulation area
    # We need: geo_type, geo_id, year, population
    df_clean = df.copy()
    df_clean['geo_type'] = 'zcta'
    df_clean['geo_id'] = df_clean['zip code tabulation area'].astype(str).str.zfill(5)
    df_clean['year'] = 2023
    df_clean['population'] = pd.to_numeric(df_clean['B01003_001E'], errors='coerce')
    
    # Keep only valid records
    df_clean = df_clean[['geo_type', 'geo_id', 'year', 'population']].dropna()
    df_clean = df_clean[df_clean['population'] > 0]
    
    print(f"Valid records: {len(df_clean)}")
    print(f"Sample: {df_clean.head()}")
    
    # Insert into fact_population
    conn = duckdb.connect('db/warehouse.duckdb')
    
    # Delete existing ZCTA records for 2023 to avoid duplicates
    conn.execute("DELETE FROM core.fact_population WHERE geo_type = 'zcta' AND year = 2023")
    
    # Insert new records
    conn.execute("INSERT INTO core.fact_population SELECT * FROM df_clean")
    
    # Verify
    cnt = conn.execute("SELECT COUNT(*) FROM core.fact_population WHERE geo_type = 'zcta' AND year = 2023").fetchone()[0]
    print(f"Inserted {cnt} ZCTA records")
    
    conn.close()
    return cnt

def main():
    print("=" * 60)
    print("Downloading ZCTA Population to fact_population")
    print("=" * 60)
    
    df = download_zcta_population()
    if df is not None:
        load_to_fact_population(df)
        print("\nDone!")
    else:
        print("Failed to download data")

if __name__ == "__main__":
    import duckdb
    import requests
    import pandas as pd
    from pathlib import Path
    from dotenv import load_dotenv
    import os
    
    PROJECT_ROOT = Path(__file__).resolve().parent
    DB_PATH = PROJECT_ROOT / "db" / "warehouse.duckdb"
    
    main()