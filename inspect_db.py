import sqlite3

conn = sqlite3.connect('nala_rd_data.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()
print(f'Total tables: {len(tables)}\n')

# Show first 30 tables
print('First 30 tables:')
for table in tables[:30]:
    print(f'  {table[0]}')

if len(tables) > 30:
    print(f'\n... and {len(tables)-30} more')

# Show schema for first 5 tables
print('\n\n=== SCHEMA SAMPLES (First 5 tables) ===\n')
for i, table in enumerate(tables[:5]):
    table_name = table[0]
    cursor.execute(f"PRAGMA table_info('{table_name}');")
    columns = cursor.fetchall()
    print(f'\nTable: {table_name}')
    print('Columns:')
    for col in columns:
        print(f'  {col[1]} ({col[2]})')

conn.close()
