# 📲 Render Shell এ Data Import করার নির্দেশনা

## এই Commands গুলো Render Shell এ চালান:

### ধাপ ১: Migrate করুন
```bash
python manage.py migrate
```

### ধাপ ২: Database Reset করুন (যদি users না থাকে)
```bash
# ⚠️ সাবধান - এটি সব data মুছে দেবে!
python manage.py flush --no-input
python manage.py migrate
```

### ধাপ ৩: Data Import করুন
```bash
python import_data.py
```

### ধাপ ৪: Verify করুন
```bash
python manage.py shell
```

Shell এ:
```python
from core.models import User
users = User.objects.all()
print(f"Total users: {users.count()}")
for u in users:
    print(f"  - {u.username} ({u.email}) - Role: {u.role}")
```

---

## যদি Specific Employees খুঁজে পেতে চান:
```python
from core.models import User
employees = User.objects.filter(role='EMPLOYEE')
print(f"Employees: {employees.count()}")
for emp in employees:
    print(f"  - {emp.username} ({emp.email})")
```

---

## Quick Step by Step:

1. Render Dashboard → Web Service → Shell
2. পেস্ট করুন: `python manage.py migrate`
3. পেস্ট করুন: `python import_data.py`
4. সাফল্যের বার্তা দেখতে পাবেন
5. Desktop app এ login করুন

---

## যদি Error দেখান:

### Error: "No such table"
```bash
python manage.py migrate --run-syncdb
```

### Error: "duplicate key"
```bash
python manage.py flush --no-input
python manage.py migrate
python import_data.py
```

### Error: "data_backup.json not found"
Backend folder এ file আছে কিনা check করুন (GitHub এ upload হয়েছে)

---

**এর পর আপনার local users দিয়ে desktop app এ login হতে পারবেন!** ✅
