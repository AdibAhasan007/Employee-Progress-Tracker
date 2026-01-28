import sqlite3
import config

class ActivityLog:
    """
    Handles the storage of employee activity logs.
    Used to track active vs inactive time segments.
    """
    def __init__(self, db_path=config.DB_PATH):
        self.db_path = db_path

    def save(self, company_id, employee_id, work_session_id, minute_type, duration_seconds):
        """
        Saves a single activity log entry to the database.
        
        Args:
            company_id (int): The ID of the company.
            employee_id (int): The ID of the employee.
            work_session_id (int): The current work session ID.
            minute_type (str): Type of activity (e.g., "ACTIVE", "INACTIVE").
            duration_seconds (int): Duration of this activity segment.
        """
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO employee_activity_logs
                (company_id, employee_id, work_session_id, minute_type, duration_seconds)
                VALUES (?, ?, ?, ?, ?)
            """, (
                company_id, employee_id, work_session_id,
                minute_type, duration_seconds
            ))
            conn.commit()
        finally:
            conn.close()
