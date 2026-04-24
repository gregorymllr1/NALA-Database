# NALA Database Scraper

A Python application for managing Research & Development data. The project includes an interactive dashboard for querying the SQLite database, with tools for database maintenance and updates.

## Quick Overview

- **Dashboard** (for all users): Interactive web interface to query R&D data
- **Database** (included): Pre-built SQLite database with all ingested R&D data
- **Extraction & Ingestion** (for maintainer only): Update the database with new weekly R&D data

## For Regular Team Members: Using the Dashboard

### Quick Start (5 minutes)


```bash
# 1. Clone the repository
git clone <repository-url>
cd "NALA-Database"

# 2. Create and activate virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the dashboard
# Open dashboard.html in a web browser or use:
start dashboard.html  # Windows
open dashboard.html   # macOS
```

The dashboard connects to `nala_rd_data.db` and displays all available R&D data.

## For Database Maintainer: Updating the Database

### When New Weekly Data Arrives

Fast path (recommended):

```bash
.venv\Scripts\python.exe weekly_update.py  # Windows
python weekly_update.py                      # macOS/Linux (with venv activated)
```

This runs extraction, ingestion, and git add/commit/push for `nala_rd_data.db`.

Manual path:

```bash
# 1. Extract Excel files from Google Drive
python Extraction.py

# 2. Ingest files into the database
python ingestion.py

# 3. Commit updated database to share with team
git add nala_rd_data.db
git commit -m "Updated database: [brief description of new data]"
git push
```

See [MAINTAINER.md](MAINTAINER.md) for detailed maintainer instructions.

## Project Structure

```
.
├── nala_rd_data.db          # ✓ Main SQLite database (distributed with project)
├── dashboard.html           # ✓ Web dashboard for data queries (for all users)
├── requirements.txt         # ✓ Python dependencies
├── config.py                # ✓ Centralized paths and settings
├── README.md                # ✓ This file
│
├── Extraction.py            # For maintainer: Download from Google Drive
├── ingestion.py             # For maintainer: Update database
├── analysis.py              # For maintainer: Generate reports
├── MAINTAINER.md            # For maintainer: Detailed instructions
│
└── [Directories - not needed for regular use]
	 ├── data/                # Downloaded Excel files (auto-created)
	 ├── archived_data/       # Processed files (auto-created)
	 └── archived_rd_csvs/    # CSV archives (auto-created)
```

## For All Users

The database is already built and included. You should:

1. **Install dependencies** (one-time):
	```bash
	pip install -r requirements.txt
	```

2. **Access the dashboard** to query data

3. **Update when notified** (pull latest from Git):
	```bash
	git pull
	```

The database is automatically updated by the maintainer and shared via Git.

## Configuration

All paths and settings are centralized in `config.py`:

- `DB_PATH`: SQLite database location
- `SEARCH_TERM`: Default analysis term
- Other settings used by extraction/ingestion scripts


## Troubleshooting

**"ModuleNotFoundError" when running dashboard:**
```bash
# Ensure virtual environment is activated
.venv\Scripts\activate
# Install requirements
pip install -r requirements.txt
```

**Database seems outdated:**
```bash
# Pull the latest version
git pull
```

## Support

- **For dashboard issues**: Check dashboard.html source code
- **For setup issues**: Refer to installation steps above
- **For database updates**: Contact the database maintainer
