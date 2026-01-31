# 🔐 OWNER Account Login Guide

**Status**: ✅ Ready to Use  
**Date**: January 31, 2026

---

## 📋 Quick Summary

An **OWNER** is the software vendor/architect who can:
- ✅ See ALL companies using the software
- ✅ View aggregate health metrics (total usage, active employees, storage)
- ✅ Manage company subscriptions (upgrade/downgrade plans)
- ✅ Suspend/reactivate companies
- ✅ Rotate company security keys
- ❌ **CANNOT** access individual employee data (screenshots, sessions, apps, websites)

---

## 🚀 Step 1: Create OWNER User Account

### Option A: Via Django Admin Shell (Recommended)

```bash
# Navigate to backend
cd backend

# Enter Django shell
python manage.py shell
```

Then in the Python shell:

```python
from core.models import User

# Create OWNER user
owner = User.objects.create_user(
    username='owner',
    password='YourSecurePassword123!',
    email='owner@yourdomain.com',
    first_name='Your',
    last_name='Name',
    role='OWNER'  # ← Important!
)

# Verify creation
print(f"✅ OWNER user created: {owner.username}")
print(f"   Role: {owner.role}")
print(f"   ID: {owner.id}")

# Exit shell
exit()
```

### Option B: Via Django Admin Interface

1. Go to: `http://localhost:8000/admin/`
2. Login with superuser credentials
3. Navigate to **Users** → **Add User**
4. Fill in:
   - **Username**: `owner`
   - **Password**: (strong password)
   - **Email**: your email
5. Scroll down to **Role** dropdown → Select **Software Owner** (OWNER)
6. Click **Save**

### Option C: Via createsuperuser (If OWNER is also Admin)

```bash
python manage.py createsuperuser
# Username: owner
# Email: owner@domain.com
# Password: (enter password)

# Then in shell, update role:
python manage.py shell << 'EOF'
from core.models import User
user = User.objects.get(username='owner')
user.role = 'OWNER'
user.save()
print(f"✅ {user.username} is now OWNER")
EOF
```

---

## 🔓 Step 2: Login to OWNER Portal

### Access Points

#### **Web Interface** (Recommended)

1. Go to: **`http://localhost:8000/admin/login/`** (or your Render domain)

2. Login with:
   - **Username**: `owner`
   - **Password**: `YourSecurePassword123!`

3. After login, you'll be redirected to: **`/owner/dashboard/`**

#### **Direct URL** (If Already Logged In)

```
http://localhost:8000/owner/dashboard/
```

---

## 📊 Step 3: Explore OWNER Dashboard

After login, you'll see:

