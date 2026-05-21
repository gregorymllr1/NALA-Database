# NALA Database Schema Overview

## 1. Database Structure

**Database File:** `nala_rd_data.db` (SQLite)
**Size:** ~70 MB
**Tables:** 10,436
**Workbooks/Sources:** 392 unique Excel files

## 2. Table Naming Convention

### Format
Tables follow the pattern created by `sanitize_table_name()` in `ingestion.py`:
```
{WORKBOOK_ID}_{SHEET_NAME}
```

### Components

**WORKBOOK_ID:**
- Extracted from Excel filename
- Examples: `A12386`, `A12387`, `AL1`, empty string for some legacy files
- Can start with alphanumeric characters, numbers prefixed with `tbl_`

**SHEET_NAME:**
- Taken directly from Excel tab/sheet name
- Examples: `Performance_calc_sheet_Data_Calcs`, `Baseline_Performance_Calculation_Data_Calcs`
- Sanitized: special characters replaced with underscores

### Examples
- `A12386_Performance_calc_sheet_Data_Calcs` = Excel file "A12386" + tab "Performance_calc_sheet_Data_Calcs"
- `A12402___Flatsheet_from_element_on_crossflow_Cell_1` = Excel file "A12402" + tab "Flatsheet_from_element_on_crossflow_Cell_1"

## 3. Data Source Tracking

### How Source is Tracked
**Method:** Implicit in table name (workbook_sheet)

**Origin Chain:**
1. Google Drive Folder (ID: `1x6_ALv4QUgzcHwcw5rcfx1hklEfoTE7a`)
2. Downloaded as Excel files (.xlsx) by `Extraction.py`
3. Each Excel file processed by `ingestion.py`
4. Each sheet in the Excel file becomes a separate table

### NO Explicit "Source" or "Type" Column
- No dedicated column tracks which spreadsheet the data came from
- No timestamp column indicates when data was scraped
- Source information is completely implicit in the table name

## 4. Column Headers & Schema

### Column Header Handling
- Headers are read directly from Excel files (first row)
- Missing headers become: `Unnamed: 0`, `Unnamed: 1`, etc.
- **NO normalization or mapping is applied**
- All column names are preserved exactly as they appear in the original spreadsheet

### Data Type Storage
- All columns stored as TEXT type (SQLite default when using pandas `to_sql()`)
- No schema constraints or type validation at database level
- Numeric values stored as strings, requiring conversion during analysis

### Unique Columns Identified
From 100 random tables sampled, ~99 unique column names found across all tables:
- `Serial #`, `Cell #`, `SAMPLE`, `Notes`, `SR%`, `Flux (LMH)`, etc.
- Many columns with timestamps: `2023-07-17 01:30:00`, `2025-04-30 14:44:59.712000`
- Columns with revision info: `Sheet Revision Date: 05/20/2025 (Maggie)`
- Many unnamed columns due to missing headers in source spreadsheets

## 5. Entity Types

Entity types are identified by keywords in table names (not explicit columns):

| Entity Type  | Count | Tracking Method |
|-------------|-------|-----------------|
| Cell        | 7,714 | "Cell_N" in table name |
| Element     | 29    | "Element" in table name |
| Membrane    | 14    | "Membrane" in table name |
| Flatsheet   | 8     | "Flatsheet" in table name |
| Crossflow   | 0     | "crossflow" in table name |

**Note:** Entity types are part of the sheet name, not database columns. No "type" or "entity" column exists.

### Examples
- `A12402___Flatsheet_from_element_on_crossflow_Cell_1` → Cell #1, Element-based
- `A13639__Element_Log_Data_Calcs` → Element-focused data
- `AL1_Cell_Acet__0104_A_Master_Calc_Sheet` → Cell A, Acetate membrane

## 6. Sheet Name Patterns

### Most Common Sheet Names
- **227 tables:** `Sheet1` (default Excel sheet name)
- **24 tables:** `__Baseline_Performance_Calculation_Data_Calcs`
- **20 tables:** `__Performance_Calculation_Data_Calcs`
- **13 tables:** `_Performance_Calculation_Data_Calcs`
- **12 tables:** `_Baseline_Performance_Calculation_Data_Calcs`

