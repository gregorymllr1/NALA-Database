# NALA R&D Database Scraper & Dashboard 📊

A centralized Python application for managing, updating, and querying NALA Research & Development data. This project features an automated ETL (Extract, Transform, Load) pipeline for ingesting weekly R&D data into a distributed SQLite database, paired with an interactive web dashboard for easy team access.

## 📑 Quick Overview

* **Dashboard (All Users):** An interactive web interface to query and visualize current R&D data.
* **Database (Included):** A pre-built, version-controlled SQLite database (`nala_rd_data.db`) containing all ingested historical data.
* **Extraction & Ingestion (Maintainer Only):** Automated scripts to pull new weekly R&D data from Google Drive and update the database.

---

## 👥 For Regular Team Members

If you are here to view and query the R&D data, follow these steps. The database is already built and included in the repository.

### Quick Start (5 Minutes)

**1. Clone the repository**
```bash
git clone <repository-url>
cd "NALA-Database"
python -m venv .venv

# Windows:
.venv\Scripts\activate

# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
# Windows:
start dashboard.html  

# macOS:
open dashboard.html

##🛠️ For Database Maintainers
Only execute these steps if you are responsible for updating the central R&D database.

When new weekly data arrives on Google Drive, you must update the database and push the changes to the team.

Automated Update (Recommended)
This master script runs the extraction, ingestion, and Git workflow (add, commit, push) in one step.

# Windows:
.venv\Scripts\python.exe weekly_update.py

# macOS/Linux (ensure venv is activated):
python weekly_update.py

# 1. Extract Excel files from Google Drive
python Extraction.py

# 2. Ingest downloaded files into the database
python ingestion.py

# 3. Commit the updated database to share with the team
git add nala_rd_data.db
git commit -m "Updated database: [Brief description of new data]"
git push

.
├── nala_rd_data.db          # ✓ Main SQLite database (distributed with project)
├── dashboard.html           # ✓ Web dashboard for data queries
├── requirements.txt         # ✓ Python dependencies
├── config.py                # ✓ Centralized environment variables and paths
├── README.md                # ✓ Core documentation
│
├── Extraction.py            # [Maintainer] Download pipeline from Google Drive
├── ingestion.py             # [Maintainer] Database update script
├── analysis.py              # [Maintainer] Report generation script
├── weekly_update.py         # [Maintainer] Automated ETL master script
├── MAINTAINER.md            # [Maintainer] Detailed administrative instructions
│
└── Data Directories         # (Auto-created during ETL, not tracked by git)
    ├── data/                # Downloaded raw Excel files
    ├── archived_data/       # Processed Excel files
    └── archived_rd_csvs/    # CSV backups

##🐛 Troubleshooting
Issue: ModuleNotFoundError when attempting to run the dashboard or scripts.
Solution: Your virtual environment is likely deactivated or missing packages.

# Reactivate the environment
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # macOS/Linux

# Reinstall requirements
pip install -r requirements.txt

