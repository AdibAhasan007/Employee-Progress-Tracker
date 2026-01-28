import time
import threading
import sqlite3
import subprocess
import queue
import config
import requests
import sys

# Try to import pygetwindow for Windows active window detection
try:
    import pygetwindow as gw
except ImportError:
    gw = None

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
                """, (item["company_id"], item["employee_id"], item["work_session_id"], item["app_name"], item["window_title"], item["active_seconds"]))

            elif item_type == "WEB":
                # Try to insert with URL, fallback if column doesn't exist
                try:
                    cur.execute("""
                        INSERT INTO website_usages
                        (company_id, employee_id, work_session_id, domain, url, active_seconds, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """, (item["company_id"], item["employee_id"], item["work_session_id"], item["domain"], item.get("url"), item["active_seconds"]))
                except Exception:
                    # Fallback for old database structure
                    cur.execute("""
                        INSERT INTO website_usages
                        (company_id, employee_id, work_session_id, domain, active_seconds, created_at)
                        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """, (item["company_id"], item["employee_id"], item["work_session_id"], item["domain"], item["active_seconds"]))

            elif item_type == "LOG":
                cur.execute("""
                    INSERT INTO employee_activity_logs
                    (company_id, employee_id, work_session_id, minute_type, duration_seconds)
                    VALUES (?, ?, ?, ?, ?)
                """, (item["company_id"], item["employee_id"], item["work_session_id"], item["minute_type"], item["duration_seconds"]))

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
    try:
        if sys.platform == "win32":
            # Method 1: pygetwindow (Safest if installed)
            if gw:
                try:
                    win = gw.getActiveWindow()
                    if win:
                        return win.title
                except:
                    pass
            
            # Method 2: ctypes (Fallback)
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
            # Linux
            try:
                output = subprocess.check_output(["xdotool", "getactivewindow", "getwindowname"], text=True)
                return output.strip()
            except:
                return "Unknown Window"
    except Exception:
        return None

def get_url_from_browser():
    """
    Attempt to extract the actual URL from browser tabs using multiple methods.
    Returns: (full_url, browser_name) tuple
    """
    url = None
    browser_name = None
    
    try:
        if sys.platform == "win32":
            # Method 1: Try Chrome DevTools Protocol
            try:
                import socket
                import json
                import urllib.request
                
                # Chrome uses port 9222
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('127.0.0.1', 9222))
                sock.close()
                
                if result == 0:
                    try:
                        response = urllib.request.urlopen('http://127.0.0.1:9222/json', timeout=2)
                        data = json.loads(response.read().decode())
                        if data and len(data) > 0:
                            # Find the active tab with longest title (usually current tab)
                            active_tab = None
                            for tab in data:
                                if tab.get('type') == 'page' and not tab.get('url', '').startswith('chrome://'):
                                    if active_tab is None or len(tab.get('title', '')) > len(active_tab.get('title', '')):
                                        active_tab = tab
                            
                            if active_tab:
                                url = active_tab.get('url')
                                browser_name = "Chrome"
                                if url:
                                    return url, browser_name
                    except Exception as e:
                        print(f"Chrome DevTools error: {e}")
            except:
                pass
            
            # Method 2: Try Edge DevTools Protocol (similar to Chrome)
            try:
                import socket
                import json
                import urllib.request
                
                # Edge uses port 9323
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('127.0.0.1', 9323))
                sock.close()
                
                if result == 0:
                    try:
                        response = urllib.request.urlopen('http://127.0.0.1:9323/json', timeout=2)
                        data = json.loads(response.read().decode())
                        if data and len(data) > 0:
                            active_tab = None
                            for tab in data:
                                if tab.get('type') == 'page' and not tab.get('url', '').startswith('edge://'):
                                    if active_tab is None or len(tab.get('title', '')) > len(active_tab.get('title', '')):
                                        active_tab = tab
                            
                            if active_tab:
                                url = active_tab.get('url')
                                browser_name = "Edge"
                                if url:
                                    return url, browser_name
                    except Exception as e:
                        print(f"Edge DevTools error: {e}")
            except:
                pass
            
            # Method 3: Try Firefox via sessionstore files
            try:
                from pathlib import Path
                import json
                
                firefox_profiles = Path.home() / "AppData/Roaming/Mozilla/Firefox/Profiles"
                if firefox_profiles.exists():
                    for profile_dir in firefox_profiles.glob("*/"):
                        # Check recovery.jsonlz4 (compressed)
                        recovery_file = profile_dir / "sessionstore-backups/recovery.jsonlz4"
                        if recovery_file.exists():
                            try:
                                import lz4.frame
                                with open(recovery_file, 'rb') as f:
                                    data = lz4.frame.decompress(f.read())
                                    session = json.loads(data)
                                    
                                    # Extract URLs from windows and tabs
                                    if 'windows' in session and len(session['windows']) > 0:
                                        window = session['windows'][0]
                                        if 'tabs' in window and len(window['tabs']) > 0:
                                            # Get the last tab (most recently accessed)
                                            for tab in reversed(window['tabs']):
                                                if 'entries' in tab and len(tab['entries']) > 0:
                                                    # Get the most recent entry for this tab
                                                    entry = tab['entries'][-1]
                                                    if 'url' in entry:
                                                        url = entry['url']
                                                        browser_name = "Firefox"
                                                        if url and not url.startswith('about:'):
                                                            return url, browser_name
                            except Exception as e:
                                print(f"Firefox sessionstore error: {e}")
                        
                        # Also check sessionstore.js (uncompressed)
                        sessionstore_file = profile_dir / "sessionstore.js"
                        if sessionstore_file.exists() and not url:
                            try:
                                with open(sessionstore_file, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()
                                    session = json.loads(content)
                                    
                                    if 'windows' in session and len(session['windows']) > 0:
                                        window = session['windows'][0]
                                        if 'tabs' in window and len(window['tabs']) > 0:
                                            for tab in reversed(window['tabs']):
                                                if 'entries' in tab and len(tab['entries']) > 0:
                                                    entry = tab['entries'][-1]
                                                    if 'url' in entry:
                                                        url = entry['url']
                                                        browser_name = "Firefox"
                                                        if url and not url.startswith('about:'):
                                                            return url, browser_name
                            except Exception as e:
                                print(f"Firefox sessionstore.js error: {e}")
                        
                        if url and browser_name:
                            return url, browser_name
            except Exception as e:
                print(f"Firefox extraction error: {e}")
            
            # Method 4: Try Chrome via WMI process inspection
            try:
                import wmi
                c = wmi.WMI()
                for process in c.Win32_Process(name="chrome.exe"):
                    if process.CommandLine and 'http' in process.CommandLine:
                        cmd = process.CommandLine
                        # Chrome might have URL in command line arguments
                        parts = cmd.split()
                        for i, part in enumerate(parts):
                            if part.startswith('http://') or part.startswith('https://'):
                                url = part
                                browser_name = "Chrome"
                                if url and len(url) < 500:
                                    return url, browser_name
            except:
                pass
            
            # Method 5: Try Edge via WMI
            try:
                import wmi
                c = wmi.WMI()
                for process in c.Win32_Process(name="msedge.exe"):
                    if process.CommandLine and 'http' in process.CommandLine:
                        cmd = process.CommandLine
                        parts = cmd.split()
                        for part in parts:
                            if part.startswith('http://') or part.startswith('https://'):
                                url = part
                                browser_name = "Edge"
                                if url and len(url) < 500:
                                    return url, browser_name
            except:
                pass
    
    except Exception as e:
        print(f"URL extraction error: {e}")
    
    return url, browser_name



def detect_domain(title):
    """
    Extract domain and full URL from browser title.
    First tries to get URL from browser directly, then falls back to title parsing.
    Returns: (domain, full_url) tuple
    Example: ("facebook.com", "https://www.facebook.com/photo/?fbid=...")
    """
    # First, try to get URL directly from browser
    direct_url, browser_name = get_url_from_browser()
    
    if direct_url:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(direct_url)
            domain = parsed.netloc
            if not domain:
                domain = direct_url.split('/')[0]
            # Clean up domain
            domain = domain.replace('www.', '')
            return domain, direct_url
        except:
            pass
    
    # Fallback to title-based extraction
    if not title: 
        return None, None
    
    suffixes = [" - Google Chrome", " - Mozilla Firefox", " - Microsoft Edge", " - Opera"]
    extracted = title
    
    for s in suffixes:
        if s in title:
            extracted = title.replace(s, "").strip()
            break
    
    if not extracted:
        return None, None
    
    # Try to extract domain (look for domain.com pattern or https://...)
    full_url = extracted
    
    # If it looks like a URL, extract domain from it
    if "://" in extracted or "http" in extracted.lower():
        try:
            from urllib.parse import urlparse
            parsed = urlparse(extracted if extracted.startswith("http") else f"https://{extracted}")
            domain = parsed.netloc or parsed.path.split('/')[0]
        except:
            # Fallback: just use the extracted string as domain
            domain = extracted.split('/')[0].replace('www.', '')
    else:
        # It's already just the domain/URL as title
        domain = extracted.split('/')[0].replace('www.', '')
        # Try to construct full URL
        full_url = extracted
    
    return domain, full_url


# ==========================
# Upload to API
# ==========================
def upload_to_api(configure):
    import internet_check
    while config.tracking_active:
        for _ in range(config.SYNC_ACTIVITY_TIMER):
            if not config.tracking_active: return
            time.sleep(1)

        if not config.tracking_active: return

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
            cur.execute("SELECT MAX(id), company_id, employee_id, work_session_id, minute_type, SUM(duration_seconds), MAX(created_at) FROM employee_activity_logs GROUP BY company_id, employee_id, work_session_id, minute_type")
            logs = cur.fetchall()
            conn.close()

            if not apps and not sites and not logs: continue
            
            app_list = [{"app_name": r[4], "window_title": r[5], "active_seconds": r[6], "created_at": r[7]} for r in apps]
            site_list = [{"domain": r[4], "active_seconds": r[5], "created_at": r[6]} for r in sites]
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

            res = requests.post(configure["api_url"], json=payload, timeout=30)
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
def start_tracking(company_id, employee_id, active_token, work_session_id):
    configure = {
        "company_id": company_id,
        "employee_id": employee_id,
        "active_token": active_token,
        "work_session_id": work_session_id,
        "api_url": f"{config.API_URL}/upload/employee-activity"
    }

    # Start API upload thread
    t = threading.Thread(target=upload_to_api, args=(configure,), daemon=True)
    t.start()

    last_title = None
    active_seconds = 0

    while config.tracking_active:
        try:
            title = get_active_window_title()
            
            if title != last_title:
                if last_title:
                    domain, full_url = detect_domain(last_title)
                    if domain:
                        db_queue.put({"type": "WEB", "company_id": company_id, "employee_id": employee_id, "work_session_id": work_session_id, "domain": domain, "url": full_url, "active_seconds": active_seconds})
                    else:
                        app_name = last_title.split("-")[-1].strip() if "-" in last_title else last_title
                        db_queue.put({"type": "APP", "company_id": company_id, "employee_id": employee_id, "work_session_id": work_session_id, "app_name": app_name, "window_title": last_title, "active_seconds": active_seconds})
                
                last_title = title
                active_seconds = 0

            active_seconds += 1
            db_queue.put({"type": "LOG", "company_id": company_id, "employee_id": employee_id, "work_session_id": work_session_id, "minute_type": "ACTIVE" if title else "INACTIVE", "duration_seconds": 1})
            
            time.sleep(1)
            
        except Exception as e:
            print(f"Tracking Error: {e}")
            time.sleep(1)
