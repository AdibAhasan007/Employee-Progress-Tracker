import sqlite3
import os

db_path = r"C:\Users\prant\Employee Progress Tracker\hrsoftbdTracker.db"
if not os.path.exists(db_path):
    print(f"Database not found: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get current config
cursor.execute("SELECT employee_id, active_token FROM config WHERE id=1")
result = cursor.fetchone()
if result:
    print(f"Current config:")
    print(f"  employee_id: {result[0]}")
    print(f"  active_token: {result[1][:20] if result[1] else 'None'}...")
    
    # Update to employee_id=25 (adib@gmail.com)
    print(f"\n✅ Updating employee_id to 25 (adib@gmail.com)...")
    cursor.execute("UPDATE config SET employee_id=25 WHERE id=1")
    conn.commit()
    
    # Verify
    cursor.execute("SELECT employee_id FROM config WHERE id=1")
    new_id = cursor.fetchone()[0]
    print(f"✅ Updated! New employee_id: {new_id}")
else:
    print("No config found")

conn.close()
