import duckdb

conn = duckdb.connect('db/nppes_raw.duckdb')
# Create schemas
conn.execute('CREATE SCHEMA IF NOT EXISTS staging')
conn.execute('CREATE SCHEMA IF NOT EXISTS core')
conn.execute('CREATE SCHEMA IF NOT EXISTS mart')

# Run staging models
with open('staging/stg_npi.sql') as f:
    conn.execute(f.read())
print('stg_npi created')
print(f'Rows: {conn.execute("SELECT COUNT(*) FROM staging.stg_npi").fetchone()[0]}')

with open('staging/stg_npi_location.sql') as f:
    conn.execute(f.read())
print('stg_npi_location created')
print(f'Rows: {conn.execute("SELECT COUNT(*) FROM staging.stg_npi_location").fetchone()[0]}')

with open('staging/stg_npi_other_names.sql') as f:
    conn.execute(f.read())
print('stg_npi_other_names created')
print(f'Rows: {conn.execute("SELECT COUNT(*) FROM staging.stg_npi_other_names").fetchone()[0]}')

with open('staging/stg_npi_endpoints.sql') as f:
    conn.execute(f.read())
print('stg_npi_endpoints created')
print(f'Rows: {conn.execute("SELECT COUNT(*) FROM staging.stg_npi_endpoints").fetchone()[0]}')

# Run core models
with open('core/dim_provider.sql') as f:
    conn.execute(f.read())
print('dim_provider created')
print(f'Rows: {conn.execute("SELECT COUNT(*) FROM core.dim_provider").fetchone()[0]}')

with open('core/dim_location.sql') as f:
    conn.execute(f.read())
print('dim_location created')
print(f'Rows: {conn.execute("SELECT COUNT(*) FROM core.dim_location").fetchone()[0]}')

with open('core/dim_specialty.sql') as f:
    conn.execute(f.read())
print('dim_specialty created')
print(f'Rows: {conn.execute("SELECT COUNT(*) FROM core.dim_specialty").fetchone()[0]}')

with open('core/bridge_provider_location.sql') as f:
    conn.execute(f.read())
print('bridge_provider_location created')
print(f'Rows: {conn.execute("SELECT COUNT(*) FROM core.bridge_provider_location").fetchone()[0]}')

conn.close()
print('All models created successfully!')