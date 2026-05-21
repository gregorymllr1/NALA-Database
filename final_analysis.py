import sqlite3

conn = sqlite3.connect('nala_rd_data.db')
cursor = conn.cursor()

print('=== DATA SOURCE TRACKING ===\n')
print('How the database tracks where data comes from:\n')

print('1. SOURCE IDENTIFICATION - Table Naming Convention:')
print('   Format: WORKBOOK_NAME + "_" + SHEET_NAME')
print('   Example: A12386_Performance_calc_sheet_Data_Calcs')
print('           - A12386 = Workbook ID from Excel filename')
print('           - Performance_calc_sheet_Data_Calcs = Sheet tab name\n')

print('2. WORKBOOK ORIGIN:')
print('   - Workbooks come from Google Drive folder (ID: 1x6_ALv4QUgzcHwcw5rcfx1hklEfoTE7a)')
print('   - Extracted as Excel files (.xlsx) via Extraction.py')
print('   - Each Excel file can have multiple sheets (tabs)\n')

print('3. SHEET TRACKING:')
print('   - Each tab in a workbook becomes a separate SQLite table')
print('   - Sheet name is preserved in the table name')
print('   - Enables tracking which original sheet each table came from\n')

# Get metadata
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
all_tables = [t[0] for t in cursor.fetchall()]

workbook_mapping = {}
for table_name in all_tables:
    if '_' in table_name:
        parts = table_name.split('_', 1)
        workbook = parts[0]
        sheet = parts[1] if len(parts) > 1 else 'Sheet1'
    else:
        workbook = table_name
        sheet = 'Sheet1'
    
    if workbook not in workbook_mapping:
        workbook_mapping[workbook] = []
    workbook_mapping[workbook].append(sheet)

print(f'4. STATISTICS:')
print(f'   Total workbooks: {len(workbook_mapping)}')
print(f'   Total tables (sheets): {len(all_tables)}')
print(f'   Avg sheets per workbook: {len(all_tables)/len(workbook_mapping):.1f}\n')

print('5. ENTITY TYPES - Identified in table names:')
entity_types = set()
for table_name in all_tables:
    if 'Cell' in table_name:
        entity_types.add('Cell')
    if 'Element' in table_name:
        entity_types.add('Element')
    if 'Membrane' in table_name:
        entity_types.add('Membrane')
    if 'Flatsheet' in table_name:
        entity_types.add('Flatsheet')
    if 'crossflow' in table_name:
        entity_types.add('Crossflow')

entity_count = {}
for etype in entity_types:
    count = len([t for t in all_tables if etype in t])
    entity_count[etype] = count

for etype, count in sorted(entity_count.items(), key=lambda x: x[1], reverse=True):
    print(f'   {count:4d}x  {etype}')

print('\n6. NO EXPLICIT SOURCE COLUMN:')
print('   - No dedicated "source" or "type" column tracks metadata')
print('   - No direct timestamp of when data was scraped')
print('   + Source is implicit in table name (workbook_sheet)')
print('   + Each table represents one Google Sheet tab\n')

print('7. COLUMN HEADER NORMALIZATION:')
print('   - Pandas reads Excel headers as-is from spreadsheets')
print('   - Missing headers become: "Unnamed: 0", "Unnamed: 1", etc')
print('   - No normalization/mapping logic is currently applied')
print('   - All column names are stored exactly as they appear in Excel\n')

print('8. SCHEMA FLEXIBILITY:')
print('   - All columns are stored as TEXT type (SQLite default from pandas)')
print('   - This accommodates varied column names across different spreadsheets')
print('   - Data types are not enforced at the database level\n')

# Sample a few different workbooks
print('9. EXAMPLE TABLE SAMPLES:\n')
sample_workbooks = sorted(list(workbook_mapping.keys()))[:3]
for wb in sample_workbooks:
    sheets = workbook_mapping[wb]
    if sheets:
        table_name = f"{wb}_{sheets[0]}"
        print(f'   Workbook: {wb}')
        print(f'   Sheets: {len(sheets)} total')
        print(f'   Example table: {table_name}')
        try:
            cursor.execute(f"PRAGMA table_info('{table_name}');")
            columns = cursor.fetchall()
            col_names = [c[1] for c in columns]
            print(f'   Columns ({len(columns)}): {", ".join(col_names[:5])}...')
        except:
            pass
        print()

conn.close()
