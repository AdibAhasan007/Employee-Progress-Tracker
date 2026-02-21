# ⚙️ OWNER POLICY CONFIGURATION - QUICK GUIDE

## Where to Find It

### Step 1: Go to Owner Dashboard
```
Navigate to: /owner/dashboard/
```

### Step 2: Find Companies Overview Section
```
Look for: "📋 Companies Overview (Last 30 Days)"
```

### Step 3: Company Cards with Action Buttons
```
Each company card (e.g., DataSoft, Arts of Tech) shows buttons:

[👁️ View] [✏️ Edit] [⚙️ Policy] [📦 Plan] [🔐 Reset Admin] [🚫 Suspend/✅ Reactivate] [🔑 Rotate Key]
                      ^^^^
                    NEW BUTTON!
```

### Step 4: Click "⚙️ Policy" Button
```
This navigates to: /owner/company/{id}/policy/

Example for DataSoft (company_id=1):
URL: /owner/company/1/policy/
```

### Step 5: Configure Tracking Settings
```
On the Policy Configuration page, you can set:

[BASIC FEATURES]
☑ Enable Screenshots
☑ Enable Website Tracking  
☑ Enable Application Tracking
☑ Enable Keyboard Tracking
☑ Enable Mouse Tracking
☑ Enable Idle Detection
☑ Show Tracker Notification

[TIMING SETTINGS]
📊 Screenshot Interval: 600 seconds (range: 30-3600)
📊 Idle Threshold: 300 seconds (range: 60-1800)
📊 Config Sync Interval: 10 seconds (range: 5-60)
📊 Notification Interval: 30 minutes (range: 0-120)

[QUALITY & STORAGE]
📸 Max Screenshot Size: 5 MB (range: 1-50)
🎨 Screenshot Quality: 85% (range: 50-95)
💾 Local Data Retention: 30 days (range: 7-365)
```

### Step 6: Save Changes
```
Click [SAVE POLICY] button

Success! Message appears:
"Policy updated successfully! (Version X) 
 Changes will sync to all desktop agents within 10 seconds"
```

### Step 7: Changes Applied Automatically
```
Timeline:
0 sec   → Config saved in database, version incremented
1-10 sec → Desktop apps detect new version via polling
10 sec  → All employees' tracking apps update with new settings
No restart needed! Changes apply in real-time.
```

## Multiple Companies

### Switching Between Companies
```
1. Go back to Owner Dashboard
2. Find different company card (e.g., Arts of Tech)
3. Click [⚙️ Policy] on that company
4. Configure settings for Arts of Tech separately
5. Each company has isolated settings
```

### Example:
```
DataSoft Policy:
- Screenshots: ENABLED
- Screenshot Interval: 600 seconds

Arts of Tech Policy:
- Screenshots: DISABLED  
- Screenshot Interval: 300 seconds (if enabled)

Both settings work independently!
```

## Keyboard Shortcuts

```
Navigate to policy for company with ID:
1. Use direct URL: /owner/company/{id}/policy/
2. Replace {id} with actual company ID
3. DataSoft (id=1): /owner/company/1/policy/
4. Arts of Tech (id=2): /owner/company/2/policy/
```

## What Changed Today

### Problem Solved
```
BEFORE: "Koi Click Korar Option Nei toh???"
        No button to access Policy Configuration
        
AFTER:  [⚙️ Policy] button visible on each company card
        Click to configure tracking settings instantly
```

### Technical Implementation
```
✅ New URL route added: /owner/company/<int:company_id>/policy/
✅ View updated to accept company_id parameter
✅ OWNER permission check implemented
✅ Policy buttons added to both dashboard templates
✅ Isolated company settings (no data leakage)
✅ Full audit logging of all changes
```

## Troubleshooting

### Button Not Visible?
```
☐ Refresh the page (Ctrl+R or Cmd+R)
☐ Clear browser cache (Ctrl+Shift+Delete)
☐ Verify you're logged in as OWNER
☐ Check if logged into admin or employee account
```

### Settings Not Saving?
```
☐ Verify all numeric fields are within valid ranges
☐ Check browser console for JavaScript errors (F12)
☐ Ensure you clicked [SAVE POLICY] button
☐ Look for error message at top of page
```

### Changes Not Syncing to Desktop Apps?
```
☐ Check that config_sync_interval_seconds is < 60
☐ Verify desktop app is running
☐ Check desktop app's config_manager.py logs
☐ Manually restart desktop app if needed
☐ Wait up to configured interval seconds
```

### Wrong Company Settings Showing?
```
☐ Verify URL shows correct company_id
☐ Check company name at top of policy page
☐ Clear browser history/cache
☐ Try accessing in incognito/private window
```

## Related Pages

```
📊 Owner Dashboard: /owner/dashboard/
👥 Companies List: /owner/companies/
📋 Company Details: /owner/company/{id}/
✏️ Edit Company: /owner/company/{id}/edit/
💳 Change Plan: /owner/company/{id}/change-plan/
🔐 Reset Admin: /owner/company/{id}/reset-admin/
⚙️ Policy Config: /owner/company/{id}/policy/  ← YOU ARE HERE
```

## Feature Overview

This feature is part of the **Realtime Configuration Sync System**:

```
OWNER Dashboard
    ↓
[⚙️ Policy] Button (THIS FEATURE)
    ↓
Policy Configuration Page
    ↓
Edit & Save Settings
    ↓
Version Increment
    ↓
Audit Log Entry
    ↓
Desktop Apps (ConfigManager)
    ↓
Automatic Polling (Every 10 sec)
    ↓
Detects Version Change
    ↓
Updates Local Config
    ↓
Applies to Tracking System
    ↓
All Employees See Changes (No Restart!)
```

---

**Feature Status:** ✅ COMPLETE  
**Last Updated:** Today  
**Version:** 1.0  
**Tested:** Yes
