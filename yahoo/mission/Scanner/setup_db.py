"""
Setup database for simplified scanner.
Creates scans.db with scans table.
"""
import sqlite3

# Connect or create the SQLite DB file
conn = sqlite3.connect("scans.db")
cursor = conn.cursor()

# Create table for storing scan records
cursor.execute("""
CREATE TABLE IF NOT EXISTS scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_path TEXT NOT NULL,
    timestamp TEXT NOT NULL
);
""")

conn.commit()
conn.close()

print("✅ Database created successfully.")


