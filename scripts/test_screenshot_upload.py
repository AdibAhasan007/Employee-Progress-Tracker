import sqlite3
import base64
import os
import sys
from pathlib import Path

# Add tracker to path
sys.path.insert(0, r'd:\Employee-Progress-Tracker\tracker')

from api_helper import api_post
import config

# Connect to database
db_path = Path.home() / "Employee Progress Tracker" / "hrsoftbdTracker.db"
conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

# Get active token
cur.execute("SELECT active_token FROM employee LIMIT 1")
token_row = cur.fetchone()
active_token = token_row[0] if token_row else None

if not active_token:
    print("ERROR: No active token found!")
    sys.exit(1)

# Get one screenshot to test
cur.execute("SELECT id, employee_id, company_id, work_session_id, photo_path, capture_time FROM screenshots WHERE uploaded=0 LIMIT 1")
row = cur.fetchone()

if not row:
    print("No pending screenshots found!")
    sys.exit(0)

local_id, emp_id, comp_id, sess_id, photo_path, capture_time = row

print(f"Testing upload for screenshot ID {local_id}")
print(f"Employee: {emp_id}, Company: {comp_id}, Session: {sess_id}")
print(f"Path: {photo_path}")

if not os.path.exists(photo_path):
    print(f"ERROR: File does not exist!")
    sys.exit(1)

# Encode image
with open(photo_path, "rb") as img_file:
    encoded = base64.b64encode(img_file.read()).decode()

print(f"Image size: {len(encoded)} bytes (base64)")

# Prepare payload
payload = {
    "employee_id": emp_id,
    "company_id": comp_id,
    "work_session_id": sess_id,
    "capture_time": capture_time,
    "photo": encoded,
    "active_token": active_token,
}

print(f"\nUploading to: {config.API_URL}/screenshot/upload")

try:
    res = api_post("/screenshot/upload", json_data=payload, timeout=30)
    print(f"\nResponse status: {res.status_code}")
    print(f"Response body: {res.text[:500]}")
    
    if res.status_code == 200:
        data = res.json()
        if data.get("status"):
            print("\n✅ Upload successful!")
        else:
            print(f"\n❌ Upload failed: {data.get('message')}")
    else:
        print(f"\n❌ HTTP Error: {res.status_code}")
        
except Exception as e:
    print(f"\n❌ Exception: {e}")
    import traceback
    traceback.print_exc()

conn.close()
