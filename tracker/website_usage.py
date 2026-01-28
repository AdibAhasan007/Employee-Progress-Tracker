import sqlite3
import config
from datetime import datetime, timezone

class WebsiteUsage:
    """
    Handles the storage of website usage data.
    Tracks which domains the employee visits and for how long.
    """
    def __init__(self, db_path=config.DB_PATH):
        self.db_path = db_path

    def save(self, company_id, employee_id, work_session_id, domain, active_seconds, url=None):
        """
        Save website usage data to the database.
        Thread-safe because each call opens a new SQLite connection.
        
        Args:
            company_id (int): The ID of the company.
            employee_id (int): The ID of the employee.
            work_session_id (int): The current work session ID.
            domain (str): The domain name of the website visited.
            active_seconds (int): Duration spent on this domain.
            url (str): Full URL path including query parameters (optional).
        """
        created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        try:
            cur = conn.cursor()
            # Try to insert with URL, fallback if column doesn't exist
            try:
                cur.execute("""
                    INSERT INTO website_usages
                    (company_id, employee_id, work_session_id, domain, url, active_seconds, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    company_id, employee_id, work_session_id,
                    domain, url, active_seconds, created_at
                ))
            except Exception:
                cur.execute("""
                    INSERT INTO website_usages
                    (company_id, employee_id, work_session_id, domain, active_seconds, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    company_id, employee_id, work_session_id,
                    domain, active_seconds, created_at
                ))
            conn.commit()
        except Exception as e:
            print("WebsiteUsage save error:", e)
        finally:
            conn.close()
