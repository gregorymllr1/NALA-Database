# Distribution Checklist

This document outlines how to properly distribute the NALA Database Scraper project to your team.

## Key Concept

- **Regular team members**: Use the dashboard to query data
- **Master/Maintainer (you)**: Keep database updated with new weekly R&D data
- **Database file**: Distributed with project, shared via Git

## Before Distribution

- [x] All paths refactored to use `config.py` (relative paths)
- [x] `requirements.txt` created with all dependencies
- [x] `.gitignore` updated to include `nala_rd_data.db` (tracked) and exclude credentials
- [x] Comprehensive README.md with quick start guide
- [x] SETUP_FOR_TEAM.md with dashboard setup (simple, 5 minutes)
- [x] MAINTAINER.md with extraction/ingestion guide (for you only)
- [x] Database file `nala_rd_data.db` committed to Git
- [x] Sensitive credentials excluded from Git (.gitignore)

## How to Distribute

### Option 1: Git Repository (Recommended for Team)

```bash
# Ensure everything is committed
git status

# Create a public or private repository (GitHub, GitLab, etc.)
git remote add origin <your-repo-url>

# Push everything to the repository
git branch -M main
git push -u origin main
```

Team members then clone with:
```bash
git clone <repository-url>
```

### Option 2: ZIP Archive

```bash
# Create a clean distribution archive (excludes .git)
git archive --format zip --output NALA-Database-Distribution.zip HEAD

# Or manually zip excluding .git and __pycache__:
# Include: all .py files, .html, requirements.txt, README.md, SETUP_FOR_TEAM.md, nala_rd_data.db
# Exclude: .git, __pycache__, *.pyc, .venv, venv
```

## Team Member Onboarding

After cloning/extracting, each team member should:

1. **Read README.md** - Project overview and quick start
2. **Follow SETUP_FOR_TEAM.md** - 5-minute setup to use dashboard
3. **Open dashboard.html** - Start querying R&D data

That's it! Regular team members don't need Python knowledge or Google Drive setup.

## Key Files to Distribute

| File | Purpose | Include | Notes |
|------|---------|---------|-------|
| `dashboard.html` | Interactive UI | ✓ | What users interact with |
| `analysis.py` | Analysis tools | ✓ | Maintainer uses this |
| `Extraction.py` | Google Drive access | ✓ | Maintainer only |
| `ingestion.py` | Database updates | ✓ | Maintainer only |
| `requirements.txt` | Dependencies | ✓ | Install with `pip install -r requirements.txt` |
| `config.py` | Configuration | ✓ | Centralized paths and settings |
| `nala_rd_data.db` | Database | ✓ | Team shared database |
| `*.json` (credentials) | Auth files | ✗ | Maintainer only |
| `.venv/` | Virtual env | ✗ | Each member creates with `python -m venv .venv` |
| `data/` | Downloaded files | ✗ | Local to maintainer only |
| `.git/` | Version control | ~ | Include only if using Git distribution |

## Post-Distribution Workflow

### First Time Setup - Regular Team Members
```bash
git clone <repo>
cd NALA-Database
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
start dashboard.html  # Windows - Open dashboard to query data
```

### First Time Setup - Maintainer (You)
```bash
git clone <repo>
cd NALA-Database
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
# Follow MAINTAINER.md for Google Drive setup
```

### Team Member Regular Workflow
```bash
# When maintainer pushes new data, pull to update
git pull

# Refresh dashboard.html in browser to see new data
start dashboard.html  # Use dashboard to query data
```

### Maintainer (You) Regular Workflow
```bash
# Weekly: When new R&D data arrives, extract it
git pull
python Extraction.py

# Ingest the new data into the database
python ingestion.py

# Share updated database with team
git add nala_rd_data.db
git commit -m "Updated database: Added Q2 2026 fouling tests"
git push
```

## Troubleshooting Distribution Issues

### Issue: "ModuleNotFoundError" after installation
**Solution**: 
- Verify virtual environment is activated
- Run `pip install -r requirements.txt` again

### Issue: Database locked or corrupted
**Solution**:
- Get fresh copy from Git: `git checkout nala_rd_data.db`
- Ensure no other Python processes using the database

### Issue: Team members have different database states
**Solution**:
- Regularly commit database updates: `git add nala_rd_data.db && git commit -m "..."`
- Team members pull: `git pull` before and after data work

### Issue: Each member needs different credentials
**Solution**:
- This is NOT expected for regular team members! They don't need credentials.
- Only maintainer needs `client_secret.json` and `token.json`
- These are in `.gitignore` and not shared
- See MAINTAINER.md for credential setup

## Version Control Best Practices

```bash
# Commit database updates with meaningful messages
git add nala_rd_data.db
git commit -m "Added Q2 2026 test data for membrane performance"

# Pull before starting work to get latest data
git pull

# Push updates regularly so team stays synchronized
git push
```

## Support for Distributed Team

1. **For regular team members**: README.md and SETUP_FOR_TEAM.md (5 min setup)
2. **For maintainer**: MAINTAINER.md (detailed extraction/ingestion guide)
3. **Config centralization**: All paths in config.py
