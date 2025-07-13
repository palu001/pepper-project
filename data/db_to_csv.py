import sqlite3
import pandas as pd
import os

def export_db_to_csv(db_path, export_dir):
    """
    Exports all tables from a SQLite database to separate CSV files.

    Parameters:
    - db_path (str): Full path to the SQLite .db file.
    - export_dir (str): Directory where CSV files will be saved.
    """
    # Ensure export directory exists
    os.makedirs(export_dir, exist_ok=True)

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    # Export each table to a CSV file
    for table_name in tables:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        csv_path = os.path.join(export_dir, f"{table_name}.csv")
        df.to_csv(csv_path, index=False)
        print(f"Exported: {table_name} -> {csv_path}")

    # Close the connection
    conn.close()

db_path = ("cinema.db")
csv_output_dir = ("csv_exports")

export_db_to_csv(db_path, csv_output_dir)
