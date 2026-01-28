# 👨‍💼 Render এ Admin User তৈরি করার সম্পূর্ণ গাইড

## 🚀 দ্রুত সমাধান (2 মিনিটে):

### ধাপ ১: Render Shell খুলুন
1. https://dashboard.render.com যান
2. **Employee-Progress-Tracker** service click করুন
3. **Shell** tab এ যান

### ধাপ ২: এই Command চালান

```bash
cd backend
python create_admin.py
```

**Done!** ✅ Admin account তৈরি হয়ে গেছে!

---

## 📋 Default Admin Credentials:

```
Username: admin
Email: admin@yourcompany.com
Password: Admin@123
```

---

## 🔗 Admin এ Login করুন:

### Web Admin Panel:
```
https://employee-progress-tracker.onrender.com/login/

Username: admin
Password: Admin@123
```

### Django Admin:
```
https://employee-progress-tracker.onrender.com/admin/
```

---

## 🎯 Custom Admin User তৈরি করতে:

### Local Test করুন:
```bash
cd backend
python create_admin.py --custom myusername myemail@example.com mypassword123
```

### Render Shell এ:
```bash
cd backend
python create_admin.py --custom myusername myemail@example.com mypassword123
```

---

## 🛠️ Alternative Method: Django Shell ব্যবহার করুন

Render Shell এ এই commands চালান:

```bash
cd backend
python manage.py shell
```

Python Shell এ:
```python
from core.models import User

# Admin user create করুন
admin = User.objects.create_superuser(
    username='admin',
    email='admin@company.com',
    password='your_secure_password',
    first_name='Admin',
    last_name='User'
)

# ADMIN role set করুন
admin.role = 'ADMIN'
admin.save()

print(f"✅ Admin '{admin.username}' created!")
exit()
```

---

## ✅ Admin User Verify করুন:

Render Shell এ:
```bash
python manage.py shell
```

```python
from core.models import User

# সব admins দেখুন
admins = User.objects.filter(role='ADMIN')
print(f"Admin users: {admins.count()}")
for admin in admins:
    print(f"  - {admin.username} ({admin.email})")

exit()
```

---

## 🔄 Admin Password পরিবর্তন করতে:

Render Shell এ:
```bash
python manage.py changepassword admin
```

নতুন password দিন।

---

## ⚠️ সতর্কতা:

1. **Password Strong রাখুন**: অন্তত 12+ characters, numbers এবং symbols সহ
2. **Email Unique রাখুন**: প্রতিটি admin এর আলাদা email থাকা উচিত
3. **First deployment**: Database সম্পূর্ণ empty থাকলে এই steps follow করুন

---

## 🎯 সম্পূর্ণ Setup Checklist:

- [ ] Render Shell খোলা আছে
- [ ] `cd backend` করেছেন
- [ ] `python create_admin.py` run করেছেন
- [ ] Admin account তৈরি হয়েছে
- [ ] Web site এ login করেছেন
- [ ] Dashboard access করছেন

**সব Done? তাহলে আপনার Render setup সম্পূর্ণ!** 🎉

---

## 📞 Troubleshooting:

### Error: "create_admin.py not found"
```bash
cd ..
git pull
cd backend
python create_admin.py
```

### Error: "Admin user already exists"
এটা মানে admin user আগে থেকেই আছে। দুটি option:
1. এই admin account দিয়ে login করুন
2. নতুন admin তৈরি করুন: `python create_admin.py --custom newadmin newemail@example.com password`

### Error: "Permission denied"
নিশ্চিত করুন যে:
- Database migrations run হয়েছে: `python manage.py migrate`
- Database connected আছে: DATABASE_URL environment variable set আছে

---

**এখনই করুন!** Render Shell এ যান এবং admin account create করুন! 🚀
