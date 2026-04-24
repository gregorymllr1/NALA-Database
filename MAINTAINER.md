# Database Maintainer Guide

This guide is for the database maintainer responsible for keeping `nala_rd_data.db` updated with new R&D data.

## Overview

Your role is to:
1. **Weekly**: Extract new Excel files from Google Drive
2. **Weekly**: Ingest the new data into the database
3. **Weekly**: Share updated database with team via Git

Regular team members only use the dashboard and don't need these tools.

## Prerequisites (One-Time Setup)

Before you can extract data, you need Google Drive credentials:

### Step 1: Create Google Cloud Project Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or use an existing one
3. Enable the Google Drive API:
   - Search for "Google Drive API"
   - Click "Enable"
4. Create OAuth 2.0 Desktop Credentials:
   - Go to "Credentials" in the left sidebar
   - Click "Create Credentials" → "OAuth client ID"
   - Select "Desktop application"
   - Download the JSON file
5. **Important**: Rename the downloaded file to `client_secret.json` and place it in the project root directory

### Step 2: Initial Authentication

Run the extraction script to authenticate with Google:

```bash
# Activate your virtual environment first
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Run extraction
python Extraction.py
```

This will:
- Open your browser to authenticate
- Create `token.json` (do not commit to Git)
- Begin downloading files

## Weekly Workflow

### 1. Extract New Data from Google Drive

```bash
# Activate virtual environment
.venv\Scripts\activate

# Download new Excel files
python Extraction.py
```

**What happens**:
- Downloads new files from the shared Google Drive folder
- Saves them to `data/` directory
- Lists files downloaded

### 2. Ingest Data into Database

```bash
python ingestion.py
```

**What happens**:
- Reads all Excel files from `data/` directory
- Parses all sheets in each workbook
- Creates/updates database tables
- Archives processed files to `archived_data/`
- Updates `nala_rd_data.db`

### 3. Commit and Share with Team

```bash
# Check what changed
git status

# Add the updated database
git add nala_rd_data.db

# Commit with description
git commit -m "Updated database: [describe new data, e.g., 'Q2 2026 membrane tests']"

# Push to repository
git push
```

Team members will pull these changes with `git pull`.

## Detailed Command Reference

### Extraction.py

Connects to Google Drive and downloads Excel files to `data/` directory.

```bash
python Extraction.py
```

**Features**:
- Authenticates with Google OAuth
- Crawls shared Google Drive folder
- Downloads all Excel files
- Shows progress of each download
- Handles resuming if interrupted

**Output**:
- Downloaded files in `data/` directory
- `token.json` created (gitignored)
- Console messages showing download progress

### ingestion.py

Reads Excel files and updates the SQLite database.

```bash
python ingestion.py
```

**Features**:
- Reads all `.xlsx` files from `data/` directory
- Processes every sheet in each workbook
- Creates appropriate table names from workbook/sheet names
- Replaces (updates) existing tables with same name
- Automatically archives processed files

**Output**:
- Updated `nala_rd_data.db`
- Archived Excel files moved to `archived_data/`
- Console messages showing ingestion progress

### analysis.py

Generates analysis visualizations (optional, for reporting).

```bash
python analysis.py
```

**Features**:
- Queries the database
- Generates performance plots
- Saves visualizations

**Output**:
- Console plots and charts
- `.html` or `.png` files (if configured)

## Understanding the Database

The database is SQLite with tables created from each sheet of each workbook.

### Table Naming

Table names are derived from workbook and sheet names:
- Workbook: `2024-06-24 2k ppm NaCl.xlsx`
- Sheet: `Time Series`
- Table: `tbl_2024_06_24_2k_ppm_NaCl_Time_Series`

Special rules:
- Non-alphanumeric characters replaced with underscores
- If table name starts with a digit, `tbl_` prefix added
- Spaces converted to underscores

### Querying the Database

You can query directly if needed:

```python
import sqlite3
from config import DB_PATH_STR

conn = sqlite3.connect(DB_PATH_STR)
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(tables)

# Query specific table
cursor.execute("SELECT * FROM [your_table_name];")
data = cursor.fetchall()
print(data)

conn.close()
```

## Troubleshooting

### Issue: "Google Drive authentication fails"
**Solution**: Delete `token.json` and run `Extraction.py` again
```bash
rm token.json
python Extraction.py
```

### Issue: "No files found" during extraction
**Cause**: No new files in the Google Drive folder
**Solution**: Check if new data has been uploaded to the shared folder. Update the `FOLDER_ID` in `config.py` if pointing to wrong folder.

### Issue: "Database locked" error
**Cause**: Another process is using the database
**Solution**: 
- Close other Python instances
- Ensure no team members are accessing the dashboard during ingestion
- Close the database connection properly

```bash
# Kill any Python processes (Windows PowerShell):
Get-Process python | Stop-Process -Force
```

### Issue: "Ingestion is slow" for large files
**Cause**: Large workbooks with many sheets take time to process
**Solution**: Normal behavior. Let it complete. Processing can take a few minutes per workbook.

### Issue: Excel file won't parse
**Cause**: Corrupted file or unsupported format
**Solution**:
- Verify the Excel file is valid
- Ensure it's in `.xlsx` format (not `.xls`)
- Check for special characters in sheet names that might cause issues

## Best Practices

### Before Extraction
- Check if new data is available in Google Drive
- Ensure you have space in `data/` directory
- Verify your Google Drive token is valid (delete `token.json` if older than a few weeks)

### During Ingestion
- Don't interrupt the process (wait for "complete" message)
- Ensure no one is accessing the database
- Monitor console output for errors

### After Ingestion
- Verify database size is increasing (shows new data was added)
- Quickly commit and push changes for team
- Notify team that new data is available

### Before Committing
```bash
# Always verify changes look correct
git diff nala_rd_data.db  # Note: binary diff won't be useful

# Check status
git status

# Verify nothing sensitive is being committed
git add -p  # Interactive add to review changes
```

## Configuration

Key settings in `config.py` for maintainer:

```python
FOLDER_ID = '1x6_ALv4QUgzcHwcw5rcfx1hklEfoTE7a'  # Google Drive folder
CLIENT_SECRET_FILE = 'client_secret.json'         # Your credentials
TOKEN_FILE = 'token.json'                         # Generated token (gitignored)
```

You can customize these if needed, but default should work.

## Team Communication

When you update the database, consider notifying the team:

**Good commit message**:
```
git commit -m "Updated database: Added Q2 2026 membrane fouling tests (5 new experiments)"
```

**Then notify team**:
- "New data available! Run `git pull` to get the latest database."
- Or send a summary of what was added

## Maintenance Schedule

Suggested schedule:
- **Weekly**: Check for new data every Friday afternoon
- **Extract**: Run `Extraction.py` if files available
- **Ingest**: Run `ingestion.py` immediately after
- **Commit**: Push to Git same day
- **Notify**: Tell team new data is available

## Disaster Recovery

If something goes wrong:

### Database corrupted
```bash
# Reset to last good version
git checkout nala_rd_data.db
```

### Too many files in data/ directory
```bash
# Manually move old files to archived_data/
mv data/*.xlsx archived_data/
```

### Need to redo ingestion
```bash
# Delete current database (careful!)
rm nala_rd_data.db

# Move archived files back to data/
mv archived_data/*.xlsx data/

# Re-run ingestion
python ingestion.py
```

## Support

- **Questions about Python**: Refer to comments in extraction/ingestion scripts
- **Google Drive API help**: https://developers.google.com/drive/api
- **SQLite help**: https://www.sqlite.org/docs.html
- **Issues with workflow**: Check troubleshooting section above
