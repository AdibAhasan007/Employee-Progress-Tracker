#!/usr/bin/env python3
"""
Test script to verify browser URL capture functionality
Run this to diagnose which capture methods are working
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required packages are installed"""
    print("=" * 60)
    print("Testing Required Imports")
    print("=" * 60)
    
    packages = {
        'socket': 'Network socket operations',
        'json': 'JSON parsing',
        'urllib': 'URL requests',
        'wmi': 'Windows Management Instrumentation',
        'lz4': 'LZ4 compression (Firefox)',
        'pygetwindow': 'Window title extraction',
    }
    
    for pkg, description in packages.items():
        try:
            __import__(pkg)
            print(f"✓ {pkg:20} - {description}")
        except ImportError as e:
            print(f"✗ {pkg:20} - MISSING! ({e})")
    
    print()

def test_browser_detection():
    """Test browser installation detection"""
    print("=" * 60)
    print("Testing Browser Detection")
    print("=" * 60)
    
    import os
    from pathlib import Path
    
    browsers = {
        'Chrome': [
            r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
        ],
        'Edge': [
            r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
            r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
        ],
        'Firefox': [
            r'C:\Program Files\Mozilla Firefox\firefox.exe',
            r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe',
        ],
    }
    
    for browser_name, paths in browsers.items():
        found = False
        for path in paths:
            if os.path.exists(path):
                print(f"✓ {browser_name:15} - Found at {path}")
                found = True
                break
        
        if not found:
            print(f"✗ {browser_name:15} - Not found")
    
    print()

def test_firefox_profiles():
    """Test Firefox profile detection"""
    print("=" * 60)
    print("Testing Firefox Profiles")
    print("=" * 60)
    
    from pathlib import Path
    
    firefox_base = Path.home() / "AppData/Roaming/Mozilla/Firefox/Profiles"
    
    if firefox_base.exists():
        profiles = list(firefox_base.glob("*/"))
        if profiles:
            print(f"✓ Found {len(profiles)} Firefox profile(s):\n")
            for profile in profiles:
                profile_name = profile.name
                # Check for sessionstore files
                recovery_file = profile / "sessionstore-backups/recovery.jsonlz4"
                sessionstore_file = profile / "sessionstore.js"
                
                has_recovery = recovery_file.exists()
                has_sessionstore = sessionstore_file.exists()
                
                print(f"  Profile: {profile_name}")
                print(f"    - recovery.jsonlz4: {'✓' if has_recovery else '✗'}")
                print(f"    - sessionstore.js:  {'✓' if has_sessionstore else '✗'}")
        else:
            print("✗ No Firefox profiles found")
    else:
        print("✗ Firefox profiles directory not found")
    
    print()

def test_devtools_ports():
    """Test if DevTools ports are accessible"""
    print("=" * 60)
    print("Testing DevTools Port Availability")
    print("=" * 60)
    
    import socket
    
    ports = {
        9222: 'Chrome DevTools',
        9323: 'Edge DevTools',
    }
    
    for port, description in ports.items():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result == 0:
            print(f"✓ Port {port:5} ({description:20}) - OPEN (Browser running with debug)")
        else:
            print(f"✗ Port {port:5} ({description:20}) - CLOSED")
            print(f"     → To open: Use shortcut with --remote-debugging-port={port}")
    
    print()

def test_url_capture():
    """Test actual URL capture"""
    print("=" * 60)
    print("Testing URL Capture")
    print("=" * 60)
    
    try:
        from tracker.activity_tracker import get_url_from_browser
        
        print("Attempting to capture current URL...\n")
        url, browser = get_url_from_browser()
        
        if url:
            print(f"✓ Success!")
            print(f"  URL: {url}")
            print(f"  Browser: {browser}")
        else:
            print("✗ No URL captured (this is normal if no browser is open)")
            print("  Suggestions:")
            print("  1. Open Chrome/Edge with --remote-debugging-port flag")
            print("  2. Or use Firefox (no special setup needed)")
            print("  3. Visit a website and try again")
        
    except Exception as e:
        print(f"✗ Error testing URL capture: {e}")
    
    print()

def test_window_title():
    """Test window title fallback"""
    print("=" * 60)
    print("Testing Window Title Fallback")
    print("=" * 60)
    
    try:
        from tracker.activity_tracker import get_active_window_title
        
        title = get_active_window_title()
        print(f"✓ Current window title: {title}")
        print(f"  (This is the fallback method used when direct capture fails)")
        
    except Exception as e:
        print(f"✗ Error getting window title: {e}")
    
    print()

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "Browser URL Capture - Diagnostic Test".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    # Run tests
    test_imports()
    test_browser_detection()
    test_firefox_profiles()
    test_devtools_ports()
    test_url_capture()
    test_window_title()
    
    # Summary
    print("=" * 60)
    print("Diagnostic Complete")
    print("=" * 60)
    print()
    print("Summary:")
    print("1. If Chrome/Edge show CLOSED for ports → Use debug flag shortcut")
    print("2. If Firefox shows CLOSED → Not installed or profile missing")
    print("3. If URL capture shows No URL → Open a website first")
    print("4. All methods are optional - app always works with window title")
    print()
    print("For setup instructions, see: BROWSER_URL_CAPTURE_SETUP.md")
    print()

if __name__ == "__main__":
    main()
