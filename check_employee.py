import sqlite3

db_path = r"C:\Users\prant\Employee Progress Tracker\hrsoftbdTracker.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check employee table
print("=== Employee Table ===")
cursor.execute("SELECT * FROM employee")
employees = cursor.fetchall()

# Get column names
cursor.execute("PRAGMA table_info(employee)")
columns = [col[1] for col in cursor.fetchall()]
print(f"Columns: {', '.join(columns)}\n")

for emp in employees:
    data = dict(zip(columns, emp))
    print(f"ID: {data.get('id', 'N/A')}")
    print(f"  employee_id: {data.get('employee_id', 'N/A')}")
    print(f"  company_id: {data.get('company_id', 'N/A')}")
    print(f"  active_token: {data.get('active_token', 'None')[:20] if data.get('active_token') else 'None'}...")
    print()

conn.close()
