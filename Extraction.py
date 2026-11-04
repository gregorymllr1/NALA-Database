import os
import io
import json
import os.path
import httplib2
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google_auth_httplib2 import AuthorizedHttp
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from config import CLIENT_SECRET_FILE, TOKEN_FILE, FOLDER_ID, DOWNLOAD_DIR, SCOPES

REQUEST_TIMEOUT = 120  # seconds

# Written after a complete Drive crawl; ingestion.py uses it to drop tables whose
# source sheet was renamed or deleted in Drive (see prune_stale_tables there).
MANIFEST_NAME = '_drive_manifest.json'


def safe_xlsx_name(sheet_name):
    file_name = f"{sheet_name}.xlsx"
    return file_name.replace('/', '-').replace('\\', '-').replace('?', '').replace('*', '').replace(':', '-').replace('"', '').replace('<', '').replace('>', '').replace('|', '')

def authenticate_user():
    """Authenticates using your saved browser login."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    authed_http = AuthorizedHttp(creds, http=httplib2.Http(timeout=REQUEST_TIMEOUT))
    service = build('drive', 'v3', http=authed_http)
    return service

def crawl_and_download_sheets(service, root_folder_id, download_path):
    """Crawls all subfolders to find and export Google Sheets."""
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    folders_to_search = [root_folder_id]
    sheets_to_download = []

    print("Crawling through subfolders to find Google Sheets...")

    # --- Phase 1: Map out the entire folder tree ---
    while folders_to_search:
        current_folder = folders_to_search.pop(0)
        page_token = None
        
        while True:
            query = f"'{current_folder}' in parents and trashed=false"
            results = service.files().list(
                q=query, 
                spaces='drive', 
                fields='nextPageToken, files(id, name, mimeType)',
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
                pageSize=1000, # Grab up to 1000 items at a time
                pageToken=page_token
            ).execute()
            
            items = results.get('files', [])

            for item in items:
                if item['mimeType'] == 'application/vnd.google-apps.folder':
                    # It's a subfolder! Add it to the queue to be searched
                    folders_to_search.append(item['id'])
                elif item['mimeType'] == 'application/vnd.google-apps.spreadsheet':
                    # It's a Google Sheet! Save it to our download list
                    sheets_to_download.append(item)

            # Check if there are more pages of files in this specific folder
            page_token = results.get('nextPageToken')
            if not page_token:
                break

    # --- Phase 2: Export everything we found ---
    if not sheets_to_download:
        print("\nNo Google Sheets found anywhere in that folder tree.")
        return

    print(f"\nFound {len(sheets_to_download)} Google Sheets! Beginning export to .xlsx...")

    # Record every sheet that currently exists in Drive (the crawl completed, so this is the
    # full list). Ingestion treats any table whose workbook is not listed here as stale.
    manifest = {
        'workbooks': sorted({safe_xlsx_name(item['name']) for item in sheets_to_download}),
    }
    with open(os.path.join(download_path, MANIFEST_NAME), 'w', encoding='utf-8') as mf:
        json.dump(manifest, mf, indent=1)
    print(f"Wrote Drive manifest ({len(manifest['workbooks'])} workbooks).")

    for item in sheets_to_download:
        file_id = item['id']
        safe_file_name = safe_xlsx_name(item['name'])
        file_path = os.path.join(download_path, safe_file_name)

        # A 0-byte file is the remnant of an earlier failed export — re-download it instead of
        # skipping it forever (that left workbooks frozen at their first ingested version).
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            print(f"Skipping {safe_file_name} (already exists locally).")
            continue

        fh = None
        try:
            # CHANGE 2: Request the Excel MIME type instead of CSV
            request = service.files().export_media(
                fileId=file_id, 
                mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            fh = io.FileIO(file_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            fh.close()

            print(f"Exported: {safe_file_name}")
        except Exception as e:
            print(f"Failed to export {safe_file_name}. Error: {e}")
            # Don't leave a partial/empty file behind for ingestion to choke on.
            if fh is not None:
                fh.close()
            if os.path.exists(file_path):
                os.remove(file_path)

if __name__ == '__main__':
    drive_service = authenticate_user()
    crawl_and_download_sheets(drive_service, FOLDER_ID, DOWNLOAD_DIR)
    print("\nExtraction complete. Ready for SQLite collation.")