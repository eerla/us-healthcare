import duckdb
conn = duckdb.connect('db/warehouse.duckdb')
# Check if CT exists in dim_location
result = conn.execute("SELECT COUNT(*) FROM core.dim_location WHERE state = 'CT'").fetchone()[0]
print(f'CT count: {result}')

result = conn.execute("SELECT COUNT(*) FROM core.dim_location WHERE state = 'Connecticut'").fetchone()[0]
print(f'Connecticut count: {result}')

# Check bridge table
result = conn.execute("""
    SELECT COUNT(*) FROM core.bridge_provider_location bpl
    JOIN core.dim_location l ON bpl.location_sk = l.location_sk
    WHERE l.state = 'CT' AND bpl.is_primary = true
""").fetchone()[0]
print(f'CT primary bridges: {result}')

conn.close()