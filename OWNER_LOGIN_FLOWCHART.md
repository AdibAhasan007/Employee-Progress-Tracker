# 🔐 OWNER LOGIN FLOW - Visual Guide

## Login Process Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    OWNER ACCOUNT LOGIN FLOW                     │
└─────────────────────────────────────────────────────────────────┘

Step 1: CREATE OWNER USER (One-time Setup)
────────────────────────────────────────────────────────────────

    Django Shell
        ↓
    python manage.py shell
        ↓
    User.objects.create_user(
        username='owner',
        password='SecurePass123!',
        role='OWNER'
    )
        ↓
    ✅ User Created in Database


Step 2: VISIT LOGIN PAGE
────────────────────────────────────────────────────────────────

    Browser
        ↓
    http://localhost:8000/admin/login/
        ↓
    Django Login Form
        │
        ├─ Username field
        ├─ Password field
        └─ Login button


Step 3: ENTER CREDENTIALS
────────────────────────────────────────────────────────────────

    Form Submission
        ↓
    POST /admin/login/
        ├─ username=owner
        └─ password=SecurePass123!
        ↓
    Django Authentication
        ├─ Check user exists
        ├─ Verify password
        └─ Create session


Step 4: REDIRECT TO DASHBOARD
────────────────────────────────────────────────────────────────

    POST /admin/login/
        ↓
    Authentication Success
        ↓
    Check: user.is_authenticated? ✅
        ↓
    Redirect: /owner/dashboard/
        ↓
    @owner_required decorator
        ├─ Is user logged in? ✅
        ├─ Is user.role == 'OWNER'? ✅
        └─ Allow access
        ↓
    owner_dashboard() view
        ├─ Query: Company.objects.all()
        ├─ Aggregate: Daily usage stats
        └─ Render: owner_dashboard.html
        ↓
    ✅ Dashboard Displayed


Step 5: INTERACT WITH PORTAL
────────────────────────────────────────────────────────────────

    Dashboard Actions:
    
    ├─ Click Company Name
    │   ↓
    │   GET /owner/company/<id>/
    │   ├─ @owner_required ✅
    │   ├─ Query: Company + Analytics
    │   └─ Display: Company Details Page
    │
    ├─ Click "Create Company"
    │   ↓
    │   GET /owner/company/create/
    │   └─ Display: Company Form
    │
    ├─ Submit Form
    │   ↓
    │   POST /owner/company/create/
    │   ├─ Validate: Company name unique
    │   ├─ Create: Company object
    │   ├─ Auto-generate: company_key
    │   ├─ Create: Subscription
    │   └─ Redirect: Dashboard
    │
    ├─ Click "Change Plan"
    │   ↓
    │   POST /owner/company/<id>/change-plan/
    │   ├─ Update: company.plan
    │   ├─ Create: Subscription audit
    │   └─ Success message
    │
    ├─ Click "Suspend"
    │   ↓
    │   POST /owner/company/<id>/suspend/
    │   ├─ Update: company.status = 'SUSPENDED'
    │   ├─ Effect: All desktop app calls → 403
    │   └─ Data preserved
    │
    ├─ Click "Rotate Key"
    │   ↓
    │   POST /owner/company/<id>/rotate-key/
    │   ├─ Generate: New company_key
    │   ├─ Archive: Old key
    │   └─ Notify: Company (24h grace)
    │
    └─ View "Reports"
        ↓
        GET /owner/reports/
        ├─ Company distribution
        ├─ Revenue by plan
        ├─ Top companies by usage
        └─ Analytics charts


Step 6: LOGOUT
────────────────────────────────────────────────────────────────

    Click: "Logout"
        ↓
    GET /admin/logout/
        ├─ Destroy: Session
        └─ Redirect: /
        ↓
    ✅ Session Cleared
```

---

## Security Checks During Login

```
┌─────────────────────────────────────────────────────────┐
│         SECURITY VALIDATION AT EACH STEP                │
└─────────────────────────────────────────────────────────┘

1. User Creation
   ├─ ✅ Hash password (Django PBKDF2)
   ├─ ✅ Check username unique
   └─ ✅ Validate role = 'OWNER'

2. Login Form
   ├─ ✅ Check user exists
   ├─ ✅ Verify password hash
   ├─ ✅ Check is_active = True
   └─ ✅ Create encrypted session

3. Decorator Check (@owner_required)
   ├─ ✅ Is user.is_authenticated?
   ├─ ✅ Is user.role == 'OWNER'?
   └─ ❌ Else: Redirect to '/'

