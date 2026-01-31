# 🔐 HOW TO LOGIN: OWNER ACCOUNT - COMPLETE ANSWER

**Question**: How To Login : Owner Account?  
**Answer**: See below ↓↓↓

---

## ⚡ QUICKEST ANSWER (30 Seconds)

```bash
# Create OWNER user
python manage.py shell << 'EOF'
from core.models import User
User.objects.create_user(username='owner', password='Pass123!', role='OWNER')
EOF

# Login at
http://localhost:8000/admin/login/

# Credentials
Username: owner
Password: Pass123!

# Access dashboard
http://localhost:8000/owner/dashboard/
```

---

## 📖 COMPLETE ANSWER

### What is OWNER Account?

An **OWNER** is the software vendor/architect who:
- ✅ Can see ALL companies using the software
- ✅ Can see aggregate metrics (health, usage, storage)
- ✅ Can manage subscriptions (create, upgrade, suspend)
- ✅ Can rotate security keys
- ❌ **CANNOT** access individual employee data (screenshots, sessions, etc.)

### Step-by-Step: Create & Login

#### **Step 1: Create OWNER User Account**

**Option A - Django Shell (Recommended)**

```bash
cd backend
python manage.py shell
```

Then type:
```python
from core.models import User

# Create OWNER
owner = User.objects.create_user(
    username='owner',
    password='YourSecurePassword123!',
    email='owner@domain.com',
    role='OWNER'  # ← Important: Must be 'OWNER'
)

print(f"✅ OWNER user created: {owner.username}")
exit()
```

**Option B - Django Admin Panel**

1. Go to: `http://localhost:8000/admin/`
2. Click: **Users** → **Add User**
3. Fill in:
   - Username: `owner`
   - Email: `owner@domain.com`
   - Password: (strong password)
4. Scroll down: **Role** → Select **"Software Owner"** (OWNER)
5. Click: **Save**

**Option C - Automated Script**

```bash
python manage.py shell << 'EOF'
from core.models import User
u = User.objects.create_user(
    username='owner',
    password='SecurePass123!',
    email='owner@yourdomain.com',
    role='OWNER'
)
print(f"✅ Created: {u.username} ({u.role})")
EOF
```

#### **Step 2: Visit Login Page**

Open browser and go to:
```
http://localhost:8000/admin/login/
```

Or on Render production:
```
https://your-domain.onrender.com/admin/login/
```

#### **Step 3: Enter Credentials**

```
Username: owner
Password: YourSecurePassword123!
```

Click: **Login** button

#### **Step 4: Access OWNER Dashboard**

After login, you'll be **redirected** to:
```
http://localhost:8000/owner/dashboard/
```

Or access directly (if already logged in):
```
http://localhost:8000/owner/dashboard/
```

---

## 🎯 What You'll See: OWNER Dashboard

### Dashboard Page (`/owner/dashboard/`)

```
┌─────────────────────────────────────────────────────────┐
│               OWNER DASHBOARD                           │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  📊 METRICS                                              │
│  ────────────────────────────────────────────────────   │
│  Total Companies: 15    Active: 12    Trial: 3           │
│  Total Users: 245       Active Sessions: 18              │
│  Storage Used: 245 GB   Avg Per Company: 16.3 GB         │
│                                                           │
│  📋 COMPANIES TABLE                                      │
│  ────────────────────────────────────────────────────   │
│  Company Name              Status  Plan   Users  Usage   │
│  ──────────────────────────────────────────────────────  │
│  Acme Corp                 ACTIVE  PRO    25    89 hrs   │
│  Tech Startup Inc          ACTIVE  PRO    18    45 hrs   │
│  Small Business LLC        TRIAL   FREE   5     12 hrs   │
│  Global Industries         ACTIVE  ENT    89    234 hrs  │
│  [View More...]                                          │
│                                                           │
│  Actions per Company:                                    │
│  • Click name → View detailed analytics                  │
│  • "Change Plan" → Upgrade/downgrade                     │
│  • "Suspend" → Block company access                      │
│  • "Rotate Key" → New security key                       │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### Available OWNER Endpoints

| Page | URL | What You See |
|------|-----|-------------|
| **Dashboard** | `/owner/dashboard/` | All companies + KPIs |
| **Company Detail** | `/owner/company/<id>/` | Analytics + charts |
| **Create Company** | `/owner/company/create/` | Form to add company |
| **Change Plan** | `/owner/company/<id>/change-plan/` | Upgrade/downgrade |
| **Suspend** | `/owner/company/<id>/suspend/` | Block access |
| **Reactivate** | `/owner/company/<id>/reactivate/` | Restore access |
| **Rotate Key** | `/owner/company/<id>/rotate-key/` | New security key |
| **Reports** | `/owner/reports/` | Analytics dashboard |

---

## 🔑 Important: Company Keys

### What is a Company Key?

```
company_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p
```

Unique secure token for each company. Used by desktop app to authenticate.

### Where is it Used?

Desktop app (tracker/) sends it on every API call:

```python
headers = {
    'X-Company-Key': 'company_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p'
}

