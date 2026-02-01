# 📊 Role Comparison - Owner vs Admin vs Employee

## System Architecture (Clear & Detailed)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                          ROLE HIERARCHY                                      ║
╚══════════════════════════════════════════════════════════════════════════════╝

                              🏆 SOFTWARE OWNER
                          (Ayman - Software Creator)
                    Controls entire SaaS platform & all companies
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                 Company A       Company B       Company N
                  (ABC Tech)      (XYZ Corp)     (Tech Inc)
                   ACTIVE          TRIAL         SUSPENDED
                    │               │               │
            ┌───────┴─────────┐     │     ┌────────┴───────┐
            │                 │     │     │                │
         👤 ADMIN         👤 ADMIN 👤ADMIN           👤 ADMIN
    (Company Manager)  (Suspended)            (Can't login)
            │
    ┌───────┼───────┬────────┐
    │       │       │        │
   👨👨👨👨👨
  EMP1 EMP2 EMP3 EMP4 EMP5
  (Desktop App Users)
```

---

## 🔐 Access Control Matrix

### OWNER (Software Owner / Super Admin) - Role: 'OWNER'

**Can Access:**
```
Dashboard:
  ✅ /api/owner/dashboard/
  ✅ /api/owner/company/{id}/
  ✅ /api/owner/reports/

Actions:
  ✅ Create new companies
  ✅ Change subscription plans
  ✅ Suspend companies
  ✅ Reactivate companies
  ✅ Rotate API keys
  ✅ View analytics & reports

Data Visible:
  ✅ Company names & emails
  ✅ Subscription plans & dates
  ✅ Aggregate usage stats (total minutes, screenshots, storage)
  ✅ Last sync timestamps
  ✅ Employee count (number only, no names)
  ✅ Seat usage (15/25, not individual employees)
```

**Cannot Access:**
```
  ❌ /api/dashboard/admin/  (Admin panel)
  ❌ /api/employees/        (Employee management)
  ❌ /api/sessions/         (Session details)
  ❌ /api/screenshots/      (Screenshot gallery)
  ❌ /api/tasks/            (Tasks)

Data NOT Visible:
  ❌ Employee names or emails
  ❌ Individual work sessions
  ❌ Screenshots/thumbnails
  ❌ Visited websites/domains
  ❌ Used applications
  ❌ Active/idle activity per employee
  ❌ Tasks or assignments
  ❌ Any personal employee data
```

---

### ADMIN (Company Admin) - Role: 'ADMIN'

**Can Access:**
```
Dashboard:
  ✅ /api/dashboard/admin/
  ✅ /api/employees/
  ✅ /api/sessions/
  ✅ /api/screenshots/
  ✅ /api/reports/
  ✅ /api/tasks/

Actions:
  ✅ Create/edit/delete employees
  ✅ View all employee data
  ✅ Manage work sessions
  ✅ View all screenshots
  ✅ Generate reports
  ✅ Assign tasks
  ✅ Change company settings
  ✅ Access all employee tracking data

Data Visible:
  ✅ ALL employee names & emails
  ✅ ALL work sessions
  ✅ ALL screenshots
  ✅ ALL visited websites
  ✅ ALL used applications
  ✅ Activity logs (active/idle per employee)
  ✅ Task assignments
  ✅ Company settings & branding
  ✅ Detailed employee reports
```

**Cannot Access:**
```
  ❌ /api/owner/dashboard/   (Owner panel)
  ❌ /api/owner/reports/     (Owner analytics)
  ❌ Suspend own company
  ❌ Change own plan
  ❌ Rotate own API key
  ❌ View other companies
  ❌ Manage other companies' data
```

---

### EMPLOYEE (Tracked Employee) - Role: 'EMPLOYEE'

**Can Access:**
```
Dashboard:
  ✅ /api/dashboard/user/
  ✅ /api/my-reports/
  ✅ Desktop tracking app

Actions:
  ✅ Start/stop work sessions
  ✅ View own tasks
  ✅ Mark tasks complete
  ✅ Update own profile
  ✅ View own reports (limited)
  ✅ Change own password
  ✅ View own activity summary (limited)

Data Visible (Self Only):
  ✅ Own tasks assigned
  ✅ Own work hours summary
  ✅ Own activity (high level only)
  ✅ Own employee profile
```

**Cannot Access:**
```
  ❌ /api/admin/dashboard/   (Admin panel)
  ❌ /api/owner/dashboard/   (Owner panel)
  ❌ /api/employees/         (Other employees)
  ❌ /api/sessions/          (Other sessions)
  ❌ /api/screenshots/       (Any screenshots)
  ❌ /api/reports/           (Company reports)

Data NOT Visible:
  ❌ Other employees' data
  ❌ Any screenshots
  ❌ Admin reports
  ❌ Company settings
  ❌ Financial/billing info
  ❌ Other employees' tasks
```

---

## 📋 Detailed Comparison Table

| Feature | Owner | Admin | Employee |
|---------|-------|-------|----------|
| **Company Management** |
| View companies | ✅ All | ✅ Own | ❌ |
| Create company | ✅ | ❌ | ❌ |
| Change plan | ✅ | ❌ | ❌ |
| Suspend company | ✅ | ❌ | ❌ |
| Rotate API key | ✅ | ❌ | ❌ |
| **Employee Management** |
| View all employees | ⚪ Count only | ✅ With details | ❌ |
| Create employee | ❌ | ✅ | ❌ |
| Edit employee | ❌ | ✅ | ✅ Own |
| Delete employee | ❌ | ✅ | ❌ |
| **Activity Tracking** |
| View sessions | ⚪ Count only | ✅ All details | ✅ Own only |
| End sessions | ❌ | ✅ | ❌ |
| View screenshots | ❌ | ✅ | ❌ |
| View app usage | ⚪ Count only | ✅ Detailed | ❌ |
| View website usage | ⚪ Count only | ✅ Detailed | ❌ |
| **Reporting** |
| Company reports | ⚪ Aggregate | ✅ Detailed | ❌ |
| Employee reports | ❌ | ✅ | ✅ Personal |
| Task reports | ❌ | ✅ | ✅ Personal |
| **Settings** |
| Company branding | ❌ | ✅ | ❌ |
| Security settings | ❌ | ✅ | ❌ |
| Billing/Plan | ✅ | ❌ | ❌ |
| **Data Access** |
| Storage limit | ✅ Manage | ✅ Use | ✅ Limited |
| API access | ✅ Manage | ✅ Use | ❌ |

Legend: ✅ = Full Access, ⚪ = Aggregate Only, ❌ = No Access

---

## 🔍 Detailed Permission Breakdown

### OWNER Permissions

```json
{
  "owner_panel": true,
  "can": [
    "view_all_companies",
    "create_company",
    "change_company_plan",
    "suspend_company",
    "reactivate_company",
    "rotate_api_key",
    "view_analytics",
    "view_reports"
  ],
  "can_see_aggregate": [
    "total_active_minutes_30d",
    "total_screenshots_30d",
    "total_storage_gb",
    "employee_count",
    "session_count",
    "last_sync"
  ],
  "cannot": [
    "view_employee_names",
    "view_employee_emails",
    "view_individual_sessions",
    "view_screenshots",
    "view_website_visits",
    "view_app_usage",
    "view_activity_logs",
    "manage_employees",
    "view_tasks",
    "access_company_admin_panel"
  ]
}
```

### ADMIN Permissions

```json
{
  "admin_panel": true,
  "can": [
    "view_all_employees",
    "create_employee",
    "edit_employee",
    "delete_employee",
    "view_all_sessions",
    "end_sessions",
    "view_all_screenshots",
    "view_app_usage",
    "view_website_usage",
    "manage_tasks",
    "generate_reports",
    "change_company_settings",
    "change_company_branding"
  ],
  "can_see": [
    "employee_names",
    "employee_emails",
    "individual_sessions",
    "screenshots",
    "website_visits",
    "app_usage",
    "activity_logs",
    "tasks",
    "company_settings"
  ],
  "cannot": [
    "access_owner_panel",
    "create_company",
    "change_plan",
    "suspend_company",
    "view_other_companies",
    "manage_billing",
    "rotate_api_key"
  ]
}
```

### EMPLOYEE Permissions

```json
{
  "user_panel": true,
  "can": [
    "start_work_session",
    "stop_work_session",
    "view_own_tasks",
    "update_task_status",
    "view_own_reports",
    "update_own_profile",
    "change_own_password",
    "run_desktop_app",
    "sync_activity_data"
  ],
  "can_see": [
    "own_tasks",
    "own_work_summary",
    "own_reports",
    "own_profile"
  ],
  "cannot": [
    "access_admin_panel",
    "access_owner_panel",
    "view_other_employees",
    "view_other_sessions",
    "view_screenshots",
    "view_company_reports",
    "manage_settings",
    "view_tasks",
    "manage_employees"
  ]
}
```

---

## 🔄 Data Flow Visualization

```
OWNER (Ayman) - /api/owner/dashboard/
    │
    ├─ Creates Company A
    │   └─ Generates: company_key, admin_user, trial_period
    │
    ├─ Company A Admin (Bob)
    │   │
    │   ├─ Creates Employee 1 (John)
    │   │   └─ Employee 1 runs desktop app
    │   │       └─ Desktop sends: activity, screenshots, usage
    │   │           └─ Data stored in: CompanyUsageDaily (aggregate)
    │   │
    │   └─ Admin Views: All employee data in /api/dashboard/admin/
    │       └─ Can see: screenshots, sessions, activity logs
    │
    └─ Owner Only Sees: CompanyUsageDaily aggregate
        └─ Example: "Company A: 1250 minutes, 45 screenshots, 2.3GB"
        └─ Does NOT see: "John did X, visited Y, used Z"
```

---

## 🎯 Security Implications

### Owner Perspective
- ✅ Cannot spy on customers' employees
- ✅ Cannot see personal data
- ✅ Can only see business metrics
- ✅ Good for privacy compliance (GDPR, etc)
- ✅ Can still manage subscriptions effectively

### Admin Perspective
- ✅ Has full control within company
- ✅ Can monitor all employees
- ✅ Cannot interfere with other companies
- ✅ Cannot change own plan/suspension
- ✅ Responsible for employee data

### Employee Perspective
- ✅ Desktop app only tracks what's needed
- ✅ Cannot access admin/owner data
- ✅ Can only see own tasks & reports
- ✅ Privacy protected from other employees
- ✅ Knows admin can see their activity

---

## 📞 FAQ

### Q: Can Owner see employee screenshots?
**A:** No. Owner can only see count (e.g., "45 screenshots"), not the images.

### Q: Can Admin suspend the company?
**A:** No. Only Owner can suspend. Admin can only manage employees.

### Q: Can Employee see other employee's tasks?
**A:** No. Employee can only see own tasks.

### Q: Can Owner change Employee passwords?
**A:** No. Only Admin can. Owner cannot access employee management.

### Q: What if Admin leaves?
**A:** Owner can create new admin, but must go through Admin panel first.

### Q: Can Owner rotate API key?
**A:** Yes. Owner can rotate any company's key for security.

### Q: Can Admin view Owner reports?
**A:** No. Admin reports and Owner reports are completely separate.

---

## ✅ This Design Ensures

1. **Privacy**: Employee data stays within company
2. **Security**: Separate dashboards prevent data leaks
3. **Scalability**: Owner can manage unlimited companies
4. **Compliance**: GDPR/privacy-friendly architecture
5. **Audit Trail**: Each role has specific permissions
6. **Business Logic**: Roles map to real-world responsibilities

