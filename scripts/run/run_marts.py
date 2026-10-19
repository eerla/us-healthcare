import duckdb

conn = duckdb.connect('db/nppes_raw.duckdb')

# Run core population table
with open('core/fact_population.sql') as f:
    conn.execute(f.read())
print('fact_population created')
print(f'Rows: {conn.execute("SELECT COUNT(*) FROM core.fact_population").fetchone()[0]}')

# Run mart models
with open('mart/mart_provider_supply.sql') as f:
    conn.execute(f.read())
print('mart_provider_supply created')
print(f'Rows: {conn.execute("SELECT COUNT(*) FROM mart.mart_provider_supply").fetchone()[0]}')

with open('mart/mart_specialty_supply.sql') as f:
    conn.execute(f.read())
print('mart_specialty_supply created')
print(f'Rows: {conn.execute("SELECT COUNT(*) FROM mart.mart_specialty_supply").fetchone()[0]}')

with open('mart/mart_geographic_access.sql') as f:
    conn.execute(f.read())
print('mart_geographic_access created')
print(f'Rows: {conn.execute("SELECT COUNT(*) FROM mart.mart_geographic_access").fetchone()[0]}')

with open('mart/mart_provider_concentration.sql') as f:
    conn.execute(f.read())
print('mart_provider_concentration created')
print(f'Rows: {conn.execute("SELECT COUNT(*) FROM mart.mart_provider_concentration").fetchone()[0]}')

conn.close()
print('All mart models created successfully!')