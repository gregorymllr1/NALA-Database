# NALA Database Project: Clarified Distribution Model

## Your Clarification - Now Implemented

You wanted to ensure that:
- ✅ **Database file** (`nala_rd_data.db`) is included and distributed with the project
- ✅ **Regular team members** can query the database via the dashboard (no extraction/ingestion needed)
- ✅ **Extraction.py and ingestion.py** are available for maintainer-only use
- ✅ **You** maintain the database by running extraction/ingestion weekly
- ✅ **Average user** only needs to open the dashboard and query existing data

## What's Been Set Up

### 📚 Documentation Updated

| Document | Audience | Purpose |
|----------|----------|---------|
| **README.md** | Everyone | Project overview; links to role-specific guides |
| **SETUP_FOR_TEAM.md** | Regular users | 5-minute setup: clone → install → open dashboard |
| **MAINTAINER.md** | You only | Detailed guide for extraction/ingestion/database maintenance |
| **DISTRIBUTION.md** | Team leads | How to distribute; clarifies role separation |

### 🎯 Two User Workflows

#### For Regular Team Members (Your R&D Colleagues)

**Setup (5 minutes):**
```bash
git clone <repository-url>
cd NALA-Database
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
start dashboard.html  # Open dashboard in browser
```

**Weekly Usage:**
- Open `dashboard.html` to query data
- When you notify them: `git pull` to get latest database
- Refresh browser to see new data
- Search experiments, view results

**What they DON'T need:**
- Google Drive credentials
- Knowledge of extraction/ingestion
- Database administration

#### For You (Database Maintainer)

**Setup (one-time):**
- Set up Google Cloud credentials (detailed in MAINTAINER.md)
- Create `client_secret.json`

**Weekly Workflow:**
```bash
# 1. Pull latest from team
git pull

# 2. Extract new data from Google Drive
python Extraction.py

# 3. Ingest into database
python ingestion.py

# 4. Share with team
git add nala_rd_data.db
git commit -m "Updated database: [description of new data]"
git push
```

**Your Responsibilities:**
- Monitor for new R&D data weekly
- Run extraction/ingestion process
- Commit database updates to Git
- Notify team when new data is available

### 📦 What Gets Distributed

When you share the project:

```
NALA-Database/
├── dashboard.html              👈 Users click this
├── nala_rd_data.db            ✅ Pre-built database (shared)
├── requirements.txt
├── README.md                   👈 Users read first
├── SETUP_FOR_TEAM.md          👈 Users follow this
├── MAINTAINER.md              👈 You use this
├── config.py                  ✅ Centralized config
├── Extraction.py              (You use weekly)
├── ingestion.py               (You use weekly)
├── analysis.py                (For reports)
└── [Other files]
```

### 🔐 Credentials Handling

| Credential File | Who Creates | Purpose | Shared? |
|-----------------|-------------|---------|---------|
| `client_secret.json` | You | Google OAuth credentials | ❌ NOT shared |
| `token.json` | You (auto-created) | Google authentication token | ❌ NOT shared |
| `nala_rd_data.db` | You (auto-updated) | Database file | ✅ Shared via Git |

Regular team members need **nothing**. Only you need credentials.

### 📁 File Organization for Clarity

**Files for Everyone:**
- `README.md` → Overview
- `SETUP_FOR_TEAM.md` → Setup instructions
- `dashboard.html` → The app users interact with
- `requirements.txt` → Dependencies to install
- `nala_rd_data.db` → The database (shared)

**Files for You (Maintainer):**
- `MAINTAINER.md` → Your comprehensive guide
- `Extraction.py` → Extract from Google Drive
- `ingestion.py` → Process and store data
- `analysis.py` → Generate reports
- `config.py` → Settings reference

**Hidden/Technical:**
- `client_secret.json` → Your Google credentials (gitignored)
- `token.json` → Your Google token (gitignored)
- `data/` directory → Downloaded files (gitignored)

## Distribution Steps

1. **Already done**: All code refactored for portability
2. **Already done**: Documentation created for both roles
3. **Your choice**: Git repository vs ZIP distribution
4. **Action**: Share repository URL or ZIP with your team

## Communication with Team

When distributing, you can say:

**For Designers/Analysts (Regular Users):**
> "Clone this repository and follow SETUP_FOR_TEAM.md (5 minutes). Then open `dashboard.html` to query all our R&D data. I'll keep the database updated weekly with new experiments."

**For Technical Users/Managers:**
> "This is our R&D data system. The database is included and maintained centrally. Regular users just open the dashboard to query data. I handle all data extraction and ingestion from Google Drive."

## Your Weekly Workflow

Every Friday (or as new data arrives):

```
1. Check if new data in Google Drive
   ↓
2. Run: python Extraction.py
   ↓
3. Run: python ingestion.py
   ↓
4. git add nala_rd_data.db
   git commit -m "Database update: [details]"
   git push
   ↓
5. Notify team: "New data available, run git pull"
```

That's it! Team members automatically get the new data when they pull.

## File Size Expectations

- Source code: ~50-100 KB
- Database (`nala_rd_data.db`): Depends on your data (likely MB to a few GB)
- Total: Fully contained, easily distributed

## Key Improvements Over Original Setup

| Before | Now |
|--------|-----|
| Hardcoded Windows paths | Relative paths that work anywhere |
| No clear roles | Clear separation: users vs maintainer |
| All users needed Google setup | Only maintainer needs Google credentials |
| No documentation | 4 comprehensive guides |
| Confusing workflows | Simple, role-based workflows |

## Next Steps

1. **Verify everything is ready:**
   ```bash
   git log --oneline -5  # See recent commits
   git status            # Should be clean
   ```

2. **Test the dashboard:**
   - Open `dashboard.html` in browser
   - Verify it loads with data

3. **Share with your team:**
   - Push to Git repository
   - Share the URL with team members
   - Direct them to `README.md` first

4. **Maintain going forward:**
   - Follow your weekly maintenance workflow
   - Keep database updated via Git
   - Reference `MAINTAINER.md` as needed

---

**Your project is now truly distributable!** Regular team members can be productive in 5 minutes with just the dashboard, while you maintain the database through a simple weekly process.
