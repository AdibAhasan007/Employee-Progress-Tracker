# Browser URL Capture Setup Guide

## Overview
The tracker now captures full URLs from all major browsers (Chrome, Edge, Firefox) instead of just relying on window titles. This bypasses browser security restrictions through multiple methods.

## How It Works

### Multiple Capture Methods (In Priority Order)

1. **Chrome DevTools Protocol** (Preferred for Chrome)
   - Captures exact URL from active tab
   - Works when Chrome is started with debugging enabled
   
2. **Edge DevTools Protocol** (Preferred for Edge)
   - Similar to Chrome, dedicated for Edge browser
   - Requires Edge to be started with debugging enabled

3. **Firefox Session Files** (Preferred for Firefox)
   - Parses sessionstore files directly
   - No special configuration needed
   - Reads from: `%APPDATA%\Mozilla\Firefox\Profiles\[profile]\sessionstore-backups\recovery.jsonlz4`

4. **WMI Process Inspection** (Fallback)
   - Reads process command lines for URL patterns
   - Works when other methods fail
   - Less accurate but more reliable

5. **Window Title Extraction** (Final Fallback)
   - Traditional method of reading browser window title
   - Always works as last resort

---

## Setup Instructions

### Setup Option 1: Chrome with DevTools (RECOMMENDED for Chrome users)

#### Step 1: Create a Chrome Shortcut with Debugging Enabled

1. Right-click on your Chrome shortcut or desktop
2. Select **Create shortcut** (or right-click an existing shortcut → Properties)
3. In the Target field, modify to:
   ```
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
   ```
4. Click OK or Apply

#### Step 2: Test if It Works

1. Close all Chrome windows
2. Launch Chrome using the new shortcut
3. In the app, visit a few websites
4. Check the desktop app logs for "Chrome DevTools" messages
5. Full URLs should now appear in the app and web dashboard

**Example URL captured:** `https://www.facebook.com/photo/?fbid=122124270927003591&set=a.122124270927003601`

---

### Setup Option 2: Edge with DevTools (RECOMMENDED for Edge users)

#### Step 1: Create an Edge Shortcut with Debugging Enabled

1. Right-click on your Edge shortcut or desktop
2. Select **Create shortcut** (or right-click an existing shortcut → Properties)
3. In the Target field, modify to:
   ```
   "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9323
   ```
4. Click OK or Apply

#### Step 2: Test if It Works

1. Close all Edge windows
2. Launch Edge using the new shortcut
3. Visit various websites
4. Full URLs should be captured automatically

---

### Setup Option 3: Firefox (NO SPECIAL SETUP NEEDED)

Firefox support works automatically! The tracker:
- Reads your Firefox sessionstore files directly
- No special flags or configuration needed
- Extracts URLs from your browsing history

Simply use Firefox normally and full URLs will be captured automatically.

**Supported Firefox Profiles:**
- Default profile
- Any profile in `%APPDATA%\Mozilla\Firefox\Profiles\`

---

## Verification

### How to Check if URL Capture is Working

#### Check Desktop App Logs
1. Open the Tracker app
2. Watch the console/debug output for messages like:
   - "Chrome DevTools error: Connection refused" → Chrome not running with debug flag
   - "Firefox extraction error: [profile] not found" → Firefox not installed
   - "Edge DevTools error: None" → Edge not running with debug flag

#### Check Web Dashboard
1. Log into the admin/manager panel
2. Go to Employee Activity → Website Usage
3. Look at the URLs column
4. You should see full URLs like: `https://www.example.com/page?param=value`
5. Not just: `example.com`

#### Manual Test
1. **Chrome users:** Open a website with query parameters (e.g., `https://www.google.com/search?q=python`)
2. **Edge users:** Same as Chrome
3. **Firefox users:** Visit any website
4. Check the Tracker app immediately
5. Verify full URL appears in logs

---

## Troubleshooting

### Chrome/Edge URLs Not Captured

**Problem:** Only title is showing, not full URLs

**Solution 1: Verify Debug Flag is Active**
```
1. Press Ctrl+Shift+Esc (Task Manager)
2. Find chrome.exe or msedge.exe in the list
3. Click it and view "Command line"
4. Should contain: --remote-debugging-port=9222 (Chrome) or 9323 (Edge)
```

**Solution 2: Use the Correct Shortcut**
```
1. Make sure you're launching from the shortcut with debug flags
2. NOT from the regular start menu
3. Test by running the debug command directly from Command Prompt:
   
   For Chrome:
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
   
   For Edge:
   "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9323
```

