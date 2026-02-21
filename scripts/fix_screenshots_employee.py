import sqlite3

db_path = r"C:\Users\prant\Employee Progress Tracker\hrsoftbdTracker.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Update employee_id from 2 to 25
cursor.execute("UPDATE screenshots SET employee_id=25 WHERE employee_id IN (2, 3)")
affected = cursor.rowcount
conn.commit()

print(f"✅ Updated {affected} screenshots")
print(f"   Changed employee_id: 2,3 → 25")

# Verify
cursor.execute("SELECT employee_id, COUNT(*) FROM screenshots WHERE uploaded=0 GROUP BY employee_id")
print("\n=== Pending Screenshots ===")
for row in cursor.fetchall():
    print(f"  Employee {row[0]}: {row[1]} screenshots")

conn.close()
