import sqlite3
import base64
import requests
import os
from pathlib import Path

# Database path
db_path = Path.home() / "Employee Progress Tracker" / "hrsoftbdTracker.db"
conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

# Get active token
cur.execute("SELECT active_token FROM employee LIMIT 1")
token = cur.fetchone()[0]

# Upload up to 5 screenshots
cur.execute("""
SELECT id, employee_id, company_id, work_session_id, photo_path, capture_time
FROM screenshots
WHERE uploaded=0
ORDER BY id
LIMIT 5
""")

API_URL = "http://127.0.0.1:8000/api"

uploaded_count = 0
for row in cur.fetchall():
    local_id, emp_id, comp_id, sess_id, photo_path, capture_time = row
    
    if not os.path.exists(photo_path):
        print(f"❌ File missing: {photo_path}")
        continue
    
    # Encode image
    with open(photo_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    
    # Upload
    payload = {
        "employee_id": emp_id,
        "company_id": comp_id,
        "work_session_id": sess_id,
        "capture_time": capture_time,
        "photo": encoded,
        "active_token": token,
    }
    
    try:
        resp = requests.post(f"{API_URL}/screenshot/upload", json=payload, timeout=30)
        if resp.status_code == 200:
            # Mark as uploaded
            cur.execute("UPDATE screenshots SET uploaded=1 WHERE id=?", (local_id,))
            conn.commit()
            uploaded_count += 1
            print(f"✅ Uploaded screenshot {local_id}")
        else:
            print(f"❌ Failed {local_id}: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ Error uploading {local_id}: {e}")

print(f"\n✅ Uploaded {uploaded_count} screenshots")

# Check remaining
cur.execute("SELECT COUNT(*) FROM screenshots WHERE uploaded=0")
remaining = cur.fetchone()[0]
print(f"📊 Remaining: {remaining} screenshots")

conn.close()
