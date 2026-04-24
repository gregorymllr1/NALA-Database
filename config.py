"""
Configuration module for NALA Database Scraper
Manages paths and settings for the project
"""

import os
from pathlib import Path

# Base directory - relative to this file
BASE_DIR = Path(__file__).resolve().parent

# Database
DB_PATH = BASE_DIR / 'nala_rd_data.db'

# Directories
DATA_DIR = BASE_DIR / 'data'
ARCHIVE_DIR = BASE_DIR / 'archived_data'
ARCHIVED_CSV_DIR = BASE_DIR / 'archived_rd_csvs'

# Create directories if they don't exist
for directory in [DATA_DIR, ARCHIVE_DIR, ARCHIVED_CSV_DIR]:
    directory.mkdir(exist_ok=True)

# Google Drive Configuration
DOWNLOAD_DIR = str(DATA_DIR)
FOLDER_ID = '1x6_ALv4QUgzcHwcw5rcfx1hklEfoTE7a'
CLIENT_SECRET_FILE = 'client_secret.json'
TOKEN_FILE = 'token.json'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Analysis Configuration
SEARCH_TERM = '5GR1'
X_KEYWORDS = ['time elapsed', 'elapsed', 'run time', 'time (h)', 'time (hrs)', 'time']
Y_KEYWORDS = ['flux']
EXCLUDE_WORDS = ['date', 'install', 'prep', 'system', 'clock']

# Ensure string path for SQLite3 compatibility
DB_PATH_STR = str(DB_PATH)
