"""
scripts/init-db.py
Run once from the project root to initialize kirana.db from schema.sql.
Usage: python scripts/init-db.py
"""
import sqlite3
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH     = os.path.join(ROOT, "kirana.db")
SCHEMA_PATH = os.path.join(ROOT, "db", "schema.sql")

def main():
    print(f"Initializing database at: {DB_PATH}")
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = f.read()
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(schema)
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    main()
