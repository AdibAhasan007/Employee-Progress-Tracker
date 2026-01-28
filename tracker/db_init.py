import sqlite3
import config

def init_db():
    """
    Initializes the local SQLite database.
    Creates all necessary tables if they do not already exist.
    This function is called at application startup.
    """
    conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
    try:
        cur = conn.cursor()

        # ----------------------
        # Employee table
        # Stores the currently logged-in employee's details and daily stats.
        # ----------------------
        cur.execute("""
            CREATE TABLE IF NOT EXISTS employee (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT,
                company_id INTEGER,
                active_token TEXT,
                toddays_worked_time TEXT,
                toddays_active_time TEXT,
                toddays_inactive_time TEXT,
                task_note TEXT
            )
        """)

        # ----------------------
        # Application usage
        # Stores records of applications used by the employee.
        # ----------------------
        cur.execute("""
            CREATE TABLE IF NOT EXISTS application_usages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                employee_id INTEGER,
                work_session_id INTEGER,
                app_name TEXT,
                window_title TEXT,
                active_seconds INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ----------------------
        # Website usage
        # Stores records of websites visited by the employee.
        # ----------------------
        cur.execute("""
            CREATE TABLE IF NOT EXISTS website_usages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                employee_id INTEGER,
                work_session_id INTEGER,
                domain TEXT,
                active_seconds INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ----------------------
        # Employee activity logs
        # Stores granular activity logs (active/inactive minutes).
        # ----------------------
        cur.execute("""
            CREATE TABLE IF NOT EXISTS employee_activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                employee_id INTEGER,
                work_session_id INTEGER,
                minute_type TEXT,
                duration_seconds INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ----------------------
        # Screenshots table
        # Stores metadata about captured screenshots.
        # 'uploaded' flag tracks if the image has been sent to the server.
        # ----------------------
        cur.execute("""
            CREATE TABLE IF NOT EXISTS screenshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER,
                work_session_id INTEGER,
                photo_path TEXT,
                company_id INTEGER,
                capture_time TEXT,
                uploaded INTEGER DEFAULT 0
            )
        """)
        
        # ----------------------
        # Worksession table
        # Stores start and end times of work sessions.
        # ----------------------
        cur.execute("""
            CREATE TABLE IF NOT EXISTS work_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_api_id INTEGER,
                employee_id INTEGER,
                start_time TEXT,
                end_time TEXT
            )
        """)

        conn.commit()
        print("[DB INIT] All tables created successfully.")
    finally:
        conn.close()

# Optional: run directly for testing
if __name__ == "__main__":
    init_db()
