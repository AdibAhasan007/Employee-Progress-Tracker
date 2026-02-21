import sqlite3
import os
from pathlib import Path

# Connect to database
db_path = Path.home() / "Employee Progress Tracker" / "hrsoftbdTracker.db"
conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

# Check active token
cur.execute("SELECT active_token FROM employee LIMIT 1")
token_row = cur.fetchone()
active_token = token_row[0] if token_row else None

print(f"Active token exists: {bool(active_token)}")
if active_token:
    print(f"Token (first 20 chars): {active_token[:20]}...")

# Check screenshots pending upload
cur.execute("SELECT COUNT(*) FROM screenshots WHERE uploaded=0")
pending = cur.fetchone()[0]
print(f"\nPending screenshots: {pending}")

# Get sample screenshot info
cur.execute("SELECT id, employee_id, company_id, work_session_id, photo_path FROM screenshots WHERE uploaded=0 LIMIT 1")
sample = cur.fetchone()

if sample:
    print(f"\nSample screenshot:")
    print(f"  ID: {sample[0]}")
    print(f"  Employee ID: {sample[1]}")
    print(f"  Company ID: {sample[2]}")
    print(f"  Session ID: {sample[3]}")
    print(f"  Path: {sample[4]}")
    print(f"  File exists: {os.path.exists(sample[4])}")

conn.close()
