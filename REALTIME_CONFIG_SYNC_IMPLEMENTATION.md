# 🔄 Realtime Configuration Sync - Complete Implementation Guide

## Overview

Your system now supports **realtime configuration management**! The Owner can change PC tracking settings from the Dashboard, and all desktop applications will apply the changes **automatically within seconds** - no restart needed!

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ OWNER DASHBOARD (Django Web)                                │
│ └─ Settings → Policy Configuration Panel                    │
│    └─ Adjust Screenshot Interval, Idle Threshold, etc.      │
│    └─ Change Features Enable/Disable                        │
│    └─ Save & Sync                                           │
│       ⬇️ API sends to Backend                              │
│       └─ Increments config_version                          │
│       └─ Logs changes to AuditLog                           │
└─────────────────────────────────────────────────────────────┘
                            ⬇️ (POLL EVERY N SECONDS)
┌─────────────────────────────────────────────────────────────┐
│ PC TRACKER SOFTWARE (Desktop App - Python)                  │
│ ├─ ConfigManager polls API every 10 seconds                 │
│ ├─ Checks if config_version changed                         │
│ ├─ If changed:                                              │
│ │  ├─ Fetch new config from /api/employee-config/          │
│ │  ├─ Apply settings immediately                            │
│ │  ├─ Cache to local file                                   │
│ │  └─ Show notification "Config Updated"                    │
│ └─ Activity Tracker uses current settings                   │
│    ├─ Takes screenshots at new interval                     │
│    ├─ Detects idle at new threshold                         │
│    └─ Sends data at new sync frequency                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 What Was Added

### 1. **Backend Model Changes** (models.py)

```python
class CompanyPolicy(models.Model):
    # NEW FIELDS:
    config_sync_interval_seconds = IntegerField(default=10)  # Check frequency
    max_screenshot_size_mb = IntegerField(default=5)         # File size limit
    screenshot_quality = IntegerField(default=85)            # JPEG quality
    enable_keyboard_tracking = BooleanField(default=False)   # Optional tracking
    enable_mouse_tracking = BooleanField(default=False)      # Optional tracking
    enable_idle_detection = BooleanField(default=True)       # Idle on/off
    show_tracker_notification = BooleanField(default=True)   # System tray notify
    notification_interval_minutes = IntegerField(default=30) # Notify frequency
    local_data_retention_days = IntegerField(default=30)     # Data cleanup
    config_version = IntegerField(default=1)                 # Cache busting
    
    # METHODS:
    def increment_version(self):  # Call when updating
    def to_dict(self):            # Convert to API response
```

### 2. **API Endpoints** (views.py + urls.py)

#### `GET /api/employee-config/`
Returns current company policy configuration for the logged-in employee.

**Response:**
```json
{
    "status": true,
    "config": {
        "screenshots_enabled": true,
        "website_tracking_enabled": true,
        "screenshot_interval_seconds": 300,
        "config_sync_interval_seconds": 10,
        "config_version": 5,
        "updated_at": "2026-02-03T15:30:00Z",
        ...
    },
    "timestamp": "2026-02-03T15:31:00Z"
}
```

#### `POST /api/update-company-policy/`
Update company policy settings (OWNER ONLY).

**Request:**
```json
{
    "screenshots_enabled": true,
    "screenshot_interval_seconds": 600,
    "max_screenshot_size_mb": 5,
    "screenshot_quality": 90,
    ...
}
```

**Features:**
- ✅ Validation of all input values
- ✅ Auto-increment config_version for cache busting
- ✅ Detailed AuditLog with old/new values
- ✅ IP address logging
- ✅ Returns updated config immediately

### 3. **Dashboard Settings Panel** (policy_configuration.html)

Enhanced Owner Dashboard with:

