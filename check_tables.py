import sqlite3

db_path = r"C:\Users\prant\Employee Progress Tracker\hrsoftbdTracker.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# List tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("=== Tables ===")
for table in tables:
    print(f"  - {table[0]}")

# Check screenshots table
print("\n=== Screenshots ===")
cursor.execute("SELECT employee_id, work_session_id, COUNT(*) FROM screenshots WHERE uploaded=0 GROUP BY employee_id, work_session_id")
for row in cursor.fetchall():
    print(f"  Employee: {row[0]}, Session: {row[1]}, Count: {row[2]}")

conn.close()