response = requests.post(
    'http://server:8000/api/login',
    headers=headers,
    json={...}
)
```

### How to Get It

1. Login to OWNER dashboard
2. Click on company name
3. Scroll to **"Security"** section
4. See: **Company Key**: `company_...`
5. Click **Copy** button

### How to Rotate It

1. Company detail page
2. Click **"Rotate Key"** button
3. Confirm action
4. New key generated automatically
5. Old key becomes inactive

---

## 🚫 Important: What OWNER CANNOT See

**By Design** (strict data isolation):

```
❌ Employee Screenshots      - Individual images blocked
❌ Website Visits           - No URL visits tracked
❌ Application Usage        - No app names/duration
❌ Work Sessions           - No individual session details
❌ Activity Logs           - No per-employee actions
❌ Employee Personal Data  - No names/emails/roles
❌ Employee List           - No individual employees
```

**Why?** OWNER role is for software vendors to monitor system health WITHOUT employee surveillance.

---

## 🔒 Security Tips

### Password
- ✅ Use strong password (16+ characters)
- ✅ Mix: uppercase, lowercase, numbers, special chars
- ✅ Example: `Tr0pic@lMango$2026!`

### Company Keys
- ✅ Store in secure vault (1Password, LastPass, Vault)
- ✅ Don't commit to git
- ✅ Don't log
- ✅ Rotate quarterly

### Monitoring
- ✅ Check "Last Login" timestamps
- ✅ Review key rotation history
- ✅ Monitor API access patterns

---

## 🧪 Test It (Local Development)

### Create Test Data

```bash
cd backend
python manage.py shell << 'EOF'
from core.models import User, Plan, Company, Subscription
from django.utils import timezone
from datetime import timedelta

# Create OWNER
owner = User.objects.create_user(
    username='owner',
    password='Test123!',
    role='OWNER'
)

# Create plan
plan, _ = Plan.objects.get_or_create(
    name='FREE',
    defaults={'max_employees': 5, 'max_storage_gb': 10}
)

# Create test company
company = Company.objects.create(
    name='Test Company',
    plan=plan,
    status='TRIAL'
)

# Create subscription
Subscription.objects.create(
    company=company,
    plan=plan,
    starts_at=timezone.now(),
    expires_at=timezone.now() + timedelta(days=30)
)

print(f"✅ OWNER: {owner.username}")
print(f"✅ Company: {company.name}")
print(f"✅ Key: {company.company_key}")
EOF
```

### Start Server & Login

```bash
# Terminal 1: Start server
python manage.py runserver

# Terminal 2: Open browser
http://localhost:8000/admin/login/

# Login
Username: owner
Password: Test123!
```

### Verify It Works

- ✅ Dashboard loads
- ✅ Test company appears
- ✅ Can click company name
- ✅ Company detail page works
- ✅ Analytics show
- ✅ Company key displays
- ✅ Cannot access employee data

---

## 🚀 Production Deployment (Render)

### Create OWNER on Production

```bash
# SSH into Render shell
# Via Render Dashboard → Shell

# Navigate
cd /opt/render/project/src

