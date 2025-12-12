"""
Offline SQLite storage
"""
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = "scans.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_path TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_scan(image_path: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO scans (image_path, timestamp) VALUES (?, ?)",
        (image_path, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

