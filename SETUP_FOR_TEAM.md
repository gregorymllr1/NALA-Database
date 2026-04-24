# Team Setup Guide

This guide walks through the one-time setup needed for team members to start using the NALA Database Scraper.

## Step 1: Clone and Install

```bash
# Clone the repository
git clone <repository-url>
cd "NALA-Database"

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Google Drive Setup (Required for Data Extraction)

If you need to extract new data from Google Drive, complete these steps:

### 2a. Get Google Cloud Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or use an existing one
3. Enable the Google Drive API:
   - Search for "Google Drive API"
   - Click "Enable"
4. Create OAuth 2.0 credentials:
   - Go to "Credentials" in the left sidebar
   - Click "Create Credentials" → "OAuth client ID"
   - Select "Desktop application"
   - Download the JSON file
5. Rename the downloaded file to `client_secret.json` and place it in the project root directory

### 2b. First Authentication

Run the extraction script to authenticate:

```bash
python Extraction.py
```

This will:
- Open your browser for Google authentication
- Create `token.json` (do not commit this to Git)
- Start downloading files from the shared Google Drive folder

## Step 3: Verify Installation

Test each component:

```bash
# Test database access
python -c "import sqlite3; print(sqlite3.connect('nala_rd_data.db').execute('SELECT count(name) FROM sqlite_master WHERE type=\"table\"').fetchone())"

python ingestion.py
```

## Step 4: Git Configuration

Ensure your Git is configured to ignore personal credentials:

```bash
# Verify .gitignore is in place
cat .gitignore
```

You should see:
- `client_secret.json` ✓
## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'google'"
**Solution**: Ensure virtual environment is activated and requirements are installed
```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: Google authentication fails
**Solution**: Delete `token.json` and try again
```bash
rm token.json
python Extraction.py
```

### Issue: "The caller does not have permission to access the shared drive"
**Solution**: Verify you have access to the Google Drive folder (ID in `config.py`)
- Ask your team lead to grant you access to the shared folder
- Verify the `FOLDER_ID` in `config.py` is correct

### Issue: Database is locked
**Solution**: Ensure no other Python process is using the database
```bash
# Kill any running Python processes
# Windows (PowerShell):
Get-Process python | Stop-Process -Force

# macOS/Linux:
pkill -f python
```

## Regular Workflow

   ```bash
   git pull
   ```

2. **Extract new data** (if needed)
   ```bash
   python Extraction.py
   ```

3. **Ingest into database** (if new files were downloaded)
   ```bash
   python ingestion.py
   ```

4. **Analyze and visualize**
   ```bash
   python analysis.py
   ```

5. **Commit database changes** if new data was added
   ```bash
   git add nala_rd_data.db
   git commit -m "Updated database with new extraction data"
   git push
   ```

## Updating Database Across Team

When you've extracted and ingested new data, share it with the team:

```bash
git add nala_rd_data.db
git commit -m "Updated database: [brief description of new data]"
git push
```

Other team members can then pull the update:
```bash
git pull
```

This keeps everyone synchronized with the latest R&D data.
