# 🎯 Complete Business Workflow - Owner → Admin → Employee

## Overview

This document explains the complete workflow from **Owner** creating a company, through **Company Admin** managing employees, to **Employees** using the desktop software.

## Workflow Steps

### 1️⃣ OWNER: Creates a Company

**What Owner Does:**
1. Login to Owner Portal: `http://localhost:8000/admin/login/`
   - Username: `ayman`
   - Password: `12345`

2. Click "Create New Company (Trial)" button in Dashboard

3. Fill in company details:
   - Company Name (required)
   - Email (optional)
   - Contact Person (optional)
   - Contact Phone (optional)
   - Select Plan (required)

4. Click "Create Company"

**System Automatically:**
- ✅ Creates new Company record
- ✅ Assigns trial plan (30 days free)
- ✅ Generates unique `company_key` for desktop app identification
- ✅ **AUTO-CREATES ADMIN ACCOUNT** with:
  - Unique username (e.g., `acme_corp_admin`)
  - Secure random password (10 characters, mixed letters/numbers/symbols)
  - Email address
  - Role: ADMIN
  - Linked to created company

5. **Displays credentials page** showing:
   - Company information
   - Admin username
   - Admin email
   - Admin password (auto-generated, temporary)
   - Login instructions
   - Next steps guide

**Owner's Task:**
- Save/print the admin credentials securely
- Share them with the company administrator

---

### 2️⃣ COMPANY ADMIN: Logs In & Creates Employees

**What Admin Does:**

1. **Login with provided credentials:**
   - URL: `http://localhost:8000/login/`
   - Username: (from credentials page, e.g., `acme_corp_admin`)
   - Password: (from credentials page)
   - Click "Sign In"

2. **First Time Setup:**
   - Dashboard loads showing "Manage Your Company"
   - Should change password immediately (optional but recommended)
   - Visit Settings to configure company branding/policies (optional)

3. **Create Employee Accounts:**
   - Navigate to "Employees" section
   - Click "Add Employee" button
   - Fill in employee details:
     - Name (required)
     - Email (required)
     - Username (auto-generated or custom)
     - Password (system-generated or custom)
     - Department (optional)
     - Designation (optional)
   - Click "Create Employee"

4. **Repeat for all team members** who need to use the software

**System Creates:**
- ✅ Employee User account with role='EMPLOYEE'
- ✅ Links employee to the company
- ✅ Generates unique `tracker_token` for desktop app authentication
- ✅ Employee becomes available for desktop software login

**Admin's Permissions (within their company only):**
- ✅ View all employees
- ✅ Create/edit/delete employees
- ✅ Reset employee passwords
- ✅ View productivity reports for all employees
- ✅ View screenshots/sessions/activity logs
- ✅ Configure company policies
- ✅ Manage company settings/branding
- ❌ Cannot see other companies' data
- ❌ Cannot see OWNER level analytics

---

### 3️⃣ EMPLOYEE: Uses Desktop Software

**What Employee Does:**

1. **Download & Install Desktop App**
   - Available at: Company's software portal or direct download link

2. **Login with provided credentials:**
   - Username/Email: (from admin)
   - Password: (from admin)
   - OR
   - Use `tracker_token` if configured

3. **System Validates:**
   - ✅ Checks if user exists in database
   - ✅ Checks if employee role='EMPLOYEE'
   - ✅ Checks if employee belongs to an active company
   - ✅ Checks if company has active subscription
   - ⚠️ **FAILS if:**
     - Employee doesn't exist (Admin hasn't created yet)
     - Company is suspended
     - Company's trial has expired
     - Company has no active subscription

4. **Desktop App Features Available:**
   - ✅ Track application usage
   - ✅ Capture screenshots
   - ✅ Log work sessions
   - ✅ Send activity data to server
   - ✅ View assigned tasks
   - ✅ Update task status

5. **Data Syncs to Server:**
   - Screenshots → Database
   - Activity logs → Work sessions
   - App usage data → Application usage records
   - All data categorized by employee and company

---

## Critical Business Rules

### ✅ Must Follow This Sequence:
```
1. Owner creates company
   ↓
2. System auto-creates admin account
   ↓
3. Admin receives credentials & logs in
   ↓
4. Admin creates employee accounts
   ↓
5. Employees can now use desktop software
```

### ❌ What FAILS if Skipped:
- Employees cannot login without being created by Admin
- Desktop app won't sync if company doesn't exist
- Desktop app won't work if company is suspended
- Data won't be visible if employee isn't linked to company

### 🔐 Security Model:

```
┌─────────────────────────────────────────┐
│     OWNER (ayman)                       │
│  - See all companies                    │
│  - Manage company lifecycle             │
│  - See aggregated stats only            │
│  - CANNOT see employee data             │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│     COMPANY ADMIN (auto-created)        │
│  - Manage own company only              │
│  - Create/manage employees              │
│  - View all employee data               │
│  - Configure company settings           │
│  - CANNOT see other companies           │
│  - CANNOT see owner data                │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│     EMPLOYEE (created by admin)         │
│  - Use desktop software                 │
│  - See own data only                    │
│  - View own tasks                       │
│  - Submit work sessions                 │
│  - CANNOT see other employees' data     │
└─────────────────────────────────────────┘
```

---

## Data Flow Example