# Create OWNER user
python backend/manage.py shell << 'EOF'
from core.models import User
owner = User.objects.create_user(
    username='owner',
    password='YourSecurePassword123!',
    email='owner@yourdomain.com',
    role='OWNER'
)
print(f"✅ OWNER created on production!")
EOF
```

### Login on Production

```
URL: https://your-domain.onrender.com/admin/login/
Username: owner
Password: YourSecurePassword123!
```

### Access Dashboard

```
https://your-domain.onrender.com/owner/dashboard/
```

---

## 🐛 Troubleshooting

### Issue: Login fails with "Invalid username or password"

**Cause**: User doesn't exist  
**Fix**:
```bash
python manage.py shell << 'EOF'
from core.models import User
user = User.objects.filter(username='owner').first()
if not user:
    User.objects.create_user(username='owner', password='Pass123!', role='OWNER')
    print("✅ Created")
else:
    print("✅ Already exists")
EOF
```

### Issue: Login succeeds but get "Permission Denied"

**Cause**: User role is not 'OWNER'  
**Fix**:
```bash
python manage.py shell << 'EOF'
from core.models import User
user = User.objects.get(username='owner')
print(f"Current role: {user.role}")
if user.role != 'OWNER':
    user.role = 'OWNER'
    user.save()
    print("✅ Updated to OWNER")
EOF
```

### Issue: Dashboard shows no companies

**Cause**: No companies created  
**Fix**:
```bash
python manage.py shell << 'EOF'
from core.models import Company, Plan
plan = Plan.objects.get(name='FREE')
Company.objects.create(
    name='Test Corp',
    plan=plan,
    status='TRIAL'
)
print("✅ Company created")
EOF
```

### Issue: Company key not showing

**Cause**: Key not generated on creation  
**Fix**:
```bash
python manage.py shell << 'EOF'
from core.models import Company
company = Company.objects.get(id=1)
if not company.company_key:
    company.save()  # Auto-generates
print(f"Key: {company.company_key}")
EOF
```

---

## ✅ Readiness Checklist

Use this to verify OWNER account is working:

- [ ] OWNER user created with `role='OWNER'`
- [ ] Can login to `/admin/login/`
- [ ] Dashboard accessible at `/owner/dashboard/`
- [ ] At least 1 company created
- [ ] Company appears in dashboard list
- [ ] Can click on company for details
- [ ] Company key visible in detail page
- [ ] Can view analytics/charts
- [ ] Cannot see employee data (permission denied if attempted)
- [ ] Can suspend/reactivate company
- [ ] Can rotate company key
- [ ] All tests passing: `python manage.py test core.tests_multitenant`

---

## 📚 More Information

### Full Documentation

- [OWNER_LOGIN_GUIDE.md](./OWNER_LOGIN_GUIDE.md) - 30-minute complete guide
- [OWNER_LOGIN_FLOWCHART.md](./OWNER_LOGIN_FLOWCHART.md) - Visual diagrams
- [OWNER_LOGIN_QUICKSTART.txt](./OWNER_LOGIN_QUICKSTART.txt) - Quick reference

### System Documentation

- [README_MULTITENANT.md](./README_MULTITENANT.md) - Multi-tenant overview
- [MULTITENANT_QUICK_START.md](./MULTITENANT_QUICK_START.md) - Full deployment
- [STATUS_REPORT_FINAL.md](./STATUS_REPORT_FINAL.md) - Implementation status

---

## 🎉 Summary

```
✅ Create OWNER user
   python manage.py shell
   User.objects.create_user(username='owner', role='OWNER')

✅ Login
   http://localhost:8000/admin/login/
   owner / SecurePass123!

✅ Access Dashboard
   http://localhost:8000/owner/dashboard/

✅ Manage Companies
   View analytics, create, suspend, rotate keys

✅ Strict Privacy
   Cannot access any employee data

READY TO USE! 🚀
```

---

**Created**: January 31, 2026  
**Status**: ✅ Production Ready  
**Last Updated**: Today

**Questions?** See [OWNER_LOGIN_GUIDE.md](./OWNER_LOGIN_GUIDE.md) for comprehensive documentation.