These patterns indicate:
- Many workbooks have multiple performance-related sheets
- Baseline vs. post-treatment comparisons are common
- Standardized naming conventions for calculation sheets

## 7. Workbook Statistics

| Metric | Value |
|--------|-------|
| Total Workbooks | 392 |
| Total Tables | 10,436 |
| Avg Sheets/Workbook | 26.6 |
| Max Sheets/Workbook | 290 (largest workbook) |
| Most Common Workbook | Empty string prefix (290 tables) |

## 8. Data Ingestion Pipeline

### Flow
```
Google Drive Sheets
    ↓ (Extraction.py)
Download as .xlsx files
    ↓ (Stored in data/ directory)
Read all sheets with pandas
    ↓ (ingestion.py)
For each sheet:
  - Create table name: sanitize(workbook_filename + "_" + sheet_name)
  - Store headers exactly as-is in Excel
  - Replace NULL columns with TEXT
  - Write to SQLite with df.to_sql(if_exists='replace')
    ↓
nala_rd_data.db (10,436 tables)
```

### Key Details
- **No header normalization** - columns are raw from Excel
- **No missing header handling** - unnamed columns become `Unnamed: N`
- **Overwrites on re-ingestion** - `if_exists='replace'` mode
- **No metadata tracking** - source info is table name only

## 9. Column Normalization Logic

### Current Behavior
**NONE.** The system does NOT normalize or map column headers.

### What This Means
- Different spreadsheets can have identical data under different column names
- "Time (h)" vs "time elapsed" vs "run time" are treated as different columns
- Column name variations must be handled at query/analysis time
- See `analysis.py` for example: `find_column()` uses keyword matching

### Example from analysis.py
```python
def find_column(df, keywords):
    for keyword in keywords:
        for col in df.columns:
            col_str = str(col).lower()
            if keyword.lower() in col_str:
                return col
    return None

# Usage:
X_KEYWORDS = ['time elapsed', 'elapsed', 'run time', 'time (h)', 'time']
Y_KEYWORDS = ['flux']
time_col = find_column(df, X_KEYWORDS)  # Fuzzy matching, not exact
```

## 10. Data Access Patterns

### For Analysis
- Query by table name (workbook_sheet pattern)
- Fuzzy column matching (keyword search) since names vary
- Type conversion needed (TEXT to numeric)
- Filter by search term (e.g., "5GR1" for experiment search)

### For Reporting
- Identify tables containing specific keywords (e.g., "Element", "Cell")
- Extract data from multiple related tables
- Perform cross-spreadsheet comparisons

## 11. Metadata Not Stored

The database does NOT include:
- ❌ Source spreadsheet ID or name (implicit in table name only)
- ❌ Timestamp of when data was scraped
- ❌ User who created or modified data
- ❌ Data quality flags or validation status
- ❌ Column header standardization or mapping
- ❌ Row-level lineage or version history
- ❌ Explicit "type" or "entity_type" columns

## 12. Distinguishing Entity Types

Currently, entity types (elements vs membranes vs cells) are distinguished by:
- **Keywords in table names:** "Element", "Cell", "Membrane", etc.
- **Keywords in sheet names:** "(Cell_1)", "(Element Log)"
- **No database columns** explicitly track entity type

### How to Add Tracking
To properly track entity types, add metadata:
1. Create a lookup table mapping table_name → entity_type
2. Or add a "source_sheet" and "entity_type" column to all tables
3. Or embed structured metadata in table creation process

## 13. Practical Usage Notes

### To Find All "Element" Data
```sql
SELECT name FROM sqlite_master 
WHERE type='table' AND name LIKE '%Element%'
```

### To Query a Specific Experiment
```sql
SELECT * FROM 'A12386_Performance_calc_sheet_Data_Calcs'
LIMIT 10
```

### Column Header Discovery
```sql
PRAGMA table_info('table_name');  -- See all column names for a table
```

### To Identify Data Source
Look at the table name prefix (workbook ID) and remaining text (sheet name).
No SQL query can retrieve original file metadata—it's implicit only.
