import os
import io
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# --- Configuration ---
CLIENT_SECRET_FILE = 'client_secret.json' 
FOLDER_ID = '1x6_ALv4QUgzcHwcw5rcfx1hklEfoTE7a' 

# Use a raw string (r) to prevent Windows path escaping errors
DOWNLOAD_DIR = r'C:\Users\grego\Projects\NALA Database Scraper\data'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authenticate_user():
    """Authenticates using your saved browser login."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('drive', 'v3', credentials=creds)
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

    print(f"\nFound {len(sheets_to_download)} Google Sheets! Beginning export to CSV...")
    
  # ... (inside the for loop of crawl_and_download_sheets) ...
    for item in sheets_to_download:
        file_id = item['id']
        # CHANGE 1: Save as .xlsx instead of .csv
        file_name = f"{item['name']}.xlsx" 
        
        # Update this line in Extraction.py
        safe_file_name = file_name.replace('/', '-').replace('\\', '-').replace('?', '').replace('*', '').replace(':', '-').replace('"', '').replace('<', '').replace('>', '').replace('|', '')
        file_path = os.path.join(download_path, safe_file_name)

        if os.path.exists(file_path):
            print(f"Skipping {safe_file_name} (already exists locally).")
            continue

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
            
            print(f"Exported: {safe_file_name}")
        except Exception as e:
            print(f"Failed to export {safe_file_name}. Error: {e}")

if __name__ == '__main__':
    drive_service = authenticate_user()
    crawl_and_download_sheets(drive_service, FOLDER_ID, DOWNLOAD_DIR)
    print("\nExtraction complete. Ready for SQLite collation.")