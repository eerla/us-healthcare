import subprocess
import os

# Remove all .duckdb files from git tracking
result = subprocess.run(['git', 'ls-files'], capture_output=True, text=True, cwd='C:/Users/gurub/projects/us-healthcare')
duckdb_files = [f for f in result.stdout.split('\n') if f.endswith('.duckdb')]
print(f'Found {len(duckdb_files)} .duckdb files in git tracking:')
for f in duckdb_files:
    print(f'  {f}')

if duckdb_files:
    result = subprocess.run(['git', 'rm', '--cached'] + duckdb_files, capture_output=True, text=True, cwd='C:/Users/gurub/projects/us-healthcare')
    print(result.stdout)
    print(result.stderr)