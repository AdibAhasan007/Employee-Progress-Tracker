import sqlite3

db_path = 'd:/Employee-Progress-Tracker/backend/db.sqlite3'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("🧹 Cleaning old data using raw SQL...")

sql_commands = [
    "DELETE FROM core_screenshot",
    "DELETE FROM core_applicationusage",
    "DELETE FROM core_websiteusage",
    "DELETE FROM core_activitylog",
    "DELETE FROM core_task",
    "DELETE FROM core_worksession",
    "DELETE FROM core_user WHERE role != 'OWNER'",
    "DELETE FROM core_companysettings",
]

for sql in sql_commands:
    cursor.execute(sql)
    print(f"  ✓ {sql}")

conn.commit()
conn.close()

print("\n✅ All old data cleaned successfully!")
print("🚀 Ready for multi-tenant migration")
