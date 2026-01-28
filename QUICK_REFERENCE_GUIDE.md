# 🚀 Full URL Tracking - Quick Reference Guide

## What's New?

### Before ❌
```
Your browser visits: https://www.facebook.com/photo/?fbid=122124270927003591
Tracked as: facebook.com
Shown as: https://facebook.com
```

### After ✅
```
Your browser visits: https://www.facebook.com/photo/?fbid=122124270927003591
Tracked as: facebook.com + https://www.facebook.com/photo/?fbid=122124270927003591
Shown as: https://www.facebook.com/photo/?fbid=122124270927003591 [CLICKABLE]
```

---

## 📊 Visual Flow Diagram

```
DESKTOP APPLICATION
┌─────────────────────────────────────┐
│  Firefox / Chrome / Edge / Opera    │
│  Title: "Facebook photo - Chrome"   │
└────────────────┬────────────────────┘
                 │
                 ↓
        ┌─────────────────┐
        │ detect_domain() │
        │ (Enhanced!)     │
        └────────┬────────┘
                 │
        ┌────────┴────────┐
        ↓                 ↓
    domain:           full_url:
    facebook.com      https://www.facebook.com/
                      photo/?fbid=12212427092700...
        │                 │
        └────────┬────────┘
                 │
         ┌───────↓────────┐
         │  SQLite DB     │
         │ website_usages │
         │  domain: facebookl
         │  url: https://www...
         │  time: 300s
         └───────┬────────┘
                 │
         ┌───────↓────────────────┐
         │   Django Web Server    │
         │   API /upload-activity │
         └───────┬────────────────┘
                 │
         ┌───────↓───────────────────────┐
         │  PostgreSQL / SQLite          │
         │  core_websiteusage            │
         │  ├─ domain: facebook.com      │
         │  ├─ url: https://www.facebook │
         │  │        /photo/?fbid=...    │
         │  └─ active_seconds: 300       │
         └───────┬───────────────────────┘
                 │
         ┌───────↓────────────┐
         │  Django Templates  │
         │  + Report Views    │
         └───────┬────────────┘
                 │
         ┌───────↓─────────────┐
         │  Web Browser        │
         │  Full URL visible   │
         │  Clickable link     │
         │  [Click to visit]   │
         └─────────────────────┘
```

---

## 🔄 Data Flow Example

### Scenario: Employee visits LinkedIn profile

```
STEP 1: Browser Activity
┌─────────────────────────────────────────┐
│ User opens: https://www.linkedin.com/in │
│            /johndoe/                    │
│ Browser title: "John Doe - LinkedIn - C │
│                hrome"                   │
└─────────────────────────────────────────┘
                    ↓
STEP 2: URL Detection
┌──────────────────────────────────────────┐
│ detect_domain(title) extracts:           │
│  domain: "linkedin.com"                  │
│  url: "https://www.linkedin.com/in/john │
│       doe/"                              │
└──────────────────────────────────────────┘
                    ↓
STEP 3: Database Storage
┌──────────────────────────────────────────┐
│ INSERT INTO website_usages VALUES        │
│  employee_id: 1                          │
│  domain: "linkedin.com"                  │
│  url: "https://www.linkedin.com/in/john │
│       doe/"                              │
│  active_seconds: 1200                    │
│  created_at: "2026-01-28 14:30:00"       │
└──────────────────────────────────────────┘
                    ↓
STEP 4: Report Generation
┌──────────────────────────────────────────┐
│ SELECT url FROM core_websiteusage WHERE  │
│  domain = "linkedin.com"                 │
│ Returns:                                 │
│ "https://www.linkedin.com/in/johndoe/"   │
└──────────────────────────────────────────┘
                    ↓
STEP 5: Display in Report
┌──────────────────────────────────────────┐
│ Rank: 15                                 │
│ Domain: linkedin.com                     │
│ URL: https://www.linkedin.com/in/johndoe │
│      [Click to visit]                    │
│ Employee: John Doe                       │
│ Time: 20m 0s                             │
└──────────────────────────────────────────┘
```

---

## 🎯 Where URLs Are Displayed

### 1️⃣ Reports Page (`/admin/reports/top-apps/`)
```
Top Websites Report
├─ Global Top Websites (clickable)
├─ Detailed Website Usage by Employee
│  ├─ Rank: 1
│  ├─ Domain: facebook.com
│  ├─ URL: https://www.facebook.com/photo/?fbid=... ← CLICKABLE
│  ├─ Employee: Pran
│  └─ Time: 2h 30m
```

### 2️⃣ Session Details (`/admin/sessions/<id>/`)
```
Work Session Details
├─ Website Usage
│  ├─ Domain: facebook.com
│  ├─ URL: https://www.facebook.com/photo/?... ← CLICKABLE
│  └─ Time: 30m 45s
```

### 3️⃣ Reports PDF/Print
```
[When you print or export as PDF]
All URLs remain visible and clickable
```

---

## 🔍 URL Examples by Category

### Social Media 👥
```
Facebook:    https://www.facebook.com/photo/?fbid=...
LinkedIn:    https://www.linkedin.com/in/username/
Instagram:   https://www.instagram.com/username/
Twitter:     https://twitter.com/username/status/123
```