### **Main Dashboard** (`/owner/dashboard/`)
```
┌─────────────────────────────────────────────────────────┐
│           OWNER DASHBOARD                               │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Total Companies: 15    Active: 12    Trial: 3           │
│  Total Users: 245       Active Sessions: 18              │
│  Storage Used: 245 GB   Avg Per Company: 16.3 GB         │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Companies List                                      │ │
│  ├──────────────────────┬─────────┬────────┬───────────┤ │
│  │ Company Name         │ Status  │ Plan   │ Users (↓) │ │
│  ├──────────────────────┼─────────┼────────┼───────────┤ │
│  │ Acme Corp            │ ACTIVE  │ PRO    │ 25        │ │
│  │ Tech Startup Inc     │ ACTIVE  │ PRO    │ 18        │ │
│  │ Global Industries    │ ACTIVE  │ ENTER. │ 89        │ │
│  │ Small Business LLC   │ TRIAL   │ FREE   │ 5         │ │
│  │ ...                  │ ...     │ ...    │ ...       │ │
│  └──────────────────────┴─────────┴────────┴───────────┘ │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

**Available Actions**:
- ✅ Click on company name → View analytics
- ✅ View last sync time
- ✅ See active employee count
- ✅ Check storage usage

---

## 🔧 Step 4: Manage Companies

### View Company Details

Click on any company to access detailed analytics:

```
/owner/company/<company_id>/
```

**Features**:
- 📊 Usage analytics (last 90 days)
- 📈 Daily usage chart (Chart.js)
- 👥 Subscription info & plan details
- 🔑 Company key (copy/rotate)
- 🛠️ Management actions

### Create New Trial Company

```
POST /owner/company/create/
```

**Form**:
```
Company Name: [Required, unique]
Email: [Optional]
Contact Person: [Optional]
Plan: [Dropdown: FREE, PRO, ENTERPRISE]
```

**Result**: 
- ✅ Company created with TRIAL status
- ✅ Unique company_key auto-generated
- ✅ Free subscription created

### Upgrade Company Plan

```
POST /owner/company/<company_id>/change-plan/
```

**Example**: Upgrade from FREE → PRO
- Plan changes immediately
- New limits apply
- Usage audit trail created

### Suspend Company (Emergency)

```
POST /owner/company/<company_id>/suspend/
```

**Effect**:
- ❌ All desktop app syncs blocked (401 error)
- ❌ Web logins rejected
- ✅ Data preserved (can reactivate)

### Reactivate Company

```
POST /owner/company/<company_id>/reactivate/
```

**Effect**:
- ✅ Desktop app syncs allowed
- ✅ Web logins enabled
- ✅ Fresh 30-day subscription

### Rotate Security Key

```
POST /owner/company/<company_id>/rotate-key/
```

**When to use**:
- 🔒 Security breach suspected
- 🔄 Scheduled rotation (quarterly)
- 🚨 Unauthorized access detected

**Process**:
1. Old key: `company_abc123...` (becomes inactive)
2. New key: `company_xyz789...` (auto-generated)
3. Company gets 24h notice to update config
4. Old key stops working after 24h

---

## 📈 Step 5: View Analytics & Reports

### Company Analytics Page

**URL**: `/owner/company/<company_id>/`

Shows:
- 📊 Last 90 days of usage
- 📈 Chart of daily activity (active seconds)
- 📸 Screenshot count trend
- 💾 Storage usage trend
- 👥 Employee count

### OWNER Reports

**URL**: `/owner/reports/`

Includes:
- 📊 Total companies by status
- 💰 Revenue by plan tier
- 📉 Top 10 companies by usage
- 📱 Plan distribution (pie chart)
- 🎯 Key metrics

---

## 🔑 Important: Company Keys

### What is a Company Key?

A secure token that identifies each company:
```
company_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p
         └─────────────────────────────┘
         32-character hex, auto-generated
```

### Where is it Used?

**Desktop App (tracker/)** sends it on every API call:

```python
# tracker/main.py or similar
headers = {
    'X-Company-Key': 'company_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p'
}

# All API requests must include this header
response = requests.post(
    'http://server:8000/api/login',
    headers=headers,
    json={'username': 'emp1', 'password': 'pass'}
)
```

### Viewing Keys in Dashboard

1. Go to company detail page
2. Scroll to **"Security"** section
3. See: **Company Key**: `company_...`
4. Actions:
   - 📋 **Copy** - Copy to clipboard
   - 🔄 **Rotate** - Generate new key
   - ⚙️ **View History** - See old keys (archived)

---

## 🚫 What OWNER CANNOT Do

**Explicitly Blocked** (strict data isolation):

❌ View individual employee data:
- ❌ Screenshots
- ❌ Website visits
- ❌ Application usage
- ❌ Work sessions
- ❌ Activity logs
- ❌ Employee personal info

❌ Manage individual employees:
- ❌ Add/remove employees
- ❌ Edit employee names
- ❌ Change employee roles
- ❌ View employee passwords

❌ Access company data:
- ❌ Files/uploads
- ❌ Settings/configs
- ❌ Team conversations

**Why?** → Privacy & ethics! OWNER role is designed for software vendors to see health metrics WITHOUT employee surveillance.

---

## 🔒 Security Best Practices

### For OWNER Account

1. **Strong Password**
   ```
   ✅ At least 16 characters
   ✅ Mix uppercase, lowercase, numbers, special chars
   ✅ Avoid dictionary words
   ✅ Example: Tr0pic@lMango$2026!
   ```

2. **Keep Company Keys Secure**
   - Don't commit to git
   - Don't share in logs
   - Rotate quarterly
   - Use environment variables in production

3. **Monitor Access**
   - Check "Last Login" timestamps
   - Review company key rotation history
   - Verify API access logs

4. **Backup Recovery Keys**
   - Save company keys in secure vault (1Password, Vault, etc.)
   - Lost key? Must rotate (old key stops working)

---

## 🧪 Testing: Quick Test Session

### Manual Test

```bash
# 1. Start server
cd backend
python manage.py runserver

# 2. In another terminal, create OWNER
python manage.py shell << 'EOF'
from core.models import User, Plan, Company, Subscription
from django.utils import timezone
from datetime import timedelta

