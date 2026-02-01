# 🎯 Phase 2 Quick Reference - Admin Dashboard Features

## 🚀 What Was Added

Phase 2 adds **4 powerful admin features** to manage employee tracking and view audit history.

---

## 📋 Feature #1: Tracking Policy Configuration

### 🔗 Access
- **URL**: `/policy/`
- **Menu**: Sidebar → Configuration → Tracking Policy
- **Required Role**: ADMIN or OWNER

### 💡 What You Can Do
1. **Enable/Disable Screenshots**
   - Toggle screenshot capture on/off
   - Set capture interval (30-3600 seconds)
   - Default: Every 10 minutes

2. **Enable/Disable Website Tracking**
   - Monitor which websites employees visit
   - Track productivity on web-based tools
   - Default: Enabled

3. **Enable/Disable Application Tracking**
   - Monitor which desktop apps employees use
   - Track time spent in each application
   - Default: Enabled

4. **Configure Idle Detection**
   - Set idle threshold (10-600 seconds)
   - After this time of no keyboard/mouse, mark as idle
   - Default: 5 minutes

### 💾 How to Use
```
1. Go to /policy/
2. Toggle each feature on/off
3. Enter new intervals if needed
4. Click "Save Policy Settings"
5. Changes apply within 1 hour
6. Action logged to audit trail
```

### 📊 What Gets Logged
```json
{
  "action_type": "POLICY_CHANGED",
  "description": "Company tracking policy updated",
  "details": {
    "screenshots": true,
    "website_tracking": true,
    "app_tracking": true,
    "screenshot_interval": 600,
    "idle_threshold": 300
  }
}
```

---

## 📜 Feature #2: Audit Log Viewer

### 🔗 Access
- **URL**: `/audit-logs/`
- **Menu**: Sidebar → Configuration → Audit Logs
- **Required Role**: ADMIN or OWNER

### 💡 What You Can Do
1. **View All Actions**
   - See every admin action in chronological order
   - 20 logs per page
   - View total count

2. **Filter by Action Type**
   - COMPANY_CREATED
   - COMPANY_SUSPENDED / REACTIVATED
   - PLAN_CHANGED
   - POLICY_CHANGED
   - EMPLOYEE_ADDED / REMOVED / ACTIVATED / DEACTIVATED
   - KEY_ROTATED
   - And more...

3. **Filter by User**
   - Select which admin's actions to view
   - See only actions by specific person

4. **Filter by Date Range**
   - From date: Start of range
   - To date: End of range
   - Default: All dates

5. **Full-Text Search**
   - Search in log description
   - Search in username
   - Case-insensitive

6. **View Details**
   - Click "View Details" button
   - See complete JSON with changes made
   - Know exactly what was modified

### 💾 How to Use
```
1. Go to /audit-logs/
2. (Optional) Select filters:
   - Action Type
   - User
   - From Date
   - To Date
3. Click "Filter"
4. Click "View Details" on any log
5. See complete action details in modal
```

### 📊 Action Types Logged
| Action | Who Can Do | Details Logged |
|--------|-----------|-----------------|
| POLICY_CHANGED | Admin | All policy changes |
| EMPLOYEE_DEACTIVATED | Admin | Employee ID, status |
| EMPLOYEE_REACTIVATED | Admin | Employee ID, status |
| COMPANY_CREATED | Owner | Plan, status |
| COMPANY_SUSPENDED | Owner | Reason |
| KEY_ROTATED | Owner | Masked keys |

### 🔐 Data Captured
- **Who**: Username of person who did action
- **What**: Description of action
- **When**: Exact timestamp with date/time
- **Where**: IP address of person
- **Details**: JSON with specific changes

---

## 📡 Feature #3: Agent Sync Status

### 🔗 Access
- **URL**: `/agent-sync-status/`
- **Menu**: Sidebar → Monitoring → Agent Status
- **Required Role**: ADMIN, MANAGER, or OWNER

### 💡 What You Can Do
1. **See Summary**
   - Total employees
   - Online count (synced in last 15 min)
   - Offline count (15+ min without sync)
   - Never synced count (new agents)

2. **View Online Agents**
   - Green "Online" badge
   - Name, username, email
   - Last sync time
   - Minutes since last sync

3. **View Offline Agents**
   - Yellow "Offline" badge
   - Last sync time
   - How long offline
   - "Notify" button to email employee

4. **View Never-Synced Agents**
   - Red "Never Synced" badge
   - Likely just created account
   - "Contact" button to send email
   - Need to install/start agent app

### 💾 How to Use
```
1. Go to /agent-sync-status/
2. See summary cards at top
3. Scroll down to view employees by status
4. (Optional) Click "Notify" to email offline employee
5. (Optional) Click "Contact" to email never-synced employee
6. Employee opens email and starts agent app
```

### 🟢 Status Indicators
- **Green (Online)**: Agent synced in last 15 minutes - tracking active
- **Yellow (Offline)**: Agent hasn't synced for 15+ minutes - may be paused
- **Red (Never)**: Employee account exists but agent never connected - needs setup

### 📊 Typical Flow
```
Employee hired → Create account (status: Never Synced)
               ↓
               Employee installs agent app
               ↓
               Agent connects to server (status: Online)
               ↓
               Agent syncs every 5 minutes (stays Online)
               ↓
               Employee closes agent app (status: Offline after 15 min)
               ↓
               Admin clicks "Notify" (sends email)
               ↓
               Employee restarts agent (status: Online again)
```

---

## 🔌 Feature #4: Dashboard Alerts API

### 🔗 Access
- **URL**: `/api/dashboard-alerts/`
- **HTTP Method**: GET
- **Required Auth**: Login + Company Key or Token

### 💡 What You Get
JSON response with alerts for dashboard display:

