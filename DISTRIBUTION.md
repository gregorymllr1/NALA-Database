# Distribution Checklist

This document outlines how to properly distribute the NALA Database Scraper project to your team.

## Before Distribution

- [x] All paths refactored to use `config.py` (relative paths)
- [x] `requirements.txt` created with all dependencies
- [x] `.gitignore` updated to include `nala_rd_data.db` (tracked) and exclude credentials
- [x] Comprehensive README.md with quick start guide
- [x] SETUP_FOR_TEAM.md with detailed team onboarding
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
2. **Follow SETUP_FOR_TEAM.md** - Complete setup instructions
3. **Verify installation** - Run test commands
4. **Complete Google Drive setup** - Set up personal Google OAuth credentials
5. **Start working** - Extract, ingest, and analyze data

## Key Files to Distribute

| File | Purpose | Include | Notes |
|------|---------|---------|-------|
| `*.py` | Main scripts | ✓ | Core functionality |
| `requirements.txt` | Dependencies | ✓ | Install with `pip install -r requirements.txt` |
| `config.py` | Configuration | ✓ | Centralized paths and settings |
| `nala_rd_data.db` | Database | ✓ | Team shared database |
| `*.json` (credentials) | Auth files | ✗ | Each member creates their own |
| `.venv/` | Virtual env | ✗ | Each member creates with `python -m venv .venv` |
| `data/` | Downloaded files | ✗ | Local to each member |
| `.git/` | Version control | ~ | Include only if using Git distribution |

## Post-Distribution Workflow

### First Time Setup
```bash
git clone <repo>
cd NALA-Database
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
# Follow SETUP_FOR_TEAM.md for Google Drive auth
```

### Regular Workflow
```bash
# Get latest database
git pull

# Extract new data
python Extraction.py

# Ingest into database
python ingestion.py

# Analyze and visualize
python analysis.py

# Share updates with team
git add nala_rd_data.db
git commit -m "Updated database with latest data"
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
- This is expected! Each member creates their own `client_secret.json` and `token.json`
- These are in `.gitignore` and not shared
- See SETUP_FOR_TEAM.md step 2 for Google Drive setup

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

1. **Documentation**: README.md and SETUP_FOR_TEAM.md
2. **Code comments**: Docstrings in each .py file
3. **Config centralization**: All paths in config.py
4. **Database sharing**: nala_rd_data.db in version control

For questions during setup, team members should:
- Check README.md first
- Check SETUP_FOR_TEAM.md troubleshooting section
- Contact project lead for Google Drive folder access issues