### Productivity 📝
```
Google Docs:  https://docs.google.com/document/d/abc/edit
Google Sheet: https://sheets.google.com/d/xyz/edit
Trello:       https://trello.com/b/board_id/board
Notion:       https://www.notion.so/page_hash
```

### Development 👨‍💻
```
GitHub PR:     https://github.com/user/repo/pull/42
GitHub Issue:  https://github.com/user/repo/issues/123
StackOverflow: https://stackoverflow.com/questions/123
NPM Package:   https://npm.js.org/package/name
```

### Communication 💬
```
Gmail:        https://mail.google.com/mail/u/0/#inbox
Slack:        https://slack.com/app/123/messages
Zoom:         https://zoom.us/j/meeting_id
Teams:        https://teams.microsoft.com/l/message/
```

---

## 🛠️ Technical Details

### Database Column Added
```sql
ALTER TABLE core_websiteusage
ADD COLUMN url TEXT NULL;

Type:       TEXT (unlimited length)
Default:    NULL (backward compatible)
Nullable:   YES
Indexed:    NO
```

### API Data Structure
```json
{
  "websites": [
    {
      "domain": "facebook.com",
      "active_seconds": 300,
      "created_at": "2026-01-28 14:30:00"
    }
  ]
}
```

**New:** URL field is captured in desktop app and sent to server

### URL Storage Location
```
Desktop (SQLite):
  Database: hrsoftbdTracker.db
  Table: website_usages
  Columns: company_id, employee_id, domain, url, active_seconds

Server (Django PostgreSQL/SQLite):
  Model: core.WebsiteUsage
  Fields: domain, url, active_seconds, employee, work_session
```

---

## ✨ Key Features

| Feature | Status | Notes |
|---------|--------|-------|
| **Capture Full URLs** | ✅ Active | With query parameters |
| **Store Complete URLs** | ✅ Active | In database |
| **Display URLs** | ✅ Active | In reports & session details |
| **Clickable Links** | ✅ Active | Opens in new tab |
| **Query Parameters** | ✅ Active | `?id=`, `?fbid=`, etc. |
| **Word Wrapping** | ✅ Active | Long URLs wrap properly |
| **Print Support** | ✅ Active | Visible in PDF/Print |
| **Mobile Responsive** | ✅ Active | Works on all devices |
| **Backward Compatible** | ✅ Active | Old records still work |

---

## 🚀 Getting Started

### Step 1: Restart Application
```bash
# Kill existing process
Ctrl+C

# Start fresh
python manage.py runserver 0.0.0.0:8000  # Backend
python main.py                            # Desktop app
```

### Step 2: Test URL Capture
1. Open desktop app
2. Visit websites in browser
3. Watch URLs being captured
4. Check database: `website_usages` table

### Step 3: View in Reports
1. Go to: http://localhost:8000/admin/reports/top-apps/
2. Look for "Detailed Website Usage by Employee"
3. See full URLs with clickable links
4. Click to verify URLs work

### Step 4: Check Session Details
1. Go to: http://localhost:8000/admin/sessions/
2. Click "Details" on any session
3. View "Website Usage" section
4. See full URLs with links

---

## 🔧 Customization Options

### If you want to change something:

**Change top websites count:**
```python
# In web_views.py, report_top_apps_view()
.order_by('-total_time')[:50]  # Change 50 to desired number
```

**Change URL display format:**
```html
<!-- In templates, change how URL is shown -->
<small class="text-muted">{{ site.url }}</small>
```

**Add URL filtering:**
```python
# Filter by URL pattern
detailed_sites = WebsiteUsage.objects.filter(
    url__contains='facebook.com'
)
```

---

## ⚠️ Important Notes

1. **First time data**: New full URLs only start after restart
2. **Old records**: Will show constructed URLs (https://domain)
3. **Long URLs**: May need scrolling in some views
4. **Privacy**: Store complete URLs with care
5. **Performance**: No impact on system performance

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| URLs showing as blank | Restart app, old records will show constructed URLs |
| URLs not clickable | Check browser allows opening links |
| Long URLs cut off | They wrap with word-break styling |
| Old records missing URLs | System constructs from domain |
| URLs not captured | Ensure desktop app is running |

---

## 📚 Related Files

### Documentation
- `FULL_URL_TRACKING_IMPLEMENTATION.md` - Technical details
- `IMPLEMENTATION_SUMMARY.md` - Feature overview
- `CODE_CHANGES_DETAILED.md` - Code comparisons
- `IMPLEMENTATION_CHECKLIST.md` - Verification checklist

### Code Files Modified
- `backend/core/models.py` - Model update
- `tracker/activity_tracker.py` - Detection logic
- `backend/templates/report_top_apps.html` - Report display
- `backend/templates/session_detail.html` - Session display

### Database
- Migration: `0005_websiteusage_url.py`
- Status: ✅ Applied

---

## 🎉 You're All Set!

Everything is ready to use. Just start the application and visit some websites to see full URL tracking in action!

**Questions?** Check the detailed documentation files.
