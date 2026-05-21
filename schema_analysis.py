import sqlite3
import re

conn = sqlite3.connect('nala_rd_data.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = [t[0] for t in cursor.fetchall()]

print(f'TOTAL TABLES: {len(tables)}\n')

# Analyze table naming patterns
print('=== TABLE NAMING PATTERNS ===\n')

patterns = {}
for table in tables:
    # Extract workbook name and sheet name from table name
    # Format appears to be: workbook_sheetname
    # Example: A12386_Performance_calc_sheet_Data_Calcs
    parts = table.split('_')
    if len(parts) > 0:
        workbook = parts[0]  # e.g., "A12386"
        if workbook not in patterns:
            patterns[workbook] = []
        patterns[workbook].append(table)

print(f'Unique workbooks: {len(patterns)}')
print('\nSample workbooks and their tables:')
for i, (workbook, table_list) in enumerate(sorted(patterns.items())[:10]):
    print(f'\n  {workbook} ({len(table_list)} tables)')
    for table in table_list[:3]:
        print(f'    - {table}')
    if len(table_list) > 3:
        print(f'    ... and {len(table_list)-3} more')

# Analyze unique column names across all tables
print('\n\n=== UNIQUE COLUMN NAMES (Sampling 100 random tables) ===\n')
import random
sample_tables = random.sample(tables, min(100, len(tables)))
all_columns = set()
for table in sample_tables:
    try:
        cursor.execute(f"PRAGMA table_info('{table}');")
        columns = cursor.fetchall()
        for col in columns:
            all_columns.add(col[1])
    except:
        pass

print(f'Total unique column names (from sample): {len(all_columns)}')
print('\nSample column names:')
for col in sorted(list(all_columns))[:50]:
    print(f'  {col}')

# Check if there's any metadata about source files
print('\n\n=== CHECKING FOR SOURCE/TYPE COLUMNS ===\n')
source_columns = [c for c in all_columns if 'source' in c.lower() or 'type' in c.lower() or 'file' in c.lower()]
print(f'Columns with "source", "type", or "file": {source_columns}')

# Look for common keyword columns in first few tables
print('\n\n=== SAMPLE DATA FROM FIRST TABLE ===\n')
table = tables[0]
cursor.execute(f"SELECT * FROM '{table}' LIMIT 5;")
result = cursor.fetchall()
cursor.execute(f"PRAGMA table_info('{table}');")
columns = [c[1] for c in cursor.fetchall()]
print(f'Table: {table}')
print(f'Columns: {columns}')
print('First 5 rows:')
for row in result:
    print(f'  {row}')

conn.close()
