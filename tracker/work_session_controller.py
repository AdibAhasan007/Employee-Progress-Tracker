import requests
import sqlite3
from datetime import datetime, timezone
import config

class WorkSessionController:
    """
    Manages the start and stop of work sessions.
    Communicates with the API to log session times and updates the local database.
    """
    def __init__(self):
        self.db = sqlite3.connect(config.DB_PATH)
        self.cursor = self.db.cursor()

    def start_session(self, employee_id, company_id, active_token):
        """
        Starts a new work session.
        Sends a request to the API and logs the start time locally.
        
        Returns:
            tuple: (session_id, message) - session_id is None on failure.
        """
        url = f"{config.API_URL}/work-session/create"
        session_start = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        data = {
            "employee_id": str(employee_id),
            "company_id": str(company_id),
            "active_token": active_token,
            "session_start": session_start
        }

        try:
            response = requests.post(url, data=data, timeout=30)
        except Exception as e:
            return None, f"Network Error: {str(e)}"

        # Parse response safely
        try:
            res = response.json()
        except ValueError:
            return None, f"Invalid response from server (status {response.status_code})"

        # Validate status flag
        if not res.get("status"):
            return None, res.get("message", "Failed to start session")

        # Ensure data/id exists
        data_field = res.get("data")
        if not isinstance(data_field, dict) or "id" not in data_field:
            return None, "Session creation failed: missing session ID"

        session_id = data_field["id"]

        # Save into local SQLite
        try:
            self.cursor.execute("""
                INSERT INTO work_sessions (session_api_id, employee_id, start_time)
                VALUES (?, ?, ?)
            """, (session_id, employee_id, session_start))

            self.db.commit()
        except Exception as e:
            print("DB Error in start_session:", e)
            
        return session_id, "OK"

    def stop_session(self, employee_id, session_api_id, active_token):
        """
        Stops an active work session.
        Sends a request to the API and updates the local database with the end time.
        
        Returns:
            tuple: (success_bool, message)
        """
        url = f"{config.API_URL}/work-session/stop"
        session_end = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        

        data = {
            "employee_id": str(employee_id),
            "session_id": session_api_id,
            "active_token": active_token,
            "session_end": session_end
        }

        try:
            response = requests.post(url, data=data, timeout=30)
        except Exception as e:
            return False, f"Network Error: {str(e)}"

        try:
            res = response.json()
        except ValueError:
            return False, f"Invalid response from server (status {response.status_code})"

        if not res.get("status"):
            return False, res.get("message", "Failed to stop session")

        # Update SQLite
        try:
            self.cursor.execute("""
                UPDATE work_sessions 
                SET end_time=? 
                WHERE session_api_id=?
            """, (session_end, session_api_id))

            self.db.commit()
        except Exception as e:
            print("DB Error in stop_session:", e)

        return True, "OK"