```
OWNER: Ayman (username: ayman)
  │
  └─→ Creates Company: "Acme Corp"
      │
      ├─→ Auto-creates Admin: "acme_corp_admin"
      │   Password: "X#7k9Lm2"
      │
      └─→ Admin logs in & creates Employees:
          │
          ├─→ Employee: John (john@acme.com)
          │   │
          │   └─→ Desktop App
          │       └─→ Tracks: Apps, Screenshots, Sessions
          │           └─→ Syncs to: Employee data (John's activities)
          │               └─→ Visible to: Admin & Owner (aggregated)
          │
          └─→ Employee: Sarah (sarah@acme.com)
              │
              └─→ Desktop App
                  └─→ Tracks: Apps, Screenshots, Sessions
                      └─→ Syncs to: Employee data (Sarah's activities)
                          └─→ Visible to: Admin & Owner (aggregated)

RESULT:
- Admin sees: All employees' data, detailed reports
- Owner sees: Company aggregate "Acme Corp: 1000 minutes, 45 screenshots"
- Owner CANNOT see: Individual employee details, screenshots, app names
```

---

## URLs Reference

### Owner URLs
- Login: `/admin/login/`
- Dashboard: `/owner/dashboard/`
- Create Company: `/owner/company/create/`
- **New: Credentials** (auto-redirect): `/owner/company/credentials/`
- Company Details: `/owner/company/<id>/`
- Edit Company: `/owner/company/<id>/edit/`
- Delete Company: `/owner/company/<id>/delete/`
- Reports: `/owner/reports/`

### Admin URLs (Company-specific)
- Login: `/login/`
- Dashboard: `/dashboard/admin/`
- Employees: `/employees/`
- Add Employee: `/employees/add/`
- Reports: `/reports/`
- Settings: `/settings/`

### Employee URLs
- Login: `/signin/`
- Dashboard: `/dashboard/user/`
- My Reports: `/my-reports/`
- Sessions: `/sessions/`
- Tasks: `/tasks/`

---

## Implementation Details

### Admin Account Auto-Creation

When Owner creates a company via `POST /owner/company/create/`:

```python
# 1. Generate unique admin username
admin_username = f"{company_name.lower().replace(' ', '_')}_admin"
# Example: "Acme Corp" → "acme_corp_admin"

# 2. Generate secure random password
# 10 characters, mix of: letters, numbers, symbols (!@#$%)
import string, secrets
password_chars = string.ascii_letters + string.digits + "!@#$%"
admin_password = ''.join(secrets.choice(password_chars) for _ in range(10))

# 3. Create admin user
admin_user = User.objects.create_user(
    username=admin_username,
    email=contact_person or f"admin@{company_name}.local",
    password=admin_password,
    role='ADMIN',  # ← Company Admin role
    company=company,  # ← Link to company
    is_active=True
)

# 4. Store in session & redirect to credentials page
# Credentials page displays username/password/email with copy buttons
```

### Employee Creation by Admin

When Admin creates employee via `POST /employees/add/`:

```python
# 1. Create user with role='EMPLOYEE'
employee = User.objects.create_user(
    username=username,
    email=email,
    password=password,
    role='EMPLOYEE',  # ← Employee role
    company=admin.company,  # ← Same company as admin
    is_active=True
)

# 2. Generate tracker token (for desktop app)
employee.tracker_token = str(uuid.uuid4())
employee.save()

# 3. Employee is now ready for desktop software login
```

### Desktop App Validation

When Employee logs in via desktop app:

```python
# Check 1: User exists with role='EMPLOYEE'
user = User.objects.get(username=username, role='EMPLOYEE')

# Check 2: Employee belongs to a company
if not user.company:
    raise AuthError("Employee not linked to company")

# Check 3: Company exists and is active
company = user.company
if company.status == 'SUSPENDED':
    raise AuthError("Company is suspended")

# Check 4: Company has active subscription
if not company.is_active_subscription():
    raise AuthError("Company subscription expired")

# ✅ All checks passed → Login allowed
# Desktop app can now:
# - Track employee activity
# - Upload screenshots
# - Send work session data
```

---

## Testing the Workflow

### Step 1: Owner Creates Company
```
1. Open: http://localhost:8000/admin/login/
2. Login: ayman / 12345
3. Click: "Create New Company (Trial)"
4. Fill: Name=TestCorp, Email=test@testcorp.com, Plan=Free
5. Click: Create Company
6. See: Credentials page with admin details
7. Screenshot: Admin username & password
```

### Step 2: Admin Logs In
```
1. Open: http://localhost:8000/login/
2. Login: {admin_username} / {admin_password}
3. See: Admin Dashboard
4. Navigate: Employees section
5. Create: Test Employee (john@testcorp.com)
```

### Step 3: Employee Logs In (via desktop app or manual test)
```
1. Desktop App tries to login
   OR
   Verify in Django shell:
   ```bash
   python manage.py shell
   from core.models import User
   emp = User.objects.get(username='john')
   print(f"Employee exists: {emp}")
   print(f"Company: {emp.company}")
   print(f"Token: {emp.tracker_token}")
   ```
```

---

## Status

✅ **Owner creates company**: Working
✅ **Admin account auto-created**: Working  
✅ **Credentials display page**: Working
✅ **Company dropdown in navigation**: Working
✅ **Edit company**: Working
✅ **Delete company**: Working
⏳ **Admin login flow**: Ready for testing
⏳ **Employee creation by Admin**: Existing functionality
⏳ **Desktop app validation**: Existing functionality

---

**Created**: February 2, 2026
**Last Updated**: Today
**Status**: ✅ Ready for User Testing
