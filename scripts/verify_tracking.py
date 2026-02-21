#!/usr/bin/env python
"""
Tracking System Verification Script
Checks if all tracking components are working correctly.
"""
import os
import sys
import sqlite3
from pathlib import Path

def check_tracker_setup():
    print("=" * 60)
    print("🔍 TRACKING SYSTEM VERIFICATION")
    print("=" * 60)
    
    tracker_dir = Path(__file__).parent / "tracker"
    
    # 1. Check Python packages
    print("\n1️⃣ Checking Required Packages...")
    packages = ["PyQt6", "requests", "Pillow", "pygetwindow", "psutil", "lz4"]
    all_ok = True
    
    for pkg in packages:
        try:
            __import__(pkg.lower().replace("-", "_"))
            print(f"   ✅ {pkg}")
        except ImportError:
            print(f"   ❌ {pkg} - MISSING! Run: pip install {pkg}")
            all_ok = False
    
    if not all_ok:
        print("\n⚠️ Install missing packages first!")
        return False
    
    # 2. Check Screenshots folder
    print("\n2️⃣ Checking Screenshots Folder...")
    screenshot_folder = tracker_dir / "screenshots"
    if screenshot_folder.exists():
        print(f"   ✅ {screenshot_folder}")
    else:
        print(f"   ❌ {screenshot_folder} - MISSING!")
        print("   Creating it now...")
        screenshot_folder.mkdir(exist_ok=True)
        print(f"   ✅ Created {screenshot_folder}")
    
    # 3. Check Database
    print("\n3️⃣ Checking Database Tables...")
    db_path = tracker_dir / "hrsoftbdTracker.db"
    if db_path.exists():
        try:
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            
            tables = {
                "application_usages": ["id", "company_id", "employee_id", "work_session_id", "app_name", "window_title", "active_seconds"],
                "website_usages": ["id", "company_id", "employee_id", "work_session_id", "domain", "url", "active_seconds"],
                "employee_activity_logs": ["id", "company_id", "employee_id", "work_session_id", "minute_type", "duration_seconds"],
                "screenshots": ["id", "employee_id", "work_session_id", "photo_path", "company_id", "capture_time", "uploaded"],
            }
            
            for table_name, expected_cols in tables.items():
                cur.execute(f"PRAGMA table_info({table_name})")
                actual_cols = [col[1] for col in cur.fetchall()]
                
                missing = set(expected_cols) - set(actual_cols)
                if missing:
                    print(f"   ⚠️ {table_name} - Missing columns: {missing}")
                else:
                    print(f"   ✅ {table_name}")
            
            conn.close()
        except Exception as e:
            print(f"   ❌ Database error: {e}")
            return False
    else:
        print(f"   ⓘ Database will be created on first run")
    
    # 4. Check Config
    print("\n4️⃣ Checking Configuration...")
    config_file = tracker_dir / "config.py"
    if config_file.exists():
        with open(config_file) as f:
            content = f.read()
            if "COMPANY_KEY" in content:
                print(f"   ✅ COMPANY_KEY configured")
            else:
                print(f"   ❌ COMPANY_KEY missing!")
                return False
            
            if "SYNC_ACTIVITY_TIMER" in content:
                print(f"   ✅ SYNC_ACTIVITY_TIMER configured")
            else:
                print(f"   ❌ SYNC_ACTIVITY_TIMER missing!")
    
    # 5. Check Python files
    print("\n5️⃣ Checking Python Files...")
    files = [
        "activity_tracker.py",
        "screenshot_controller.py",
        "dashboard_ui.py",
        "main.py"
    ]
    
    for filename in files:
        filepath = tracker_dir / filename
        if filepath.exists():
            print(f"   ✅ {filename}")
        else:
            print(f"   ❌ {filename} - MISSING!")
            return False
    
    print("\n" + "=" * 60)
    print("✅ ALL CHECKS PASSED - System Ready!")
    print("=" * 60)
    print("\n🚀 Next Steps:")
    print("   1. Start Backend: python backend/manage.py runserver")
    print("   2. Start Desktop App: python tracker/main.py")
    print("   3. Login and start session")
    print("   4. Check Admin Dashboard for Activity/Screenshot data")
    print("\n" + "=" * 60)
    
    return True

if __name__ == "__main__":
    success = check_tracker_setup()
    sys.exit(0 if success else 1)