```json
{
  "status": "success",
  "offline_agents_count": 2,
  "offline_agents": [
    {
      "id": 5,
      "username": "john_doe",
      "email": "john@company.com",
      "last_agent_sync_at": "2026-02-02T12:30:00Z"
    },
    ...
  ],
  "never_synced_count": 1,
  "never_synced_agents": [
    {
      "id": 8,
      "username": "jane_smith",
      "email": "jane@company.com"
    }
  ],
  "recent_audit_logs": [
    {
      "id": 1,
      "action_type": "POLICY_CHANGED",
      "description": "Company tracking policy updated",
      "timestamp": "2026-02-02T18:00:00Z",
      "user__username": "admin_user"
    },
    ...
  ]
}
```

### 💾 Usage
Perfect for:
- Dashboard widgets showing alerts
- Real-time notification system
- Admin mobile app
- Custom dashboards
- Integration with other tools

### 🔄 Example Usage
```javascript
// Fetch alerts every 5 minutes
fetch('/api/dashboard-alerts/', {
  headers: {
    'X-Company-Key': 'your_company_key',
    'Authorization': 'Token your_token'
  }
})
.then(r => r.json())
.then(data => {
  // Update dashboard with offline agent count
  document.getElementById('offline-count').textContent = 
    data.offline_agents_count;
  
  // Show warning if offline agents
  if (data.offline_agents_count > 0) {
    showWarning('Some agents are offline!');
  }
});
```

---

## 🎯 Common Admin Tasks

### Task: Change Screenshot Interval
```
1. Go to /policy/
2. Find "Capture Interval (seconds)"
3. Change value (e.g., 300 for 5 minutes)
4. Click "Save Policy Settings"
5. Agents fetch new policy within 1 hour
```

### Task: Check Who Changed Company Policy
```
1. Go to /audit-logs/
2. Filter by Action Type: "POLICY_CHANGED"
3. Review all policy modifications
4. Click "View Details" to see what was changed
```

### Task: Monitor Agent Health
```
1. Go to /agent-sync-status/
2. Check "Offline (15+ min)" count
3. If > 0, click "Notify" on each
4. Employees get email asking them to check agent
```

### Task: Review Yesterday's Audit Log
```
1. Go to /audit-logs/
2. Set From Date: Yesterday's date
3. Set To Date: Yesterday's date
4. Click Filter
5. Review all actions from that day
```

### Task: Find All Employee Deactivations
```
1. Go to /audit-logs/
2. Filter by Action Type: "EMPLOYEE_DEACTIVATED"
3. See all employees who were deactivated
4. Click Details to see when/by whom/why
```

---

## ⚙️ Configuration Recommendations

### For Production Environment

**Screenshot Interval**: 600 seconds (10 minutes)
- Balances documentation with resource usage
- Not too intrusive
- Captures most activities

**Idle Threshold**: 300 seconds (5 minutes)
- Standard for productivity tracking
- Allows short breaks without marking idle
- Reasonable for most work styles

**Tracking Enabled**: All three on
- Screenshots: YES (visual evidence)
- Website: YES (productivity tracking)
- App: YES (software usage tracking)

### For Compliance/Legal
- Keep all features ON
- Take screenshots more frequently (300s)
- Lower idle threshold (180s)
- Retain logs for 90+ days (default)

### For Cost Reduction
- Disable screenshots (save storage)
- Keep website/app tracking (minimal cost)
- Increase idle threshold (600s)
- Reduce screenshot retention (30 days)

---

## 🔐 Security Notes

All admin actions are logged:
- ✅ IP address captured
- ✅ Timestamp recorded
- ✅ User identified
- ✅ Action details saved
- ✅ Logs are immutable

Admin best practices:
- ✅ Don't share your login
- ✅ Check audit logs regularly
- ✅ Monitor offline agents
- ✅ Keep policies consistent

---

## 🆘 Troubleshooting

### Problem: Can't see "Tracking Policy" in sidebar
**Solution**: You need ADMIN or OWNER role. Ask owner to give you admin access.

### Problem: Policy changes aren't taking effect
**Solution**: Agents check for policy updates every hour. Wait up to 1 hour, or have employee restart their agent app.

### Problem: Agents showing as offline but they're at their desk
**Solution**: 
1. Ask employee to check if agent app is running
2. Ask them to restart the app
3. Check if their network is blocked
4. Check server logs for connection errors

### Problem: Can't see audit logs
**Solution**: You need ADMIN or OWNER role. Only see logs for your company.

### Problem: Audit logs don't show my action
**Solution**: 
1. Logs update in real-time - refresh page
2. Check if you're filtering correctly
3. Make sure you're in correct company
4. Check "All Actions" first to see if log exists

---

## 📚 Related Features from Phase 1

Phase 2 builds on Phase 1:
- **CompanyPolicy Model**: Stores tracking settings
- **AuditLog Model**: Stores all admin actions
- **User.last_agent_sync_at**: Tracks agent connectivity
- **Agent Heartbeat**: Agents sync with `/api/agent/heartbeat/`
- **Agent Policy Fetch**: Agents GET from `/api/policy/`

---

## 🎓 Learning Resources

### For Admins
- [PHASE2_COMPLETE_SUMMARY.md](PHASE2_COMPLETE_SUMMARY.md) - Full technical details
- [PHASE1_QUICK_REFERENCE.md](PHASE1_QUICK_REFERENCE.md) - Phase 1 features

### For Managers
- Check Agent Status daily
- Monitor offline agents
- Review audit logs weekly

### For Business
- Use Policy to control tracking level
- Use Audit Logs for compliance
- Use Alerts for team health monitoring

---

**Phase 2 is production-ready and deployed!** 🚀

Questions? Check the full documentation or contact your administrator.
