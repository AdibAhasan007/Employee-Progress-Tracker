# 🔐 OWNER ACCOUNT - COMPLETE DOCUMENTATION INDEX

**Last Updated**: January 31, 2026  
**Status**: ✅ Ready for Production

---

## 📚 Start Here: Choose Your Path

### 🚀 **I Just Want to Login (5 minutes)**
→ Read: [OWNER_LOGIN_QUICKSTART.txt](./OWNER_LOGIN_QUICKSTART.txt)

Contains:
- 3-minute setup
- Login credentials
- Quick troubleshooting

### 📖 **I Want Full Details (30 minutes)**
→ Read: [OWNER_LOGIN_GUIDE.md](./OWNER_LOGIN_GUIDE.md)

Contains:
- Step-by-step instructions (3 options)
- How to create OWNER user
- How to login
- Dashboard walkthrough
- Company management
- Security best practices
- Troubleshooting guide

### 🎨 **I'm Visual (Show me diagrams)**
→ Read: [OWNER_LOGIN_FLOWCHART.md](./OWNER_LOGIN_FLOWCHART.md)

Contains:
- Login process flowchart
- Security checks diagram
- Data flow visualization
- Request journey
- Decision tree
- Failure scenarios

---

## 🔍 Quick Reference

### Create OWNER Account

```bash
cd backend
python manage.py shell << 'EOF'
from core.models import User
User.objects.create_user(
    username='owner',
    password='SecurePass123!',
    email='owner@domain.com',
    role='OWNER'
)
EOF
```

### Login
- **URL**: `http://localhost:8000/admin/login/`
- **Username**: `owner`
- **Password**: `SecurePass123!`

### Dashboard
- **URL**: `http://localhost:8000/owner/dashboard/`
- **Access**: Via login redirect or direct URL (if logged in)

---

## 📊 OWNER Capabilities

### ✅ Can Do

| Feature | URL | Purpose |
|---------|-----|---------|
| 📊 Dashboard | `/owner/dashboard/` | View all companies + KPIs |
| 📈 Analytics | `/owner/company/<id>/` | Detailed company analytics |
| ➕ Create | `/owner/company/create/` | Create new trial company |
| 📋 Plan | `/owner/company/<id>/change-plan/` | Upgrade/downgrade |
| 🚫 Suspend | `/owner/company/<id>/suspend/` | Block company access |
| ✅ Activate | `/owner/company/<id>/reactivate/` | Restore company |
| 🔄 Rotate | `/owner/company/<id>/rotate-key/` | New security key |
| 📊 Reports | `/owner/reports/` | Analytics dashboard |

### ❌ Cannot Do

- View employee screenshots
- See website/app usage
- Access employee sessions
- View employee personal data
- Manage individual employees

**Why?** → Strict data isolation for privacy & ethics!

---

## 🔑 Company Keys

### What is it?
```
company_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p
```
Auto-generated secure token for each company.

### Where is it used?
Desktop app sends it on every API call:
```python
headers = {'X-Company-Key': 'company_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p'}
```

### Actions
- 📋 **Copy** - Get key for desktop app config
- 🔄 **Rotate** - Generate new key (old becomes inactive)
- 👁️ **View** - See key in company detail page

---

## 🔒 Security Checklist

- [ ] Strong password (16+ characters)
- [ ] Company keys stored in secure vault
- [ ] Keys rotated quarterly
- [ ] Login attempts monitored
- [ ] Session timeout configured
- [ ] Two-factor auth (if available)

---

## 🧪 Test the Login (Local Development)

### Quick Manual Test

```bash
# 1. Create test company
cd backend
python manage.py shell << 'EOF'
from core.models import User, Plan, Company
from django.utils import timezone
from datetime import timedelta

# Create OWNER
owner = User.objects.create_user(
    username='owner',
    password='Test123!',
    role='OWNER'
)

# Create test company
plan = Plan.objects.get_or_create(
    name='FREE',
    defaults={'max_employees': 5, 'max_storage_gb': 10}
)[0]

company = Company.objects.create(
    name='Test Corp',
    plan=plan,
    status='TRIAL'
)

print(f"✅ OWNER: {owner.username}")
print(f"✅ Company: {company.name}")
print(f"✅ Key: {company.company_key}")
EOF

# 2. Start server
python manage.py runserver

# 3. In browser:
# http://localhost:8000/admin/login/
# Login: owner / Test123!
# Access: http://localhost:8000/owner/dashboard/
```

### What to Check

- ✅ Login successful
- ✅ Dashboard loads
- ✅ Test company visible
- ✅ Can click on company
- ✅ Company details show
- ✅ Key displays
- ✅ Cannot see employee data

---

## 🚀 Deployment: Production Login

### 1. Create OWNER on Render

