"""
Geocode CT addresses to county FIPS using Census Geocoder API batch endpoint.
"""
import duckdb
import requests
import pandas as pd
import time
import csv
from io import StringIO

PROJECT_ROOT = "C:/Users/gurub/projects/us-healthcare"
DB_PATH = PROJECT_ROOT + "/db/warehouse.duckdb"

# Census Geocoder API batch endpoint
GEOCODER_URL = "https://geocoding.geo.census.gov/geocoder/geographies/addressbatch"

def extract_ct_addresses():
    """Extract CT addresses needing geocoding from dim_location."""
    conn = duckdb.connect(DB_PATH)
    query = """
    SELECT 
        location_sk,
        address1,
        address2,
        city,
        state,
        zip5
    FROM core.dim_location
    WHERE state = 'CT' 
      AND (county_fips IS NULL OR county_fips = '')
      AND address1 IS NOT NULL
      AND address1 <> ''
    """
    df = conn.execute(query).df()
    conn.close()
    return df

def geocode_batch(df_batch):
    """Send batch to Census Geocoder API."""
    # Prepare CSV for API
    csv_data = df_batch[['location_sk', 'address1', 'city', 'state', 'zip5']].copy()
    csv_data.columns = ['id', 'street', 'city', 'state', 'zip']
    csv_buffer = StringIO()
    csv_data.to_csv(csv_buffer, index=False, header=False, quoting=csv.QUOTE_ALL)
    csv_content = csv_buffer.getvalue()
    
    # Send to Census API
    files = {
        'addressFile': ('addresses.csv', csv_content, 'text/csv'),
        'benchmark': (None, 'Public_AR_Current'),
        'vintage': (None, 'Current_Current'),
    }
    
    response = requests.post(GEOCODER_URL, files=files, timeout=120)
    return response.text

def parse_geocoder_response(response_text):
    """Parse Census Geocoder API response."""
    reader = csv.reader(StringIO(response_text))
    results = []
    for row in reader:
        # Census API returns: id, input address, match, match type, matched address, coordinates, tiger/line id, side, state, county, tract, block
        if len(row) >= 11:
            location_id = row[0]
            match = row[2]
            county_fips = row[10] if len(row) > 10 else ''
            results.append({
                'location_sk': int(location_id),
                'county_fips': county_fips,
                'match': match
            })
    return pd.DataFrame(results)

def main():
    print("=" * 60)
    print("Geocoding CT Addresses to County FIPS")
    print("=" * 60)
    
    # Extract addresses
    df = extract_ct_addresses()
    print(f"Total CT addresses to geocode: {len(df)}")
    
    if len(df) == 0:
        print("No addresses to geocode.")
        return
    
    # Process in batches of 1000 (Census API limit)
    batch_size = 1000
    total_updated = 0
    
    conn = duckdb.connect('db/warehouse.duckdb')
    
    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i+batch_size]
        print(f"\nProcessing batch {i//batch_size + 1}: rows {i+1} to {min(i+batch_size, len(df))}")
        
        try:
            # Geocode batch
            response_text = geocode_batch(batch)
            
            # Parse results
            results_df = parse_geocoder_response(response_text)
            
            # Update dim_location
            for _, row in results_df.iterrows():
                if row['county_fips'] and row['match'] == 'Match':
                    conn.execute("""
                        UPDATE core.dim_location 
                        SET county_fips = ? 
                        WHERE location_sk = ?
                    """, [row['county_fips'], row['location_sk']])
                    total_updated += 1
            
            print(f"  Updated {len(results_df)} addresses")
            
        except Exception as e:
            print(f"  Error: {e}")
        
        # Rate limiting - be nice to Census API
        time.sleep(1)
    
    conn.close()
    print(f"\nTotal updated: {total_updated}")
    
    # Verify
    conn = duckdb.connect('db/warehouse.duckdb')
    cnt = conn.execute("SELECT COUNT(*) FROM core.dim_location WHERE state = 'CT' AND county_fips IS NOT NULL AND county_fips <> ''").fetchone()[0]
    total_ct = conn.execute("SELECT COUNT(*) FROM core.dim_location WHERE state = 'CT'").fetchone()[0]
    print(f"\nCT locations with county_fips: {cnt}/{total_ct}")
    conn.close()

if __name__ == "__main__":
    main()