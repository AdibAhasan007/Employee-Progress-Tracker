import sqlite3

db_path = 'd:/Employee-Progress-Tracker/backend/db.sqlite3'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check schema for tables with company FK
tables = ['core_activitylog', 'core_applicationusage', 'core_websiteusage', 'core_screenshot']

for table in tables:
    print(f"\n{table}:")
    cursor.execute(f"PRAGMA table_info({table})")
    for row in cursor.fetchall():
        col_id, name, col_type, notnull, default, pk = row
        if 'company' in name.lower():
            nullable = "NULL" if notnull == 0 else "NOT NULL"
            print(f"  {name}: {col_type} {nullable}")

conn.close()
