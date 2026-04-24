# NALA Database Scraper

A Python application for scraping Research & Development data from Google Drive, organizing it into a SQLite database, and generating analysis visualizations.

## Project Overview

- **Extraction.py**: Downloads Excel files from Google Drive
- **ingestion.py**: Parses Excel files and ingests them into the SQLite database
- **analysis.py**: Analyzes data and generates visualizations
- **dashboard.html**: Interactive dashboard for data visualization

## Quick Start

### 1. Prerequisites
- Python 3.8+
- Git

### 2. Setup Instructions

```bash
# Clone the repository
git clone <repository-url>
cd "NALA-Database"

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Google Drive Setup (First Time Only)

See [SETUP_FOR_TEAM.md](SETUP_FOR_TEAM.md) for detailed Google Drive authentication setup.

### 4. Usage

**Extract data from Google Drive:**
```bash
python Extraction.py
```

**Ingest downloaded Excel files into database:**
```bash
python ingestion.py
```

**Run analysis and generate visualizations:**
```bash
python analysis.py
```

## Project Structure

```
.
├── nala_rd_data.db          # Main SQLite database (included in distribution)
├── client_secret.json        # Google OAuth credentials (create on first setup)
├── token.json                # Google OAuth token (generated after first auth)
├── requirements.txt          # Python dependencies
├── config.py                 # Configuration and paths
├── Extraction.py             # Google Drive downloader
├── ingestion.py              # Database ingester
├── analysis.py               # Data analysis and visualization
├── dashboard.html            # Web dashboard
├── data/                     # Downloaded Excel files (auto-created)
├── archived_data/            # Archived processed files (auto-created)
└── archived_rd_csvs/         # Archive of CSV exports (auto-created)
```

## Database

The project includes `nala_rd_data.db`, a SQLite database containing all ingested R&D data. This database is version-controlled and distributed with the project.

### Updating the Database

1. Run `Extraction.py` to download new files from Google Drive
2. Run `ingestion.py` to process and add them to the database
3. Commit changes to `nala_rd_data.db` to Git for team synchronization

## Configuration

All paths and settings are centralized in `config.py`:

- `DB_PATH`: Location of SQLite database
- `DATA_DIR`: Downloaded files directory
- `ARCHIVE_DIR`: Archived data directory
- `FOLDER_ID`: Google Drive folder for data extraction
- `SEARCH_TERM`: Default search term for analysis

Modify `config.py` to customize behavior for your environment.

## Common Issues

**"module not found" errors**: Ensure you've activated the virtual environment and installed requirements:
```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

**Google Drive authentication fails**: Delete `token.json` and run `Extraction.py` again to re-authenticate.

**Database locked**: Ensure no other process is using `nala_rd_data.db`. Close other Python instances and try again.

## Team Collaboration

1. Each team member clones the repository
2. First time: Complete Google Drive setup in [SETUP_FOR_TEAM.md](SETUP_FOR_TEAM.md)
3. Run scripts to extract/ingest new data
4. Commit database changes for team synchronization

## Version Control Notes

- `client_secret.json` and `token.json` are not tracked (in `.gitignore`)
- Each team member needs their own Google OAuth credentials
- `nala_rd_data.db` IS tracked and shared across the team
- The `data/`, `archived_data/`, and `archived_rd_csvs/` directories are not tracked to avoid large file sync issues

## Support

For issues or questions, refer to:
- Individual script docstrings and comments
- Google Drive API documentation: https://developers.google.com/drive/api
- SQLite documentation: https://www.sqlite.org/docs.html