```
Tracking Settings
├─ Screenshot Capture
│  ├─ Enable/Disable toggle
│  ├─ Capture Interval (slider 30-3600s)
│  ├─ Screenshot Quality (slider 50-95%)
│  └─ Max File Size (1-50 MB)
├─ Website Tracking (Enable/Disable)
├─ Application Tracking (Enable/Disable)
├─ Activity Detection
│  ├─ Keyboard tracking
│  ├─ Mouse tracking
│  └─ Idle detection
├─ Idle Threshold (60-1800 seconds)
├─ Notification Settings
│  ├─ Enable system notifications
│  └─ Notification interval
├─ Realtime Sync Config
│  └─ Check interval (5-60 seconds)
└─ Data Retention (7-365 days)
```

**UI Features:**
- ✅ Real-time value display
- ✅ Visual sliders for interval settings
- ✅ Configuration version badge
- ✅ Active features summary
- ✅ Last update timestamp
- ✅ Success notifications with sync timing info

### 4. **PC Software Config Manager** (config_manager.py)

```python
class ConfigManager:
    # Initialize with local cache
    __init__()
    
    # Check for updates and apply automatically
    check_for_updates(employee_token) -> bool
    
    # Get individual settings
    get_setting(name, default=None) -> value
    
    # Force immediate refresh
    force_refresh(employee_token) -> bool
    
    # Get status information
    get_status_info() -> dict
```

**Features:**
- ✅ Automatic polling (configurable interval)
- ✅ Version-based cache busting
- ✅ Local file caching for offline use
- ✅ Immediate application of changes
- ✅ Network error handling
- ✅ Notification on config changes

### 5. **Dashboard Integration** (dashboard_ui.py)

```python
class DashboardUI:
    def __init__(self):
        # Initialize config manager
        self.config_manager = ConfigManager()
        
        # Setup config check timer
        self.config_check_timer = QTimer()
        self.config_check_timer.timeout.connect(self.check_config_updates)
        self.config_check_timer.start(2000)  # Check every 2 seconds
    
    def check_config_updates(self):
        # Polls API for config changes
        # Applies changes immediately
        # Logs to console
```

---

## 📈 Configuration Hierarchy & Validation

All numeric values are **validated and clamped**:

| Setting | Range | Default |
|---------|-------|---------|
| `screenshot_interval_seconds` | 30-3600 | 600 |
| `idle_threshold_seconds` | 60-1800 | 300 |
| `config_sync_interval_seconds` | 5-60 | 10 |
| `max_screenshot_size_mb` | 1-50 | 5 |
| `screenshot_quality` | 50-95 | 85 |
| `notification_interval_minutes` | 0-120 | 30 |
| `local_data_retention_days` | 7-365 | 30 |

---

## 🔄 Realtime Sync Flow

### Step-by-Step Process

1. **Owner makes changes in Dashboard**
   - Opens: Dashboard → Tracking Policy Configuration
   - Changes settings (e.g., screenshot interval 300 → 600)
   - Clicks "Save Policy & Sync to All Agents"

2. **Backend processes changes**
   - Validates all input values
   - Increments `config_version` (e.g., 5 → 6)
   - Saves to database
   - Creates AuditLog entry with old/new values

3. **Desktop app checks for updates**
   - Every 2-10 seconds (configurable)
   - Calls: `GET /api/employee-config/`
   - Compares `config_version`

4. **If version changed:**
   - Fetches new config
   - Validates response
   - Updates ConfigManager
   - Caches to local file
   - Shows notification (if enabled)
   - Activity Tracker uses new settings

5. **Settings take effect immediately**
   - Next screenshot uses new interval
   - Idle detection uses new threshold
   - App continues running - no restart!

---

## 📱 Using in Your Code

### In Activity Tracker

```python
from config_manager import ConfigManager

config_mgr = ConfigManager()

# Get screenshot interval
interval = config_mgr.get_setting('screenshot_interval_seconds', 600)

# Check if feature enabled
if config_mgr.get_setting('screenshots_enabled', True):
    take_screenshot()

# Get quality setting
quality = config_mgr.get_setting('screenshot_quality', 85)
save_screenshot(quality=quality)
```

### In Dashboard

```python
# Already done! Dashboard automatically:
# 1. Initializes ConfigManager
# 2. Checks for updates every 2-10 seconds
# 3. Applies changes immediately
# 4. Uses new settings in activity tracking
```