```bash
# Via Render shell
cd /opt/render/project/src
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

- **URL**: `https://your-domain.onrender.com/admin/login/`
- **Username**: `owner`
- **Password**: `YourSecurePassword123!`

### 3. First Time Setup

1. Login to dashboard
2. Create a test company
3. Verify it appears
4. Test company detail page
5. Check company key displays

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Login fails | `python manage.py shell` → verify user exists |
| Permission denied | Check `user.role = 'OWNER'` |
| No companies | Create one via shell or dashboard |
| Key missing | Save company: `company.save()` |
| "Not OWNER" error | Update role in shell |

See [OWNER_LOGIN_GUIDE.md](./OWNER_LOGIN_GUIDE.md) for detailed troubleshooting.

---

## 📞 Support

### By Question

**Q: How do I create an OWNER account?**  
A: See [OWNER_LOGIN_GUIDE.md](./OWNER_LOGIN_GUIDE.md) → Step 1

**Q: How do I login?**  
A: See [OWNER_LOGIN_QUICKSTART.txt](./OWNER_LOGIN_QUICKSTART.txt) → Step 2

**Q: What can OWNER see?**  
A: Only aggregate metrics. See section "OWNER Capabilities" above.

**Q: Where's the company key?**  
A: Dashboard → Company detail page → Security section

**Q: How do I rotate the key?**  
A: Dashboard → Company detail → "Rotate Key" button

**Q: Why can't I see employee data?**  
A: By design! OWNER role is for vendors to see health, not surveillance.

---

## 🎓 Related Documentation

### Multi-Tenant System
- [README_MULTITENANT.md](./README_MULTITENANT.md) - Master guide
- [MULTITENANT_QUICK_START.md](./MULTITENANT_QUICK_START.md) - Setup
- [MULTITENANT_IMPLEMENTATION_COMPLETE.md](./MULTITENANT_IMPLEMENTATION_COMPLETE.md) - Technical spec

### Deployment
- [DEPLOYMENT_FIX_DECORATOR.md](./DEPLOYMENT_FIX_DECORATOR.md) - Decorator fix
- [STATUS_REPORT_FINAL.md](./STATUS_REPORT_FINAL.md) - Implementation status

### Code
- [MULTITENANT_CODE_CHANGES.md](./MULTITENANT_CODE_CHANGES.md) - Code review

---

## 📋 Implementation Details

### User Model
```python
class User(AbstractUser):
    ROLE_CHOICES = (
        ('OWNER', 'Software Owner'),    # ← OWNER role
        ('ADMIN', 'Company Admin'),
        ('MANAGER', 'Manager'),
        ('EMPLOYEE', 'Employee'),
    )
    
    role = CharField(choices=ROLE_CHOICES)
    company = ForeignKey(Company)  # OWNER: null/blank
```

### Decorator
```python
def owner_required(func):
    """Ensure user is OWNER and logged in."""
    @wraps(func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'OWNER':
            return redirect('/')
        return func(request, *args, **kwargs)
    return wrapper

@owner_required
def owner_dashboard(request):
    # All OWNER views use this decorator
```

### Routes
```python
path('owner/dashboard/', owner_dashboard),
path('owner/company/<id>/', company_detail),
path('owner/company/create/', create_company),
path('owner/company/<id>/change-plan/', change_plan),
path('owner/company/<id>/suspend/', suspend_company),
path('owner/company/<id>/reactivate/', reactivate_company),
path('owner/company/<id>/rotate-key/', rotate_company_key),
path('owner/reports/', owner_reports),
```

---

## ✅ Checklist: Ready to Go?

- [ ] OWNER user created
- [ ] Can login to `/admin/login/`
- [ ] Dashboard loads at `/owner/dashboard/`
- [ ] At least one company created
- [ ] Company appears in dashboard
- [ ] Can click on company for details
- [ ] Company key visible
- [ ] Can view analytics
- [ ] Cannot access employee data
- [ ] All tests passing

---

## 🎉 You're Ready!

```
✅ OWNER account created
✅ Login working
✅ Dashboard accessible
✅ Companies manageable
✅ Strict data isolation active

READY TO USE! 🚀
```

---

## 📞 Need Help?

1. **Quick answer?** → [OWNER_LOGIN_QUICKSTART.txt](./OWNER_LOGIN_QUICKSTART.txt)
2. **Full guide?** → [OWNER_LOGIN_GUIDE.md](./OWNER_LOGIN_GUIDE.md)
3. **Visual learner?** → [OWNER_LOGIN_FLOWCHART.md](./OWNER_LOGIN_FLOWCHART.md)
4. **Still stuck?** → See troubleshooting section above

---

**Created**: January 31, 2026  
**Status**: ✅ Production Ready  
**Version**: 1.0
