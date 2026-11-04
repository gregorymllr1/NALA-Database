import argparse
import datetime
import json
import sqlite3
import pandas as pd
import glob
import os
import shutil
import re
from config import DB_PATH_STR, DOWNLOAD_DIR, ARCHIVE_DIR

# Written by Extraction.py after a full Drive crawl: the list of workbooks that exist in Drive now.
MANIFEST_NAME = '_drive_manifest.json'

# Bookkeeping table: which workbook file each data table was ingested from. Lets us drop a
# workbook's tables when the Google Sheet is renamed/deleted, or when one of its tabs is removed.
# (index.html skips this table.)
SOURCES_TABLE = 'nala_meta_table_sources'

# Refuse to prune more than this fraction of tables in one run unless --force-prune is given,
# so a partial Drive listing can never wipe out the database.
MAX_PRUNE_FRACTION = 0.10


def sanitize_table_name(workbook_name, sheet_name):
    """Creates a clean SQLite table name combining the workbook and the tab name."""
    clean_workbook = str(workbook_name).replace('.xlsx', '')
    combined_name = f"{clean_workbook}_{sheet_name}"

    clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', combined_name)
    if clean_name[0].isdigit():
        clean_name = 'tbl_' + clean_name
    return clean_name


def workbook_table_prefix(workbook_name):
    """Prefix shared by every table created from this workbook (sanitize_table_name minus the tab)."""
    return sanitize_table_name(workbook_name, '')  # ends with '_'


def ensure_sources_table(conn):
    conn.execute(
        f'CREATE TABLE IF NOT EXISTS "{SOURCES_TABLE}" '
        '(table_name TEXT PRIMARY KEY, workbook TEXT NOT NULL, ingested_at TEXT NOT NULL)'
    )


def data_tables(conn):
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    return [r[0] for r in rows if r[0] != SOURCES_TABLE and not r[0].startswith('sqlite_')]


def drop_tables(conn, tables):
    for t in tables:
        conn.execute(f'DROP TABLE IF EXISTS "{t}"')
        conn.execute(f'DELETE FROM "{SOURCES_TABLE}" WHERE table_name = ?', (t,))


def ingest_workbook(conn, file_path):
    file_name = os.path.basename(file_path)
    # sheet_name=None forces Pandas to load every single tab in the workbook
    sheets_dict = pd.read_excel(file_path, sheet_name=None)
    now = datetime.datetime.now().isoformat(timespec='seconds')
    written = set()

    for sheet_name, df in sheets_dict.items():
        # Skip tabs that the engineers left completely blank
        if df.empty:
            print(f"  -> Skipped blank tab: '{sheet_name}' in {file_name}")
            continue

        table_name = sanitize_table_name(file_name, sheet_name)
        df.to_sql(name=table_name, con=conn, if_exists='replace', index=False)
        conn.execute(
            f'INSERT OR REPLACE INTO "{SOURCES_TABLE}" (table_name, workbook, ingested_at) VALUES (?, ?, ?)',
            (table_name, file_name, now),
        )
        written.add(table_name)
        print(f"Ingested [{sheet_name}] into table -> {table_name}")

    # Tabs that were deleted (or emptied/renamed) in this workbook since the last ingestion.
    previous = {r[0] for r in conn.execute(
        f'SELECT table_name FROM "{SOURCES_TABLE}" WHERE workbook = ?', (file_name,))}
    removed_tabs = sorted(previous - written)
    if removed_tabs:
        drop_tables(conn, removed_tabs)
        print(f"  -> Dropped {len(removed_tabs)} table(s) for tabs no longer in {file_name}")
    conn.commit()


def find_stale_tables(conn, current_workbooks):
    """Tables whose source workbook is not in Drive any more (renamed or deleted sheets)."""
    current = set(current_workbooks)
    tracked = dict(conn.execute(f'SELECT table_name, workbook FROM "{SOURCES_TABLE}"').fetchall())
    tracked_workbooks = set(tracked.values())
    # Untracked tables can only still belong to a current workbook that hasn't been re-ingested
    # since source tracking began. (Once a workbook is tracked, all of its tables are recorded.)
    untracked_prefixes = [workbook_table_prefix(wb) for wb in current if wb not in tracked_workbooks]

    stale = []
    for t in data_tables(conn):
        if t in tracked:
            if tracked[t] not in current:
                stale.append(t)
        elif not any(t.startswith(p) for p in untracked_prefixes):
            stale.append(t)
    return stale


def prune_stale_tables(conn, force=False, dry_run=False):
    manifest_path = os.path.join(DOWNLOAD_DIR, MANIFEST_NAME)
    if not os.path.exists(manifest_path):
        print("\nNo Drive manifest found (Extraction.py did not complete a crawl) - skipping stale-table pruning.")
        return

    with open(manifest_path, encoding='utf-8') as f:
        current_workbooks = json.load(f)['workbooks']

    stale = find_stale_tables(conn, current_workbooks)
    total = len(data_tables(conn))
    if not stale:
        print("\nStale-table check: none found.")
    else:
        print(f"\nStale-table check: {len(stale)} of {total} tables come from sheets that were renamed or deleted in Drive:")
        for t in stale:
            print(f"  - {t}")

        if dry_run:
            print("Dry run - nothing dropped.")
            return
        if len(stale) > MAX_PRUNE_FRACTION * total and not force:
            print(f"REFUSING to drop {len(stale)} tables (> {MAX_PRUNE_FRACTION:.0%} of the database). "
                  "If the Drive listing is correct, re-run with --force-prune.")
            return
        drop_tables(conn, stale)
        conn.commit()
        conn.execute('VACUUM')
        print(f"Dropped {len(stale)} stale table(s).")

    # Use each manifest only once, so a later run whose crawl fails can't prune against old data.
    shutil.move(manifest_path, os.path.join(ARCHIVE_DIR, MANIFEST_NAME))


def collate_to_sqlite(force_prune=False, prune_dry_run=False):
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)

    conn = sqlite3.connect(DB_PATH_STR)
    ensure_sources_table(conn)
    # Look for Excel files now instead of CSVs
    excel_files = glob.glob(os.path.join(DOWNLOAD_DIR, '*.xlsx'))

    if not excel_files:
        print("No new Excel files found in the download directory.")
    else:
        print(f"Found {len(excel_files)} workbooks. Starting Multi-Tab Ingestion...")

    for file_path in excel_files:
        file_name = os.path.basename(file_path)
        try:
            ingest_workbook(conn, file_path)
            # Archive the workbook once all tabs are successfully extracted
            shutil.move(file_path, os.path.join(ARCHIVE_DIR, file_name))
        except Exception as e:
            print(f"Error processing {file_name}: {e}")

    prune_stale_tables(conn, force=force_prune, dry_run=prune_dry_run)

    conn.close()
    print("\nMulti-tab Ingestion complete. Database is up to date.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Ingest downloaded workbooks into the SQLite database.")
    parser.add_argument('--force-prune', action='store_true',
                        help=f"Drop stale tables even if they exceed {MAX_PRUNE_FRACTION:.0%} of the database.")
    parser.add_argument('--prune-dry-run', action='store_true',
                        help="List stale tables without dropping them.")
    args = parser.parse_args()
    collate_to_sqlite(force_prune=args.force_prune, prune_dry_run=args.prune_dry_run)
