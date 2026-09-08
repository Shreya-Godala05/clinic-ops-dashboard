"""
build_db.py
------------
Loads the generated CSVs into a single SQLite database (clinic.db)
so the dashboard and analysis queries can use real SQL joins,
just like you would against a production database.
"""

import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "clinic.db"


def main():
    conn = sqlite3.connect(DB_PATH)

    tables = {
        "patients": "patients.csv",
        "appointments": "appointments.csv",
        "billing": "billing.csv",
        "feedback": "feedback.csv",
    }

    for table_name, filename in tables.items():
        df = pd.read_csv(DATA_DIR / filename)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f"Loaded {len(df)} rows into '{table_name}'")

    conn.commit()
    conn.close()
    print(f"\nDatabase ready at {DB_PATH}")


if __name__ == "__main__":
    main()