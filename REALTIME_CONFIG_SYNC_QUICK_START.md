# 🚀 Realtime Config Sync - QUICK START GUIDE

## 30-Second Overview

Your system now supports **realtime configuration changes**! Owner changes settings in the Dashboard, and all PC apps apply them **automatically within 10 seconds** - no restart needed!

---

## ⚡ Quick Start (3 Steps)

### Step 1: Owner Makes Changes
```
1. Login to web dashboard as OWNER
2. Go to: Tracking Policy → Settings
3. Change any setting (e.g., screenshot interval: 600 → 300 seconds)
4. Click "Save & Sync to All Agents"
```

### Step 2: Backend Updates (Automatic)
```
✅ Config version increments: v5 → v6
✅ Change logged to AuditLog
✅ API ready to serve new config
```

### Step 3: Desktop App Syncs (Automatic)
```
Every 10 seconds:
  1. Desktop app checks: GET /api/employee-config/
  2. Compares config_version
  3. If new: Fetch, validate, apply
  4. Activity tracker uses new settings
  ✅ Done! No restart needed.
```

---

## 📊 What You Can Configure

| Setting | Range | Effect |
|---------|-------|--------|
| Screenshot interval | 30-3600 sec | How often to capture screens |
| Idle threshold | 60-1800 sec | How long before marking idle |
| Config sync check | 5-60 sec | How often app checks for updates |
| Screenshot quality | 50-95% | JPEG quality (higher = larger) |
| Max file size | 1-50 MB | Screenshot file size limit |
| Features | On/Off | Enable/disable tracking types |
| Notifications | On/Off | Show system tray notifications |
| Data retention | 7-365 days | How long to keep local data |

---

## 🔍 Verify It Works

### In Django Backend
```bash
cd backend
python manage.py runserver
# Go to: Dashboard → Tracking Policy Configuration
# Make a change and save
```

### In Desktop App
Watch the console for:
```
🔧 ConfigManager initialized
🔄 Config update: v5 → v6
✅ Config applied: 2 changes
```

### In Audit Logs
```bash
# Go to: Dashboard → Audit Logs
# Filter by: POLICY_CHANGED
# See: Who changed what, when, from where
```

---

## 📝 New Files Created

| File | Purpose |
|------|---------|
| `config_manager.py` | Manages config sync (desktop app) |
| `REALTIME_CONFIG_SYNC_IMPLEMENTATION.md` | Full technical guide |
| `REALTIME_CONFIG_SYNC_SUMMARY.txt` | This overview |
| Migration `0006_*.py` | Database updates |

## 🔧 Modified Files

| File | Changes |
|------|---------|
| `models.py` | +10 fields to CompanyPolicy |
| `views.py` | +2 API endpoints |
| `urls.py` | +2 routes |
| `web_views.py` | Enhanced policy_configuration_view |
| `policy_configuration.html` | Complete redesign |
| `dashboard_ui.py` | +ConfigManager integration |

---

## 🎯 Use Cases

### Case 1: Increase Monitoring
```
Owner: "Productivity down, need more screenshots"
Action: Screenshot interval 600s → 180s
Result: All apps within 10s are taking screenshots every 3 minutes
```

### Case 2: Optimize Performance
```
Owner: "Server load high, reduce tracking"
Action: Disable app tracking, disable keyboard tracking
Result: All apps reduce CPU usage immediately
```

### Case 3: Compliance Change
```
Owner: "New privacy policy requires data deletion in 15 days"
Action: Data retention 30 days → 15 days
Result: All apps auto-delete data after 15 days
```

---

## ⚙️ Configuration Priority

If you need to change how often the app checks for config:

### Dashboard Setting
```
Policy Configuration → Realtime Sync Configuration
→ Config Check Interval: 5-60 seconds
```

**Recommendation:**
- **5-10 seconds:** Immediate updates (more API calls)
- **10-30 seconds:** Good balance (default 10s)
- **30-60 seconds:** Less frequent (fewer API calls)

---

## 🔒 Security Notes

✅ **Only OWNER can update** - API validates role
✅ **Token required** - Desktop app needs auth
✅ **Every change logged** - Full audit trail with IP
✅ **Version tracking** - Cache busting prevents stale configs

---

## 🆘 Troubleshooting

### Desktop App Not Syncing?
1. Check internet connection
2. Verify API URL in `config.py`
3. Watch console for "Config check error"
4. Check token is valid

### Changes Not Applying?
1. Verify desktop app is running
2. Check Dashboard → Audit Logs for change entry
3. Wait up to 10 seconds for next check
4. Restart desktop app if needed

### Want to Force Immediate Sync?
```python
# In config_manager.py
config_mgr.force_refresh(employee_token)
```

---

## 📚 Documentation

**Complete Guide:** `REALTIME_CONFIG_SYNC_IMPLEMENTATION.md`
- Full architecture
- Code examples
- Advanced features
- Testing procedures

**This File:** `REALTIME_CONFIG_SYNC_QUICK_START.md`
- Quick overview
- 3-step process
- Common use cases

**Technical Summary:** `REALTIME_CONFIG_SYNC_SUMMARY.txt`
- Features checklist
- Statistics
- Performance metrics

---

## 🎓 Next Level Features (Future)

- [ ] Scheduled config changes
- [ ] Config templates for different roles
- [ ] Batch update multiple companies
- [ ] Config rollback/history
- [ ] Real-time metrics dashboard
- [ ] Config versioning UI

---

## ✅ Status

**Version:** 1.0
**Status:** ✅ Production Ready
**Tested:** Yes
**Documentation:** Complete
**Audit Logging:** Enabled
**Security:** Validated

Ready to deploy! 🚀

---

**Questions?** Check the full implementation guide:
👉 `REALTIME_CONFIG_SYNC_IMPLEMENTATION.md`
