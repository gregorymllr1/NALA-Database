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