**Solution 3: Check Port Availability**
```
1. Open Command Prompt
2. Run: netstat -ano | findstr :9222 (for Chrome)
3. Or: netstat -ano | findstr :9323 (for Edge)
4. If you see a listening port, it's available
5. If you see an error, the port might be in use
```

### Firefox URLs Not Captured

**Problem:** Firefox profile not found or no URLs captured

**Solution 1: Verify Firefox Installation**
```
1. Open File Explorer
2. Navigate to: %APPDATA%\Mozilla\Firefox\Profiles\
3. You should see folders like: xxxxxxxx.default-release
4. This is your Firefox profile
```

**Solution 2: Check Session File**
```
1. In File Explorer, go to: %APPDATA%\Mozilla\Firefox\Profiles\[profile name]\
2. Look for: sessionstore-backups folder
3. Check if recovery.jsonlz4 or recovery.json exists
4. If they exist, Firefox support should work
```

**Solution 3: Force Firefox to Save Session**
```
1. In Firefox, visit several websites
2. Close Firefox normally (don't force close)
3. This saves your session
4. Reopen Tracker app - it should now read the session
```

### All Methods Failing (Fallback Mode)

If all direct methods fail, the app automatically falls back to **window title extraction**:
- Shows domain name from browser title
- Less detailed than full URL
- Always works as safety net

**Why this happens:**
- Browsers not launched with debug flags
- Firefox not installed or profile not accessible
- Ports 9222/9323 blocked by antivirus
- WMI access restricted

---

## Requirements

### Installed Dependencies

The tracker automatically includes:
- `wmi` - For Windows process inspection
- `lz4` - For Firefox sessionstore decompression
- `pygetwindow` - For window title fallback
- `requests` - For API communication

All are installed automatically with the tracker.

---

## Security & Privacy Notes

**What the tracker captures:**
- Full URLs you visit in your browser
- Domain names
- Query parameters in URLs

**What the tracker DOES NOT capture:**
- Passwords or login credentials
- Private browsing data (incognito mode)
- Browser history from before tracking started
- Bookmarks or other stored data

**Browser Security:**
- Chrome/Edge DevTools requires explicit --remote-debugging-port flag
- Firefox session files are stored locally on your computer
- WMI requires administrator privileges
- All data is encrypted in transit to the server

---

## Advanced Configuration

### Custom Chrome Debug Port

If port 9222 is blocked, you can use a different port:

```
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9333
```

Then modify `tracker/activity_tracker.py`:
```python
result = sock.connect_ex(('127.0.0.1', 9333))  # Change from 9222 to 9333
```

### Disable URL Capture (If Needed)

Edit `tracker/activity_tracker.py` and comment out this line in `detect_domain()`:
```python
# direct_url, browser_name = get_url_from_browser()
```

---

## FAQ

**Q: Why do I need to enable Chrome debugging?**
A: Due to browser security restrictions, window titles only show the domain name. Debugging mode allows the tracker to read the exact URL from Chrome's open tabs.

**Q: Does Firefox need special setup?**
A: No! Firefox stores session data locally, so the tracker can read it without special flags.

**Q: Can I use all three browsers at once?**
A: Yes! The tracker handles all three browsers. Each one uses its own capture method.

**Q: What if I don't want full URLs captured?**
A: Contact your admin to disable URL capture, or use incognito/private browsing mode (won't be tracked).

**Q: Are my passwords captured?**
A: No. Only the URLs are captured. Passwords are stored in browser vaults, not in window titles or session files.

**Q: What about HTTPS websites?**
A: Full HTTPS URLs are captured correctly, including query parameters.

---

## Verification Script

To test if all capture methods are working:

```python
# Run this in Python to test
from tracker.activity_tracker import get_url_from_browser

# This will attempt all capture methods and show which ones work
url, browser = get_url_from_browser()
print(f"Captured: {url}")
print(f"Browser: {browser}")
```

---

## Summary Table

| Browser | Setup Required | Method | Accuracy |
|---------|---------------|---------|-----------| 
| Chrome  | Yes (debug flag) | DevTools Protocol | Very High (exact URL) |
| Edge    | Yes (debug flag) | DevTools Protocol | Very High (exact URL) |
| Firefox | No | Session Files | High (from session) |
| Any     | No | Title Extraction | Low (domain only) |

---

## Support

If URL capture isn't working:
1. Check the logs in the Tracker app
2. Verify browser is launched with correct flags
3. Confirm Firefox profile exists
4. Try the manual test procedures above
5. Fall back to domain name extraction as temporary solution

The app always has a fallback method, so tracking continues even if advanced URL capture fails.
