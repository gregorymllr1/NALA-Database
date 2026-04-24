import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
from config import DB_PATH_STR, SEARCH_TERM, X_KEYWORDS, Y_KEYWORDS, EXCLUDE_WORDS

def find_column(df, keywords):
    for keyword in keywords:
        for col in df.columns:
            if pd.isna(col): 
                continue
            col_str = str(col).lower()
            if keyword.lower() in col_str:
                if not any(bad_word in col_str for bad_word in EXCLUDE_WORDS):
                    return col
    return None

def extract_number(value):
    val_str = str(value)
    match = re.search(r'([-+]?\d*\.?\d+)', val_str)
    if match:
        return float(match.group(1))
    return None
    return pd.NA 

def format_legend_label(raw_name):
    """Cleans up the raw SQLite table name for a professional plot legend."""
    # 1. Remove the 'tbl_' prefix if we added it during ingestion
    clean_name = raw_name.replace('tbl_', '')
    
    # 2. THE FIX: Strip leading underscores so matplotlib doesn't hide the entry!
    clean_name = clean_name.lstrip('_')
    
    # 3. Replace remaining underscores with spaces for human readability
    clean_name = clean_name.replace('_', ' ')
    
    # 4. Truncate nicely if the filename is incredibly long
    return clean_name[:45] + '...' if len(clean_name) > 45 else clean_name

def query_and_plot():
    conn = sqlite3.connect(DB_PATH_STR)
    
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    all_tables = pd.read_sql(query, conn)['name'].tolist()
    matched_tables = [t for t in all_tables if SEARCH_TERM.lower() in t.lower()]
    
    if not matched_tables:
        print(f"No tables found for: '{SEARCH_TERM}'")
        conn.close()
        return
        
    print(f"Found {len(matched_tables)} experiments containing '{SEARCH_TERM}'.\n")

    plt.figure(figsize=(12, 7))
    sns.set_style("whitegrid")
    plot_success = False

    for table_name in matched_tables:
        try:
            df = pd.read_sql(f"SELECT * FROM '{table_name}'", conn)
            
            # Transpose the DataFrame
            first_col = df.columns[0]
            df.set_index(first_col, inplace=True)
            df = df.T 
            
            time_col = find_column(df, X_KEYWORDS)
            flux_col = find_column(df, Y_KEYWORDS)
            
            if time_col and flux_col:
                # Clean the data
                df[time_col] = df[time_col].apply(extract_number)
                df[flux_col] = df[flux_col].apply(extract_number)
                
                # Drop rows missing coordinates and sort
                plot_data = df.dropna(subset=[time_col, flux_col])
                plot_data = plot_data.sort_values(by=time_col)
                
                if not plot_data.empty:
                    # Pass the raw table name through our new formatter
                    legend_label = format_legend_label(table_name)
                    
                    plt.plot(
                        plot_data[time_col], 
                        plot_data[flux_col], 
                        marker='o', 
                        linestyle='-', 
                        label=legend_label 
                    )
                    plot_success = True
                
        except Exception as e:
            print(f"Error analyzing {table_name}: {e}\n")

    conn.close()

    if plot_success:
        plt.title(f"Performance for {SEARCH_TERM}", fontsize=16)
        plt.xlabel("Time Elapsed (h)", fontsize=12)
        plt.ylabel("Flux", fontsize=12)
        
        # We also added a title to the legend box to make it look cleaner
        plt.legend(title="Experiment Source", bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.show()
    else:
        print("\nCould not generate plot.")

if __name__ == '__main__':
    query_and_plot()