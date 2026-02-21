import requests
import sqlite3
from PyQt6.QtWidgets import QMessageBox
from config import DB_PATH, API_URL
import threading
from db_init import init_db
from PyQt6.QtCore import QObject, pyqtSignal
from api_helper import api_post

class LoginController(QObject):
    """
    Controller for handling user authentication.
    Manages API calls for login, local storage of user data, and session validation.
    Uses PyQt signals to communicate results back to the UI thread.
    """
    login_success = pyqtSignal(dict) # Signal emitted on successful login
    login_failed = pyqtSignal(str)   # Signal emitted on login failure
    error_occurred = pyqtSignal(str) # Signal emitted on unexpected errors

    def __init__(self, app_context):
        super().__init__()
        self.app_context = app_context
        self.employee_id = None
        self.token = None
        # Ensure database is initialized when controller starts
        init_db()
        # Connect signals to local handlers
        self.login_success.connect(self.on_login_success)
        self.login_failed.connect(self.on_login_failed)
        self.error_occurred.connect(self.on_error)

    def api_login(self, username, password):
        """
        Initiates the login process in a background thread to keep UI responsive.
        """
        threading.Thread(target=self._api_login_thread, args=(username, password), daemon=True).start()

    def _api_login_thread(self, username, password):
        """
        Background thread function for login API call.
        """
        try:
            response = api_post("/login", json_data={"email": username, "password": password})
            data = response.json()
            if data["status"]:
                self.employee_local_save(data["data"])
                self.login_success.emit(data["data"])
            else:
                self.login_failed.emit(data["message"])
        except Exception as e:
            self.error_occurred.emit(str(e))

    def employee_local_save(self, emp_data):
        """
        Saves the logged-in employee's data to the local SQLite database.
        This allows the app to remember the user and their session.
        """
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        try:
            cur = conn.cursor()
            # Clear previous user data to ensure only one active user
            cur.execute("DELETE FROM employee")
            cur.execute("""
                INSERT INTO employee (id, name, email, company_id, active_token, toddays_worked_time, toddays_active_time, toddays_inactive_time, task_note)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                emp_data["id"], emp_data["name"], emp_data["email"], emp_data["company_id"],
                emp_data["active_token"], emp_data["toddays_worked_time"], emp_data["toddays_active_time"],
                emp_data["toddays_inactive_time"], emp_data["task_note"]
            ))
            conn.commit()
        finally:
            conn.close()

    def login_status_check(self):
        """
        Checks if a valid user session exists locally and verifies it with the API.
        Also checks for stalled sessions that need recovery.
        Returns True if logged in, False otherwise.
        """
        try:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            try:
                cur = conn.cursor()
                cur.execute("SELECT * FROM employee ORDER BY id DESC LIMIT 1")
                emp = cur.fetchone()
            finally:
                conn.close()

            if not emp:
                return False

            # Verify token with API
            response = api_post("/login-check", data={"id": emp[0], "token": emp[4]})
            data = response.json()
            return data["status"]
        except:
            return False

    def check_stalled_session(self):
        """
        Checks if there's an active session that wasn't properly closed.
        Returns session_id if found, None otherwise.
        """
        try:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            try:
                cur = conn.cursor()
                # Get the latest session
                cur.execute("""
                    SELECT id FROM work_sessions 
                    WHERE end_time IS NULL 
                    ORDER BY start_time DESC LIMIT 1
                """)
                result = cur.fetchone()
            finally:
                conn.close()
            
            return result[0] if result else None
        except:
            return None

    def resume_session(self, session_id):
        """Resume a stalled session - just return the session ID to continue tracking"""
        return session_id

    def close_stalled_session(self, session_id):
        """Close a stalled session with current timestamp"""
        try:
            from datetime import datetime
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            try:
                cur = conn.cursor()
                cur.execute("""
                    UPDATE work_sessions 
                    SET end_time = ? 
                    WHERE id = ? AND end_time IS NULL
                """, (datetime.now(), session_id))
                conn.commit()
            finally:
                conn.close()
            return True
        except Exception as e:
            print(f"Error closing stalled session: {e}")
            return False

    def on_login_success(self, data):
        """
        Slot handling successful login.
        Switches the main window from LoginUI to DashboardUI.
        """
        from dashboard_ui import DashboardUI
        # Store auth details for other controllers
        self.employee_id = data.get("id")
        self.token = data.get("active_token")
        # Close current window (LoginUI)
        if hasattr(self.app_context, 'window') and self.app_context.window:
            self.app_context.window.close()
        
        self.app_context.window = DashboardUI(self)
        self.app_context.window.show()

    def on_login_failed(self, message):
        """Slot handling login failure. Shows an error message."""
        if hasattr(self.app_context, 'window'):
            QMessageBox.critical(self.app_context.window, "Login Failed", message)

    def on_error(self, message):
        """Slot handling general errors. Shows an error message."""
        if hasattr(self.app_context, 'window'):
            QMessageBox.critical(self.app_context.window, "Error", message)
