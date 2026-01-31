# 🔐 AYMAN - OWNER ACCOUNT CREDENTIALS

**Status**: ✅ ACCOUNT CREATED & READY

---

## 📝 Account Details

| Field | Value |
|-------|-------|
| **Name** | Ayman |
| **Username** | ayman |
| **Email** | ayman@gmail.com |
| **Password** | 12345 |
| **Role** | OWNER (Software Owner) |
| **Status** | ✅ Active |

---

## 🔓 How to Login

### Step 1: Visit Login Page
```
http://localhost:8000/admin/login/
```

Or on production (Render):
```
https://your-domain.onrender.com/admin/login/
```

### Step 2: Enter Credentials
```
Username: ayman
Password: 12345
```

### Step 3: Access Dashboard
After login, you'll be automatically redirected to:
```
http://localhost:8000/owner/dashboard/
```

Or visit directly:
```
http://localhost:8000/owner/dashboard/
```

---

## ✨ What You Can Do

✅ View all companies  
✅ See usage analytics  
✅ Create new companies  
✅ Manage subscriptions (upgrade/downgrade)  
✅ Suspend/reactivate companies  
✅ Rotate security keys  
✅ View reports & analytics  

❌ Cannot see employee data (screenshots, sessions, apps, websites)

---

## 🔑 Company Management

After logging in:

1. **Dashboard** - See all companies + KPIs
   - Click on company name for details
   - View usage metrics
   - See active users & storage

2. **Create Company** - Add new trial company
   - Set company name
   - Choose plan (FREE, PRO, ENTERPRISE)
   - Auto-generate security key

3. **Change Plan** - Upgrade or downgrade
   - Select new plan tier
   - Billing updated immediately

4. **Suspend Company** - Block access (emergency)
   - All desktop app syncs blocked (401)
   - Company data preserved
   - Can be reactivated

5. **Reactivate Company** - Restore access
   - Resume desktop app syncs
   - New 30-day trial period

6. **Rotate Key** - Security key rotation
   - Generate new company_key
   - Old key becomes inactive
   - 24-hour grace period

7. **Reports** - Analytics dashboard
   - Revenue by plan
   - Top companies by usage
   - Plan distribution

---

## 🔒 Security

### Your Password
```
Password: 12345
```

⚠️ **Security Reminder**:
- Keep this password secure
- Don't share with others
- Change if compromised
- Log out after use

### Company Keys
When managing companies, you'll see security keys like:
```
company_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p
```

These are used by desktop apps to authenticate. You can:
- 📋 Copy the key
- 🔄 Rotate the key
- 👁️ View history

---

## 🧪 Quick Test

1. Start server:
   ```bash
   cd backend
   python manage.py runserver
   ```

2. Login with:
   - URL: `http://localhost:8000/admin/login/`
   - Username: `ayman`
   - Password: `12345`

3. Verify you can:
   - ✅ Access dashboard
   - ✅ Create a test company
   - ✅ View company details
   - ✅ See analytics
   - ✅ Cannot see employee data

---

## 📱 Using on Different Devices

### Local Development
```
URL: http://localhost:8000/admin/login/
Username: ayman
Password: 12345
```

### Production (Render)
```
URL: https://your-domain.onrender.com/admin/login/
Username: ayman
Password: 12345
```

### Mobile Browser
Same credentials work on mobile browsers (responsive design)

---

## 🔄 If You Forget Password

To reset password:

```bash
cd backend
python manage.py shell << 'EOF'
from core.models import User
user = User.objects.get(username='ayman')
user.set_password('12345')  # Reset to original
user.save()
print("✅ Password reset to: 12345")
EOF
```

---

## 📞 Dashboard Features Overview

### Main Dashboard (`/owner/dashboard/`)
- 📊 Total companies count
- 📈 Active vs suspended companies
- 💾 Storage usage stats
- 👥 Total active users
- 📊 Table of all companies with quick actions

### Company Detail (`/owner/company/<id>/`)
- 📊 Usage analytics (last 90 days)
- 📈 Charts showing trends
- 📝 Subscription info
- 🔑 Security key (copy/rotate)
- 🎛️ Management controls

### Company Actions
```
Create  → /owner/company/create/
Update  → /owner/company/<id>/change-plan/
Suspend → /owner/company/<id>/suspend/
Restore → /owner/company/<id>/reactivate/
Rotate  → /owner/company/<id>/rotate-key/
```

### Reports (`/owner/reports/`)
- 📊 Company statistics
- 💰 Revenue breakdown
- 📉 Plan distribution
- 🏆 Top companies list

---

## ✅ Verification Checklist

After login, verify:

- [ ] Dashboard loads without errors
- [ ] Can see company list (or empty if no companies)
- [ ] Can create a new company
- [ ] Can view company details
- [ ] Company key is visible
- [ ] Can see analytics charts
- [ ] Cannot access admin section (forbidden)
- [ ] Cannot see employee data
- [ ] Can logout successfully

---

## 📚 Related Documentation

- [HOW_TO_LOGIN_OWNER_ACCOUNT.md](./HOW_TO_LOGIN_OWNER_ACCOUNT.md) - Complete login guide
- [OWNER_LOGIN_GUIDE.md](./OWNER_LOGIN_GUIDE.md) - Full featured guide
- [OWNER_LOGIN_FLOWCHART.md](./OWNER_LOGIN_FLOWCHART.md) - Visual diagrams
- [README_MULTITENANT.md](./README_MULTITENANT.md) - Multi-tenant system

---

## 🎉 You're Ready!

```
✅ Account Created: ayman
✅ Email: ayman@gmail.com
✅ Password: 12345
✅ Role: OWNER

READY TO LOGIN AND MANAGE COMPANIES! 🚀

URL: http://localhost:8000/admin/login/
Username: ayman
Password: 12345
```

---

**Created**: January 31, 2026  
**Account Status**: ✅ Active & Ready  
**Last Updated**: Today

**Keep this safe!** These are your OWNER credentials.
