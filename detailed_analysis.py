import sqlite3

conn = sqlite3.connect('nala_rd_data.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
all_tables = [t[0] for t in cursor.fetchall()]

print('=== TABLE NAMING STRUCTURE ===\n')

# Parse the naming convention
# Format: workbook_sheetname (created by sanitize_table_name in ingestion.py)
# The workbook name comes from the Excel file name, sheet name comes from tab name

# Count tables by workbook prefix (extract first part before underscore)
workbooks = {}
for table_name in all_tables:
    # Find the first underscore to split workbook from sheet
    if '_' in table_name:
        parts = table_name.split('_', 1)
        workbook_id = parts[0]
    else:
        workbook_id = table_name
    
    if workbook_id not in workbooks:
        workbooks[workbook_id] = {'count': 0, 'tables': []}
    workbooks[workbook_id]['count'] += 1
    workbooks[workbook_id]['tables'].append(table_name)

print(f'Number of unique workbooks: {len(workbooks)}')
print(f'Total tables: {len(all_tables)}\n')

# Look for patterns in sheet names
sheet_patterns = {}
for table_name in all_tables:
    # Extract everything after first underscore
    if '_' in table_name:
        parts = table_name.split('_', 1)
        sheet_part = parts[1] if len(parts) > 1 else ''
    else:
        sheet_part = ''
    
    # Count occurrences
    if sheet_part:
        sheet_patterns[sheet_part] = sheet_patterns.get(sheet_part, 0) + 1

print(f'Unique sheet names: {len(sheet_patterns)}')
print('\nMost common sheet names:')
for sheet, count in sorted(sheet_patterns.items(), key=lambda x: x[1], reverse=True)[:20]:
    print(f'  {count:4d}x  {sheet}')

print('\n\n=== CHECKING FOR ENTITY/ELEMENT TRACKING ===\n')

# Sample several tables to look for cell/element references
sample_count = 0
for table_name in all_tables:
    if 'Cell' in table_name or 'Element' in table_name or 'Membrane' in table_name:
        cursor.execute(f"PRAGMA table_info('{table_name}');")
        columns = [c[1] for c in cursor.fetchall()]
        
        if sample_count < 10:
            print(f'Table: {table_name}')
            print(f'  Columns: {columns[:10]}')
            
            # Try to get sample data
            try:
                cursor.execute(f"SELECT * FROM '{table_name}' LIMIT 2;")
                rows = cursor.fetchall()
                if rows:
                    print(f'  Sample data: {rows[0][:5]}...')
            except:
                pass
            print()
            sample_count += 1

conn.close()
