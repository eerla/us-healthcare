import duckdb
conn = duckdb.connect('db/warehouse.duckdb')

# Check CT county_fips status
total = conn.execute("SELECT COUNT(*) FROM core.dim_location WHERE state = 'CT'").fetchone()[0]
with_fips = conn.execute("SELECT COUNT(*) FROM core.dim_location WHERE state = 'CT' AND county_fips IS NOT NULL").fetchone()[0]
print(f'CT locations: {total}')
print(f'With county_fips: {with_fips}')
print(f'Missing: {total - with_fips}')

# Show some county_fips distribution
result = conn.execute("SELECT county_fips, COUNT(*) as cnt FROM core.dim_location WHERE state = 'CT' AND county_fips IS NOT NULL GROUP BY county_fips ORDER BY cnt DESC").fetchall()
for row in result:
    print(f'  {row[0]}: {row[1]}')

conn.close()