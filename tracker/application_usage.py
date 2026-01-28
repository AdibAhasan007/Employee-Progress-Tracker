import sqlite3
import config

class ApplicationUsage:
    """
    Handles the storage of application usage data.
    Tracks which desktop applications the employee uses and for how long.
    """
    def __init__(self, db_path=config.DB_PATH):
        self.db_path = db_path

    def save(self, company_id, employee_id, work_session_id, app_name, window_title, active_seconds):
        """
        Save application usage data to the database.
        Thread-safe because each call opens a new SQLite connection.
        
        Args:
            company_id (int): The ID of the company.
            employee_id (int): The ID of the employee.
            work_session_id (int): The current work session ID.
            app_name (str): The name of the application (e.g., "Code").
            window_title (str): The full title of the window.
            active_seconds (int): Duration spent on this application.
        """
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO application_usages
                (company_id, employee_id, work_session_id, app_name, window_title, active_seconds)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                company_id, employee_id, work_session_id,
                app_name, window_title, active_seconds
            ))
            conn.commit()
        finally:
            conn.close()
