import sqlite3
import base64
import os
import random
import json
from datetime import datetime, timezone
import requests
from PIL import ImageGrab
import config
import threading
import internet_check
import time
from api_helper import api_post

class ScreenshotController:
    """
    Manages the capture and upload of screenshots.
    Screenshots are captured randomly within a defined interval to monitor work.
    """
    def __init__(self):
        self.active_token = None  # set when session starts
        self.capture_timers = []  # Keep references to prevent garbage collection
        self.upload_loop_started = False

    def _load_runtime_config(self):
        defaults = {
            "screenshots_enabled": True,
            "screenshot_interval_seconds": config.CAPTURE_DURATION,
        }
        cache_path = os.path.join(config.APP_ROOT, "config_cache.json")
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                defaults["screenshots_enabled"] = data.get("screenshots_enabled", defaults["screenshots_enabled"])
                defaults["screenshot_interval_seconds"] = data.get("screenshot_interval_seconds", defaults["screenshot_interval_seconds"])
            except Exception:
                pass
        return defaults

    def capture_screenshot_threadsafe(self, employee_id, company_id, work_session_id):
        """
        Captures a screenshot of the entire screen and saves it locally.
        This function is designed to run in a separate thread.
        """
        try:
            runtime_config = self._load_runtime_config()
            if not runtime_config.get("screenshots_enabled", True):
                return

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
                # Fallback to Qt-based capture
                try:
                    from PyQt6.QtGui import QGuiApplication
                    app = QGuiApplication.instance()
                    if app:
                        screen = app.primaryScreen()
                        if screen:
                            pixmap = screen.grabWindow(0)
                            pixmap.save(filename, "PNG")
                        else:
                            print(f"ImageGrab failed: {e}")
                            return
                    else:
                        print(f"ImageGrab failed: {e}")
                        return
                except Exception:
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
                    res = api_post("/screenshot/upload", json_data=payload, timeout=30)

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

    def start_upload_loop(self):
        if self.upload_loop_started:
            return
        self.upload_loop_started = True

        def upload_loop():
            while config.tracking_active:
                self.safe_upload()
                time.sleep(30)

        threading.Thread(target=upload_loop, daemon=True).start()
                
                
    def start_random_capture_loop(self, employee_id, company_id, work_session_id, active_token, root):
        """
        Starts the recursive loop for random screenshot capturing.
        Schedules 2 random captures within the CAPTURE_DURATION interval.
        Works with PyQt6 using QTimer.
        """
        try:
            from PyQt6.QtCore import QTimer
        except ImportError:
            from PyQt5.QtCore import QTimer
        
        self.active_token = active_token
        if not config.tracking_active:
            return

        runtime_config = self._load_runtime_config()
        if not runtime_config.get("screenshots_enabled", True):
            # Re-check later in case owner enables it
            def schedule_next_check():
                self.start_random_capture_loop(employee_id, company_id, work_session_id, active_token, root)

            next_timer = QTimer()
            next_timer.setSingleShot(True)
            next_timer.timeout.connect(schedule_next_check)
            next_timer.start(60 * 1000)
            self.capture_timers.append(next_timer)
            return

        interval_seconds = int(runtime_config.get("screenshot_interval_seconds", config.CAPTURE_DURATION))
        interval_seconds = max(30, interval_seconds)
        
        # Schedule 2 random screenshots within the next interval
        delays = sorted([random.randint(10, interval_seconds) for _ in range(2)])
        
        for delay in delays:
            # Use QTimer for PyQt6 compatibility
            def create_capture_callback(emp_id, comp_id, sess_id):
                def capture():
                    threading.Thread(
                        target=self.capture_screenshot_threadsafe,
                        args=(emp_id, comp_id, sess_id),
                        daemon=True
                    ).start()
                return capture
            
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(create_capture_callback(employee_id, company_id, work_session_id))
            timer.start(delay * 1000)
            self.capture_timers.append(timer)  # Keep reference
        
        # Attempt to upload pending screenshots immediately in background
        self.start_upload_loop()
        
        # Schedule the next loop iteration using QTimer
        def schedule_next():
            self.start_random_capture_loop(employee_id, company_id, work_session_id, active_token, root)
        
        next_timer = QTimer()
        next_timer.setSingleShot(True)
        next_timer.timeout.connect(schedule_next)
        next_timer.start(interval_seconds * 1000)
        self.capture_timers.append(next_timer)  # Keep reference
