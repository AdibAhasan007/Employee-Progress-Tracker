import time
import threading
import sqlite3
import subprocess
import queue
import config
import requests
import sys
import os
import json
from pathlib import Path
from urllib.parse import urlparse

try:
    import pygetwindow as gw
except ImportError:
    gw = None

try:
    import psutil
except ImportError:
    psutil = None

try:
    from pywinauto import Desktop
except ImportError:
    Desktop = None

# ==========================
# Thread-safe DB queue
# ==========================
db_queue = queue.Queue()

def db_worker():
    while True:
        try:
            item = db_queue.get()
            if item is None:
                break
            
            item_type = item["type"]
            conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
            cur = conn.cursor()

            if item_type == "APP":
                cur.execute("""
                    INSERT INTO application_usages
                    (company_id, employee_id, work_session_id, app_name, window_title, active_seconds)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (item["company_id"], item["employee_id"], item["work_session_id"], 
                      item["app_name"], item["window_title"], item["active_seconds"]))

            elif item_type == "WEB":
                try:
                    cur.execute("""
                        INSERT INTO website_usages
                        (company_id, employee_id, work_session_id, domain, url, active_seconds, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """, (item["company_id"], item["employee_id"], item["work_session_id"], 
                          item["domain"], item.get("url"), item["active_seconds"]))
                except Exception:
                    cur.execute("""
                        INSERT INTO website_usages
                        (company_id, employee_id, work_session_id, domain, active_seconds, created_at)
                        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """, (item["company_id"], item["employee_id"], item["work_session_id"], 
                          item["domain"], item["active_seconds"]))

            elif item_type == "LOG":
                cur.execute("""
                    INSERT INTO employee_activity_logs
                    (company_id, employee_id, work_session_id, minute_type, duration_seconds)
                    VALUES (?, ?, ?, ?, ?)
                """, (item["company_id"], item["employee_id"], item["work_session_id"], 
                      item["minute_type"], item["duration_seconds"]))

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"DB Worker Error: {e}")
        finally:
            db_queue.task_done()

threading.Thread(target=db_worker, daemon=True).start()

# ==========================
# Active Window Detection
# ==========================
def get_active_window_title():
    """Get the active window title and process information"""
    try:
        if sys.platform == "win32":
            if gw:
                try:
                    win = gw.getActiveWindow()
                    if win:
                        return win.title
                except:
                    pass
            
            try:
                import ctypes
                hwnd = ctypes.windll.user32.GetForegroundWindow()
                length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
                    return buff.value
            except:
                pass
                
            return "Unknown Window"
        else:
            try:
                output = subprocess.check_output(["xdotool", "getactivewindow", "getwindowname"], text=True)
                return output.strip()
            except:
                return "Unknown Window"
    except Exception:
        return None

def get_active_process_name():
    """Get the actual process name of the active window using psutil"""
    if not psutil:
        return None
    
    try:
        if sys.platform == "win32":
            import ctypes
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            pid = ctypes.c_ulong()
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            process_id = pid.value
            
            if process_id:
                try:
                    process = psutil.Process(process_id)
                    return process.name().replace('.exe', '')
                except:
                    pass
        return None
    except Exception:
        return None

def _get_foreground_hwnd():
    if sys.platform != "win32":
        return None
    try:
        import ctypes
        return ctypes.windll.user32.GetForegroundWindow()
    except Exception:
        return None

def get_url_from_address_bar():
    """Attempt to read the current URL from the active browser address bar using UI Automation."""
    if sys.platform != "win32" or Desktop is None:
        return None, None

    hwnd = _get_foreground_hwnd()
    if not hwnd:
        return None, None

    try:
        window = Desktop(backend="uia").window(handle=hwnd)
        if not window.exists(timeout=0.5):
            return None, None

        # Try to find address bar edit control
        edits = window.descendants(control_type="Edit")
        for edit in edits:
            try:
                value = edit.get_value()
                if not value:
                    continue
                value = value.strip()
                if value.startswith("http://") or value.startswith("https://"):
                    return value, "Browser"
            except Exception:
                continue
    except Exception:
        return None, None

    return None, None

def get_url_from_browser_improved():
    """
    Extract actual URL from browser tabs using multiple methods.
    Returns: (full_url, browser_name) tuple
    """
    url = None
    browser_name = None
    
    try:
        if sys.platform == "win32":
            # Method 0: Try UI Automation address bar (works without remote debugging)
            addr_url, addr_name = get_url_from_address_bar()
            if addr_url:
                return addr_url, addr_name

            # Method 1: Chrome DevTools Protocol
            try:
                import socket
                import urllib.request
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('127.0.0.1', 9222))
                sock.close()
                
                if result == 0:
                    try:
                        response = urllib.request.urlopen('http://127.0.0.1:9222/json', timeout=2)
                        data = json.loads(response.read().decode())
                        if data:
                            for tab in data:
                                if tab.get('type') == 'page' and not tab.get('url', '').startswith('chrome://'):
                                    url = tab.get('url')
                                    browser_name = "Chrome"
                                    if url and len(url) < 2048:
                                        return url, browser_name
                    except Exception as e:
                        pass
            except:
                pass
            
            # Method 2: Edge DevTools Protocol
            try:
                import socket
                import urllib.request
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('127.0.0.1', 9323))
                sock.close()
                
                if result == 0:
                    try:
                        response = urllib.request.urlopen('http://127.0.0.1:9323/json', timeout=2)
                        data = json.loads(response.read().decode())
                        if data:
                            for tab in data:
                                if tab.get('type') == 'page' and not tab.get('url', '').startswith('edge://'):
                                    url = tab.get('url')
                                    browser_name = "Edge"
                                    if url and len(url) < 2048:
                                        return url, browser_name
                    except Exception:
                        pass
            except:
                pass
            
            # Method 3: Firefox sessionstore extraction
            try:
                firefox_profiles = Path.home() / "AppData/Roaming/Mozilla/Firefox/Profiles"
                if firefox_profiles.exists():
                    for profile_dir in firefox_profiles.glob("*/"):
                        recovery_file = profile_dir / "sessionstore-backups/recovery.jsonlz4"
                        if recovery_file.exists():
                            try:
                                import lz4.frame
                                with open(recovery_file, 'rb') as f:
                                    data = lz4.frame.decompress(f.read())
                                    session = json.loads(data)
                                    
                                    if 'windows' in session and session['windows']:
                                        window = session['windows'][0]
                                        if 'tabs' in window and window['tabs']:
                                            for tab in reversed(window['tabs']):
                                                if 'entries' in tab and tab['entries']:
                                                    entry = tab['entries'][-1]
                                                    if 'url' in entry:
                                                        url = entry['url']
                                                        browser_name = "Firefox"
                                                        if url and not url.startswith('about:'):
                                                            return url, browser_name
                            except Exception:
                                pass
            except Exception:
                pass
    
    except Exception:
        pass
    
    return url, browser_name

def is_browser_process(process_name):
    if not process_name:
        return False
    browser_processes = {"chrome", "msedge", "firefox", "opera", "brave", "vivaldi", "iexplore"}
    return process_name.lower() in browser_processes

def is_browser_window(title, process_name=None):
    """Check if the given title is from a browser"""
    if process_name and is_browser_process(process_name):
        return True
    if not title:
        return False
    browser_keywords = [" - Google Chrome", " - Mozilla Firefox", " - Microsoft Edge", " - Opera", "YouTube", "Facebook", "Instagram", "Twitter", "Google", "Gmail", "Edge", "Chrome", "Brave"]
    return any(keyword.lower() in title.lower() for keyword in browser_keywords)

def extract_clean_url(full_url):
    """Clean and validate extracted URL"""
    if not full_url:
        return None
    
    # Check if it's actually a valid URL
    if not (full_url.startswith('http://') or full_url.startswith('https://')):
        return None
    
    # Remove very long URLs (likely corrupted)
    if len(full_url) > 2048:
        return None
    
    # Check for common corruption patterns
    if '%20%20' in full_url or 'xn--' in full_url and len(full_url) > 500:
        return None
    
    return full_url

def detect_domain_and_url(title, process_name=None):
    """
    Extract domain and URL from browser title and browser state.
    Returns: (domain, full_url) tuple
    """
    # First, try to get URL directly from browser
    direct_url, browser_name = get_url_from_browser_improved()
    
    if direct_url:
        clean_url = extract_clean_url(direct_url)
        if clean_url:
            try:
                parsed = urlparse(clean_url)
                domain = parsed.netloc
                if domain:
                    domain = domain.replace('www.', '')
                    return domain, clean_url
            except:
                pass
    
    # Fallback: extract from title (domain only)
    if not title:
        return None, None
    
    # For known services that don't include a domain in the title
    title_lower = title.lower()
    keyword_domains = {
        "youtube": "youtube.com",
        "facebook": "facebook.com",
        "instagram": "instagram.com",
        "twitter": "twitter.com",
        "x.com": "x.com",
        "linkedin": "linkedin.com",
        "github": "github.com",
        "gmail": "mail.google.com",
        "google": "google.com",
        "drive": "drive.google.com",
        "docs": "docs.google.com",
        "meet": "meet.google.com",
    }
    for key, domain in keyword_domains.items():
        if key in title_lower:
            return domain, None
    
    # Extract domain from title (e.g., "youtube.com - Video Title")
    suffixes = [" - Google Chrome", " - Mozilla Firefox", " - Microsoft Edge", " - Opera", " — YouTube", " | YouTube"]
    extracted = title
    
    for suffix in suffixes:
        if suffix in title:
            extracted = title.split(suffix)[0].strip()
            break
    
    if extracted and "." in extracted:
        domain = extracted.split()[0].replace('www.', '')
        if len(domain) < 100 and not any(char in domain for char in ['%', 'xn--']):
            return domain, None
    
    return None, None


# ==========================
# Upload to API
# ==========================
def upload_to_api(configure):
    import internet_check
    from api_helper import api_post
    
    while config.tracking_active:
        for _ in range(config.SYNC_ACTIVITY_TIMER):
            if not config.tracking_active:
                return
            time.sleep(1)

        if not config.tracking_active:
            return

        if not internet_check.is_connected():
            print("No Internet.")
            continue

        try:
            conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
            cur = conn.cursor()
            
            cur.execute("SELECT * FROM application_usages")
            apps = cur.fetchall()
            cur.execute("SELECT * FROM website_usages")
            sites = cur.fetchall()
            cur.execute("""
                SELECT MAX(id), company_id, employee_id, work_session_id, minute_type, SUM(duration_seconds), MAX(created_at) 
                FROM employee_activity_logs 
                GROUP BY company_id, employee_id, work_session_id, minute_type
            """)
            logs = cur.fetchall()
            conn.close()

            if not apps and not sites and not logs:
                continue
            
            app_list = [{"app_name": r[4], "window_title": r[5], "active_seconds": r[6], "created_at": r[7] if len(r) > 7 else None} for r in apps]
            site_list = [{"domain": r[4], "url": r[5] if len(r) > 5 else None, "active_seconds": r[6] if len(r) > 6 else r[5], "created_at": r[7] if len(r) > 7 else None} for r in sites]
            log_list = [{"minute_type": r[4], "duration_seconds": r[5], "created_at": r[6]} for r in logs]

            payload = {
                "employee_id": configure["employee_id"],
                "company_id": configure["company_id"],
                "active_token": configure["active_token"],
                "work_session_id": configure["work_session_id"],
                "applications": app_list,
                "websites": site_list,
                "activities": log_list
            }

            res = api_post("/upload/employee-activity", json_data=payload, timeout=30)
            if res.status_code == 200:
                conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
                cur = conn.cursor()
                cur.execute("DELETE FROM application_usages")
                cur.execute("DELETE FROM website_usages")
                cur.execute("DELETE FROM employee_activity_logs")
                conn.commit()
                conn.close()
        except Exception as e:
            print(f"Upload failed: {e}")

# ==========================
# Main Tracking Loop
# ==========================
_runtime_config = {
    "idle_threshold_seconds": 300,
    "enable_idle_detection": True,
    "website_tracking_enabled": True,
    "app_tracking_enabled": True,
}
_last_config_read = 0

def _load_runtime_config():
    global _runtime_config, _last_config_read
    now = time.time()
    if now - _last_config_read < 10:
        return _runtime_config

    cache_path = Path(config.APP_ROOT) / "config_cache.json"
    if cache_path.exists():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            _runtime_config.update({
                "idle_threshold_seconds": data.get("idle_threshold_seconds", _runtime_config["idle_threshold_seconds"]),
                "enable_idle_detection": data.get("enable_idle_detection", _runtime_config["enable_idle_detection"]),
                "website_tracking_enabled": data.get("website_tracking_enabled", _runtime_config["website_tracking_enabled"]),
                "app_tracking_enabled": data.get("app_tracking_enabled", _runtime_config["app_tracking_enabled"]),
            })
        except Exception:
            pass

    _last_config_read = now
    return _runtime_config

def get_idle_seconds():
    if sys.platform != "win32":
        return 0
    try:
        import ctypes

        class LASTINPUTINFO(ctypes.Structure):
            _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

        last_input_info = LASTINPUTINFO()
        last_input_info.cbSize = ctypes.sizeof(LASTINPUTINFO)
        if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(last_input_info)) == 0:
            return 0
        millis = ctypes.windll.kernel32.GetTickCount() - last_input_info.dwTime
        return max(0, int(millis / 1000))
    except Exception:
        return 0

def _record_usage(company_id, employee_id, work_session_id, title, process_name, active_seconds, runtime_config):
    if not title or active_seconds <= 0:
        return

    if is_browser_window(title, process_name):
        if not runtime_config.get("website_tracking_enabled", True):
            return
        domain, full_url = detect_domain_and_url(title, process_name)
        if domain:
            db_queue.put({
                "type": "WEB",
                "company_id": company_id,
                "employee_id": employee_id,
                "work_session_id": work_session_id,
                "domain": domain,
                "url": full_url,
                "active_seconds": active_seconds,
            })
    else:
        if not runtime_config.get("app_tracking_enabled", True):
            return
        app_name = process_name if process_name else (title.split("-")[-1].strip() if "-" in title else title)
        db_queue.put({
            "type": "APP",
            "company_id": company_id,
            "employee_id": employee_id,
            "work_session_id": work_session_id,
            "app_name": app_name,
            "window_title": title,
            "active_seconds": active_seconds,
        })

def start_tracking(company_id, employee_id, active_token, work_session_id):
    configure = {
        "company_id": company_id,
        "employee_id": employee_id,
        "active_token": active_token,
        "work_session_id": work_session_id,
    }

    # Start API upload thread
    t = threading.Thread(target=upload_to_api, args=(configure,), daemon=True)
    t.start()

    last_title = None
    last_process = None
    active_seconds = 0
    flush_interval_seconds = 60

    while config.tracking_active:
        try:
            title = get_active_window_title()
            process_name = get_active_process_name()
            runtime_config = _load_runtime_config()

            if title in ["Unknown Window", ""]:
                title = None

            idle_seconds = get_idle_seconds() if runtime_config.get("enable_idle_detection", True) else 0
            is_idle = runtime_config.get("enable_idle_detection", True) and idle_seconds >= runtime_config.get("idle_threshold_seconds", 300)
            
            if is_idle:
                if last_title and active_seconds > 0:
                    _record_usage(company_id, employee_id, work_session_id, last_title, last_process, active_seconds, runtime_config)
                    last_title = None
                    last_process = None
                    active_seconds = 0
            elif title != last_title or active_seconds >= flush_interval_seconds:
                if last_title:
                    _record_usage(company_id, employee_id, work_session_id, last_title, last_process, active_seconds, runtime_config)

                last_title = title
                if process_name:
                    last_process = process_name
                active_seconds = 0

            if not is_idle:
                active_seconds += 1

            minute_type = "INACTIVE" if (is_idle or not title) else "ACTIVE"
            db_queue.put({
                "type": "LOG", 
                "company_id": company_id, 
                "employee_id": employee_id, 
                "work_session_id": work_session_id, 
                "minute_type": minute_type, 
                "duration_seconds": 1
            })
            
            time.sleep(1)
            
        except Exception as e:
            print(f"Tracking Error: {e}")
            time.sleep(1)
