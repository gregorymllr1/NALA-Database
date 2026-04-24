import sqlite3
import pandas as pd
import glob
import os
import shutil
import re
from config import DB_PATH_STR, DOWNLOAD_DIR, ARCHIVE_DIR

def sanitize_table_name(workbook_name, sheet_name):
    """Creates a clean SQLite table name combining the workbook and the tab name."""
    clean_workbook = str(workbook_name).replace('.xlsx', '')
    combined_name = f"{clean_workbook}_{sheet_name}"
    
    clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', combined_name)
    if clean_name[0].isdigit():
        clean_name = 'tbl_' + clean_name
    return clean_name

def collate_to_sqlite():
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)

    conn = sqlite3.connect(DB_PATH_STR)
    # Look for Excel files now instead of CSVs
    excel_files = glob.glob(os.path.join(DOWNLOAD_DIR, '*.xlsx'))
    
    if not excel_files:
        print("No new Excel files found in the download directory.")
        conn.close()
        return

    print(f"Found {len(excel_files)} workbooks. Starting Multi-Tab Ingestion...")

    for file_path in excel_files:
        file_name = os.path.basename(file_path)
        
        try:
            # sheet_name=None forces Pandas to load every single tab in the workbook
            sheets_dict = pd.read_excel(file_path, sheet_name=None)
            
            # Iterate through every tab in the workbook
            for sheet_name, df in sheets_dict.items():
                
                # Skip tabs that the engineers left completely blank
                if df.empty:
                    print(f"  -> Skipped blank tab: '{sheet_name}' in {file_name}")
                    continue
                    
                table_name = sanitize_table_name(file_name, sheet_name)
                
                # Write this specific tab to its own SQLite table
                df.to_sql(
                    name=table_name, 
                    con=conn, 
                    if_exists='replace', 
                    index=False
                )
                print(f"Ingested [{sheet_name}] into table -> {table_name}")
            
            # Archive the workbook once all tabs are successfully extracted
            archive_path = os.path.join(ARCHIVE_DIR, file_name)
            shutil.move(file_path, archive_path)

        except Exception as e:
            print(f"Error processing {file_name}: {e}")

    conn.close()
    print("\nMulti-tab Ingestion complete. Database is up to date.")

if __name__ == '__main__':
    collate_to_sqlite()