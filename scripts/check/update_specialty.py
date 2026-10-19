import duckdb
import pandas as pd

# Load mapping
df = pd.read_csv('nucc_taxonomy.csv')
mapping = {}
for _, row in df.iterrows():
    code = row['Code']
    classification = row['Classification']
    grouping = row['Grouping']
    specialization = row['Specialization']
    
    if pd.notna(classification) and str(classification).strip():
        specialty = str(classification).strip()
    elif pd.notna(row['Specialization']) and str(row['Specialization']).strip():
        specialty = str(row['Specialization']).strip()
    else:
        specialty = str(grouping).strip()
    
    mapping[code] = specialty.strip()

conn = duckdb.connect('db/warehouse.duckdb')

# Update dim_specialty
updated = 0
for code, specialty in mapping.items():
    result = conn.execute("UPDATE core.dim_specialty SET specialty_group = ? WHERE taxonomy_code = ?", [specialty, code])
    # DuckDB doesn't return affected rows count directly, just execute

# Check remaining 'Other'
result = conn.execute("SELECT COUNT(*) FROM core.dim_specialty WHERE specialty_group = 'Other'").fetchone()
print(f'Remaining Other: {result[0]}')

# Show specialty groups
result = conn.execute("SELECT specialty_group, COUNT(*) FROM core.dim_specialty GROUP BY specialty_group ORDER BY COUNT(*) DESC").fetchall()
for row in result:
    print(f'  {row[0]}: {row[1]}')

conn.close()