4. View Execution (owner_dashboard)
   ├─ ✅ Access all companies
   ├─ ✅ Calculate aggregates only
   └─ ❌ Cannot access raw employee data

5. API Calls (if via X-Company-Key header)
   ├─ ✅ Validate company_key exists
   ├─ ✅ Check company.status != 'SUSPENDED'
   ├─ ✅ Verify subscription not expired
   └─ ❌ Else: Return 401/403 JSON
```

---

## Login Success: What Happens Next

```
                    ✅ Login Successful
                            ↓
            Session Created & Stored in Browser
                            ↓
        Cookie: sessionid=abc123def456...
                            ↓
        Every Subsequent Request:
            Browser sends: sessionid cookie
                    ↓
        Django Verifies: Is session valid?
                    ↓
            ✅ Load User from Database
                    ↓
            ✅ Check: user.role = 'OWNER'
                    ↓
        Permission Granted: Access Dashboard
```

---

## Login Failure Scenarios

```
❌ SCENARIO 1: Wrong Username
    Input: owner (doesn't exist)
    ↓
    Django: User not found
    ↓
    Response: "Invalid username or password"
    ↓
    Stay on login page

❌ SCENARIO 2: Wrong Password
    Input: owner, WrongPass
    ↓
    Django: Password hash mismatch
    ↓
    Response: "Invalid username or password"
    ↓
    Stay on login page

❌ SCENARIO 3: User Inactive
    Input: owner (is_active=False)
    ↓
    Django: User disabled
    ↓
    Response: "Invalid username or password"
    ↓
    Stay on login page

❌ SCENARIO 4: User is not OWNER
    Input: admin (role='ADMIN')
    ↓
    Login succeeds (is_authenticated=True)
    ↓
    Redirect to /owner/dashboard/
    ↓
    @owner_required decorator checks: role == 'OWNER'?
    ↓
    Response: Redirect to '/'
    ↓
    Cannot access OWNER portal

❌ SCENARIO 5: Session Expired
    Browser: sessionid=expired
    ↓
    Django: Session not found in cache
    ↓
    User auto-logged out
    ↓
    Redirect to: /admin/login/
```

---

## Request Flow: From Browser to Database

```
┌──────────────────────────────────────────────────────────┐
│         FROM BROWSER TO DATABASE                         │
└──────────────────────────────────────────────────────────┘

Browser:
    1. User enters username: "owner"
    2. User enters password: "SecurePass123!"
    3. Clicks login button
    4. Browser sends: POST /admin/login/

─────────────────────────────────────────────────────────

Django URL Router:
    /admin/login/ → django.contrib.admin.LoginView

─────────────────────────────────────────────────────────

LoginView.post():
    1. Get form data
    2. Call: authenticate(username, password)
    3. Check: username exists in DB?
    4. Check: password matches hash?
    5. If success:
        - Create session
        - Save to cache/database
        - Return redirect

─────────────────────────────────────────────────────────

After Authentication:
    Browser now has: Cookie: sessionid=xyz...

─────────────────────────────────────────────────────────

Next Request to /owner/dashboard/:
    
    Browser sends:
        GET /owner/dashboard/
        Cookie: sessionid=xyz...

─────────────────────────────────────────────────────────

Django Middleware:
    1. Receive request
    2. Extract: sessionid from cookie
    3. Query: SessionStore.get(sessionid)
    4. Load: user from session data
    5. Attach: request.user = User(id=123)

─────────────────────────────────────────────────────────

@owner_required Decorator:
    1. Check: request.user.is_authenticated? ✅
    2. Check: request.user.role == 'OWNER'? ✅
    3. Call: owner_dashboard(request)

─────────────────────────────────────────────────────────

owner_dashboard() View:
    1. Query: Company.objects.all()
        ↓
        SELECT * FROM core_company
    
    2. For each company:
        Query: CompanyUsageDaily
            ↓
            SELECT SUM(total_active_seconds) FROM core_companyusagedaily
            WHERE company_id = ? AND date >= ?
    
    3. Render: owner_dashboard.html
        ↓
        Pass: companies_data to template

─────────────────────────────────────────────────────────

Response to Browser:
    
    HTML rendered with:
    - Company list
    - Usage statistics
    - Links to detailed pages
    - Forms for actions

─────────────────────────────────────────────────────────

Browser:
    Displays: OWNER Dashboard ✅
```

---

## Data Flow: Login → Dashboard → Action

```
LOGIN
  │
  ├─→ User.objects.get(username='owner')
  │     Database: Look up user by username
  │
  ├─→ check_password(password)
  │     Crypto: Verify password hash
  │
  ├─→ Session.objects.create(...)
  │     Database: Store session data
  │
  └─→ Cookie: sessionid = xyz123

DASHBOARD
  │
  ├─→ request.user = User.from_session()
  │     Memory: Load user from request
  │
  ├─→ @owner_required decorator
  │     Check: role == 'OWNER'
  │
  ├─→ Company.objects.all()
  │     Database: Get all companies
  │
  ├─→ company.daily_usage.filter(...)
  │     Database: Get aggregated stats
  │
  └─→ Render: Template with data

ACTION (e.g., Suspend Company)
  │
  ├─→ POST /owner/company/<id>/suspend/
  │
  ├─→ Company.objects.get(id=<id>)
  │     Database: Load company
  │
  ├─→ company.status = 'SUSPENDED'
  │
  ├─→ company.save()
  │     Database: UPDATE core_company
  │
  ├─→ Subscription.objects.create(...)
  │     Database: Audit trail
  │
  └─→ Redirect: Dashboard
```

---

## Example: Full Login Session

```
TIME    ACTION                          DATABASE        BROWSER
────────────────────────────────────────────────────────────────

10:00   User visits /admin/login/                      GET request
        
10:01   Enters:                                         Form filled
        • username: owner
        • password: SecurePass123!

10:02   Clicks: Login                   SELECT user     POST request
                                        WHERE
                                        username='owner'
        
10:03   Django verifies password        CHECK hash      Match? ✅
        
10:04   Session created                 INSERT session  Cookie set
        sessionid=abc123xyz             SESSION         sessionid=
                                                        abc123xyz

10:05   Redirect to dashboard           (no query)      Redirect 302

10:06   Visit /owner/dashboard/         SELECT *        GET with
                                        FROM company    sessionid
        
10:07   Get all companies               Multiple        Render
                                        SELECT queries  HTML

10:08   Page displays                                   Dashboard
                                                       visible ✅

10:30   User clicks "Change Plan"       UPDATE          POST with
                                        company SET     data
                                        plan_id=2

10:31   Plan changed                    INSERT audit    Success msg

10:45   User clicks "Logout"            DELETE session  Clear
                                                        session

10:46   Logout complete                 (no query)      Login page
                                                        shown
```

---

## Quick Decision Tree

```
                    User visits login?
                            │
                    ┌───────┴───────┐
                    NO              YES
                    │               │
               Skip to      Display login form
               dashboard        │
                               User enters creds
                                   │
                          ┌────────┴────────┐
                         NO                YES
                         │                 │
                    Stay on form    Verify password
                                        │
                                  ┌─────┴─────┐
                                 NO           YES
                                 │            │
                            Invalid error   Create session
                            message            │
                                         ┌─────┴──────┐
                                    SET role check
                                   NOT OWNER
                                        │
                                   Redirect /
                                        │
                                    IS OWNER
                                        │
                                   Load dashboard
                                        │
                                    ✅ Success
```

---

## Summary: Login → Dashboard → Manage

```
┌────────────────┐
│  OWNER LOGIN   │  Create user with role='OWNER'
└────────────────┘
        ↓
┌────────────────┐
│  VISIT LOGIN   │  http://localhost:8000/admin/login/
└────────────────┘
        ↓
┌────────────────┐
│  ENTER CREDS   │  username=owner, password=SecurePass
└────────────────┘
        ↓
┌────────────────┐
│ AUTHENTICATE   │  Check user exists + password match
└────────────────┘
        ↓
┌────────────────┐
│ CHECK ROLE     │  Is user.role == 'OWNER'? ✅
└────────────────┘
        ↓
┌────────────────┐
│  TO DASHBOARD  │  /owner/dashboard/ ← Shows all companies
└────────────────┘
        ↓
┌────────────────┐
│  VIEW COMPANY  │  /owner/company/<id>/ ← Analytics
└────────────────┘
        ↓
┌────────────────┐
│  MANAGE PLAN   │  Upgrade/downgrade company
└────────────────┘
        ↓
┌────────────────┐
│ SUSPEND/REVOKE │  Stop sync + restrict access
└────────────────┘
        ↓
┌────────────────┐
│  ROTATE KEY    │  Generate new company_key
└────────────────┘
        ↓
┌────────────────┐
│  VIEW REPORTS  │  /owner/reports/ ← Analytics
└────────────────┘
        ↓
┌────────────────┐
│    LOGOUT      │  Clear session + return to login
└────────────────┘
```

---

**Status**: ✅ Ready for Login  
**Created**: January 31, 2026
