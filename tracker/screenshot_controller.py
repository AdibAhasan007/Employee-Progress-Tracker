import sqlite3
import base64
import os
import random
from datetime import datetime, timezone
import requests
from PIL import ImageGrab
import config
import threading
import internet_check
import time

class ScreenshotController:
    """
    Manages the capture and upload of screenshots.
    Screenshots are captured randomly within a defined interval to monitor work.
    """
    def __init__(self):
        self.active_token = None  # set when session starts

    def capture_screenshot_threadsafe(self, employee_id, company_id, work_session_id):
        """
        Captures a screenshot of the entire screen and saves it locally.
        This function is designed to run in a separate thread.
        """
        try:
            # Create a NEW sqlite connection (threads cannot share!)
            db = sqlite3.connect(config.DB_PATH)
            cursor = db.cursor()

            # Generate filename with timestamp
            now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            now_file_name = datetime.now(timezone.utc).strftime("%Y_%m_%d_%H_%M_%S")
            filename = f"{config.SCREENSHOT_FOLDER}/ss_{now_file_name}.png"

            # Capture screen (Wrapped in try-except to prevent crash)
            try:
                img = ImageGrab.grab()
                img.save(filename)
            except Exception as e:
                print(f"ImageGrab failed: {e}")
                return # Exit if capture fails

            # Insert record into database
            cursor.execute("""
                INSERT INTO screenshots (employee_id, company_id, work_session_id, photo_path, capture_time)
                VALUES (?, ?, ?, ?, ?)
            """, (employee_id, company_id, work_session_id, filename, now))

            db.commit()
            db.close()

        except Exception as e:
            print(f"SS capture error: {e}")


    def upload_pending(self):
        """
        Checks for pending screenshots in the database and uploads them to the API.
        Deletes the local file upon successful upload.
        """
        try:
            # Create new connection for THIS thread
            db = sqlite3.connect(config.DB_PATH)
            cursor = db.cursor()

            # Fetch up to 5 pending screenshots
            cursor.execute("SELECT * FROM screenshots WHERE uploaded=0 LIMIT 5")
            rows = cursor.fetchall()

            for row in rows:
                local_id, emp, ws_id, path, comp, ctime, uploaded = row

                if not os.path.exists(path):
                    # If file is missing, mark as uploaded to skip it
                    cursor.execute("DELETE FROM screenshots WHERE id=?", (local_id,))
                    db.commit()
                    continue

                try:
                    # Encode image to Base64
                    with open(path, "rb") as img_file:
                        encoded = base64.b64encode(img_file.read()).decode()

                    payload = {
                        "employee_id": emp,
                        "company_id": comp,
                        "work_session_id": ws_id,
                        "capture_time": ctime,
                        "photo": encoded,
                        "active_token": self.active_token,  # required by backend
                    }

                    # Upload to API
                    res = requests.post(f"{config.API_URL}/screenshot/upload", json=payload, timeout=30)

                    if res.status_code == 200 and res.json().get("status"):
                        # Mark as uploaded (delete record and file)
                        cursor.execute("DELETE FROM screenshots WHERE id=?", (local_id,))
                        db.commit()
                        os.remove(path)

                except Exception as e:
                    print(f"Upload failed for {path}: {e}")
            
            db.close()
        except Exception as e:
            print(f"Upload thread DB error: {e}")

                
    def safe_upload(self):
        """
        Wrapper for upload_pending that checks for internet connection first.
        """
        if internet_check.is_connected():
            try:
                self.upload_pending()
            except Exception as e:
                print(f"Upload thread error: {e}")
                
                
    def start_random_capture_loop(self, employee_id, company_id, work_session_id, active_token, root):
        """
        Starts the recursive loop for random screenshot capturing.
        Schedules 2 random captures within the CAPTURE_DURATION interval.
        """
        self.active_token = active_token
        if not config.tracking_active:
            return
        
        # Schedule 2 random screenshots within the next 5 minutes
        delays = sorted([random.randint(10, config.CAPTURE_DURATION) for _ in range(2)])
        
        for delay in delays:
            # Use QTimer.singleShot from the root (DashboardUI) to schedule safely
            root.after(delay * 1000,
                lambda: threading.Thread(
                    target=self.capture_screenshot_threadsafe,
                    args=(employee_id, company_id, work_session_id),
                    daemon=True
                ).start())
        
        # Attempt to upload pending screenshots immediately in background
        threading.Thread(target=self.safe_upload, daemon=True).start()
        
        # Schedule the next loop iteration
        root.after(config.CAPTURE_DURATION * 1000, 
                   lambda: self.start_random_capture_loop(employee_id, company_id, work_session_id, active_token, root))