---

## 🔐 Security & Audit

### Permission Control
- ✅ Only **OWNER** can update policies (API validates)
- ✅ Employees can only **READ** their company's policy
- ✅ All changes logged with IP address

### Audit Log Entry Example

```json
{
    "action_type": "POLICY_CHANGED",
    "user": "owner@company.com",
    "timestamp": "2026-02-03T15:31:00Z",
    "details": {
        "old_values": {
            "screenshot_interval_seconds": 600,
            "max_screenshot_size_mb": 5
        },
        "new_values": {
            "screenshot_interval_seconds": 300,
            "max_screenshot_size_mb": 10
        },
        "config_version": 6
    },
    "ip_address": "192.168.1.100"
}
```

---

## 🧪 Testing

### Test in Development

1. **Start Backend**
   ```bash
   cd backend
   python manage.py runserver
   ```

2. **Login as Owner**
   - Go to: http://localhost:8000/owner/login/
   - Navigate to: Tracking Policy Configuration

3. **Make a change**
   - Change screenshot interval from 600 → 300 seconds
   - Click Save

4. **Check API Response**
   ```bash
   # As employee, check config
   curl -H "Authorization: Token <token>" \
        http://localhost:8000/api/employee-config/
   ```

5. **Start Desktop App**
   - `python tracker/main.py`
   - Login as employee
   - Watch console for "Config update: v5 → v6"

### Monitor Config Checks

Desktop app logs:
```
🔧 ConfigManager initialized
🔄 Checking for updates...
⏱️  Config check at interval: 10s
🔄 Config update: v5 → v6
✅ Config applied: 2 changes
📢 Notification: Config updated with 2 changes
```

---

## 🚀 Advanced Features

### Force Manual Refresh

```python
# In desktop app
config_manager.force_refresh(employee_token)
```

### Get Config Status

```python
status = config_manager.get_status_info()
# Returns:
# {
#     'version': 6,
#     'last_update': '2026-02-03T15:31:00Z',
#     'screenshot_interval': '300s',
#     'sync_check_interval': '10s',
#     'features_enabled': 3
# }
```

### Offline Mode

If network is down, desktop app automatically:
- Uses cached config from `config_cache.json`
- Continues tracking with last known settings
- Tries again on next check interval

---

## 📊 Database Migration

Migration `0006_companypolicy_config_sync_interval_seconds_and_more.py` was created and applied.

**Changes:**
- Added 9 new fields to `CompanyPolicy`
- Modified help text on existing fields
- All with appropriate defaults
- No data loss - backfill with defaults

**Status:** ✅ Applied successfully

---

## ✅ Verification Checklist

- ✅ Model changes applied
- ✅ API endpoints created
- ✅ Dashboard UI enhanced
- ✅ ConfigManager implemented
- ✅ Dashboard integration done
- ✅ Migrations created & applied
- ✅ Audit logging configured
- ✅ Security enforced (OWNER-only)

---

## 🎯 Next Steps

1. **Test with Multiple Employees**
   - Start desktop app on 2-3 machines
   - Change config from Owner Dashboard
   - Verify all apps sync simultaneously

2. **Monitor Audit Logs**
   - Go to: Dashboard → Audit Logs
   - Filter by "POLICY_CHANGED"
   - Verify all changes are logged

3. **Performance Tuning**
   - Adjust `config_sync_interval_seconds` based on needs
   - Shorter = more responsive but more API calls
   - Longer = fewer API calls but slower updates
   - Default (10s) is recommended

4. **Custom Notifications**
   - Enhance `_show_notification()` in ConfigManager
   - Show toast popups instead of console logs
   - Add sound notifications if needed

---

## 📞 Support

If anything doesn't work:

1. Check backend logs: `python manage.py runserver`
2. Check desktop app console output
3. Verify API endpoint: `GET /api/employee-config/`
4. Check Audit Logs: Dashboard → Audit Logs → Filter: POLICY_CHANGED

---

**Created:** February 3, 2026
**Status:** ✅ Production Ready
**Version:** 1.0