# Create OWNER
owner = User.objects.create_user(
    username='owner',
    password='Test123!',
    email='owner@test.com',
    role='OWNER'
)
print(f"✅ OWNER created")

# Create FREE plan if not exists
plan, _ = Plan.objects.get_or_create(
    name='FREE',
    defaults={'max_employees': 5, 'max_storage_gb': 10}
)

# Create a test company
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

print(f"✅ Test company created: {company.name}")
print(f"✅ Company key: {company.company_key}")
EOF

# 3. Open browser
# Go to: http://localhost:8000/admin/login/
# Login: owner / Test123!
# Access: http://localhost:8000/owner/dashboard/
```

### What to Verify

- ✅ Login successful
- ✅ Dashboard loads
- ✅ Test company appears in list
- ✅ Can click on company
- ✅ Company details page works
- ✅ Cannot access employee data

---

## 🚀 Deployment: OWNER Login on Render

### 1. Create OWNER User on Render

```bash
# SSH into Render shell
cd /opt/render/project/src

# Run migrations first
python backend/manage.py migrate core 0007

# Create OWNER
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

### 2. Login on Production

- **URL**: `https://your-render-domain.onrender.com/admin/login/`
- **Username**: `owner`
- **Password**: `YourSecurePassword123!`
- **Redirect**: `https://your-render-domain.onrender.com/owner/dashboard/`

### 3. Environment Configuration

Add to Render environment variables:
```
OWNER_USERNAME=owner
OWNER_EMAIL=owner@yourdomain.com
# Password: Use secure method (not in env vars!)
```

---

## 📞 Troubleshooting

### Issue: "Login Failed - User Not Found"

**Solution**:
```bash
# Verify OWNER user exists
python manage.py shell << 'EOF'
from core.models import User
owner = User.objects.filter(username='owner').first()
if owner:
    print(f"✅ OWNER user exists: {owner}")
    print(f"   Role: {owner.role}")
    print(f"   Active: {owner.is_active}")
else:
    print("❌ OWNER user does not exist - create one!")
EOF
```

### Issue: "Permission Denied - Not OWNER"

**Solution**:
```bash
# Check user role
python manage.py shell << 'EOF'
from core.models import User
user = User.objects.get(username='owner')
print(f"Current role: {user.role}")
if user.role != 'OWNER':
    user.role = 'OWNER'
    user.save()
    print("✅ Updated to OWNER role")
EOF
```

### Issue: "Dashboard Shows No Companies"

**Solution**:
```bash
# Create a test company
python manage.py shell << 'EOF'
from core.models import Company, Plan, Subscription
from django.utils import timezone
from datetime import timedelta

plan = Plan.objects.get(name='FREE')
company = Company.objects.create(
    name='Test Corp',
    plan=plan,
    status='TRIAL'
)
Subscription.objects.create(
    company=company,
    plan=plan,
    starts_at=timezone.now(),
    expires_at=timezone.now() + timedelta(days=30)
)
print(f"✅ Test company created: {company.name}")
EOF

# Refresh dashboard
```

### Issue: "Company Key Not Showing"

**Solution**: Company key auto-generates on first save. If missing:
```bash
python manage.py shell << 'EOF'
from core.models import Company
company = Company.objects.get(id=1)
if not company.company_key:
    company.save()  # Auto-generates key
print(f"Company key: {company.company_key}")
EOF
```

---

## ✅ Checklist: OWNER Account Ready?

- [ ] OWNER user created in database
- [ ] OWNER role set correctly
- [ ] Can login to `/admin/login/`
- [ ] Redirects to `/owner/dashboard/`
- [ ] At least one company created for testing
- [ ] Dashboard shows companies
- [ ] Can click on company for details
- [ ] Company key visible
- [ ] Can view analytics
- [ ] Cannot access employee data (permission denied)

---

## 📚 Related Documentation

- [README_MULTITENANT.md](./README_MULTITENANT.md) - Master guide
- [MULTITENANT_QUICK_START.md](./MULTITENANT_QUICK_START.md) - Setup & deployment
- [DEPLOYMENT_FIX_DECORATOR.md](./DEPLOYMENT_FIX_DECORATOR.md) - Decorator fix

---

## 🎉 You're All Set!

Your OWNER account is ready to manage companies, view analytics, and maintain subscriptions while maintaining strict privacy from employee data. ✅

**Questions?** See the main documentation files or check the Django admin panel.

---

**Created**: January 31, 2026  
**Status**: ✅ Ready for Production
