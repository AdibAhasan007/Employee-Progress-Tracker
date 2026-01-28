# Browser URL Capture - Quick Start

## For Chrome Users ⚡

### One-Time Setup (2 minutes)

1. **Close all Chrome windows**
2. **Open Command Prompt** and paste:
   ```batch
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
   ```
3. **Done!** Chrome will now share URLs with the Tracker app

### Permanent Setup (Create Shortcut)
1. Right-click Desktop → New → Shortcut
2. Paste path: `"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222`
3. Name it: "Chrome with Tracker"
4. Click Finish
5. Use this shortcut to launch Chrome

---

## For Edge Users ⚡

### One-Time Setup (2 minutes)

1. **Close all Edge windows**
2. **Open Command Prompt** and paste:
   ```batch
   "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9323
   ```
3. **Done!** Edge will now share URLs with the Tracker app

### Permanent Setup (Create Shortcut)
1. Right-click Desktop → New → Shortcut
2. Paste path: `"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9323`
3. Name it: "Edge with Tracker"
4. Click Finish
5. Use this shortcut to launch Edge

---

## For Firefox Users ✅

### Setup Required: **NONE!**

Firefox works automatically with the Tracker app. Just:
1. Use Firefox normally
2. Visit websites
3. URLs are captured automatically

---

## How to Verify It's Working

1. **Launch Tracker app**
2. **Open your browser** (Chrome/Edge with debug, or Firefox)
3. **Visit a website** with parameters:
   - Chrome/Edge: `https://www.google.com/search?q=tracker`
   - Firefox: Visit any website
4. **Check the Tracker logs**
5. **You should see:** Full URL with query parameters

---

## What You'll See

### Before Setup (Without Debug Flag)
```
Domain: facebook.com
URL: facebook.com
```

### After Setup (With Debug Flag or Firefox)
```
Domain: facebook.com
URL: https://www.facebook.com/photo/?fbid=122124270927003591&set=a.122124270927003601
```

---

## Troubleshooting

### "Chrome DevTools error: Connection refused"
✓ Solution: You're not using the debug flag shortcut
- Launch Chrome with: `chrome.exe --remote-debugging-port=9222`

### "Edge DevTools error"
✓ Solution: You're not using the debug flag shortcut  
- Launch Edge with: `msedge.exe --remote-debugging-port=9323`

### Firefox URLs not showing
✓ Solution: Verify Firefox profile exists
- Go to: `%APPDATA%\Mozilla\Firefox\Profiles\`
- Should have folders like `xxxxxxxx.default-release`

### Still not working?
The app falls back to showing domain names. This always works as a backup.

---

## That's It! 

Your URLs are now being captured in full detail across all browsers. Check your employee activity dashboard to see captured URLs.
