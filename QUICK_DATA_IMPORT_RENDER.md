# 🚀 Render Shell এ Data Import করার সহজ নির্দেশনা

## এখনই করুন (3 ধাপে):

### ধাপ ১: Render Dashboard খুলুন
1. https://dashboard.render.com এ যান
2. **Employee-Progress-Tracker** service select করুন
3. **Shell** tab click করুন

### ধাপ ২: এই Commands Copy-Paste করুন

**প্রথমে:**
```bash
cd backend
python manage.py migrate
```

**তারপর:**
```bash
python recover_user_data.py
```

### ধাপ ৩: Verify করুন
```bash
python manage.py shell
```

এটা Shell এ:
```python
from core.models import User
print(f"Total users: {User.objects.count()}")
```

---

## কি হবে?

✅ আপনার সব local users Render এ import হয়ে যাবে
✅ Desktop app এ login সফল হবে
✅ সব existing data থাকবে

---

## যদি Problem হয়:

### Error: "recover_user_data.py not found"
Repository update করুন:
```bash
cd ..
git pull
cd backend
```

### Error: "data_backup.json not found"  
এটি local তে আছে, GitHub এ push করুন:
```bash
# Local machine এ:
cd backend
git add data_backup.json
git commit -m "Add data backup"
git push
```

---

## Demo User তৈরি করতে (Quick Test):
```bash
python recover_user_data.py --demo
```

এটি create করবে:
- **Username**: demo
- **Email**: demo@example.com
- **Password**: demo123

---

**এর পর desktop app এ login হতে পারবেন!** ✅

```
Email: demo@example.com
Password: demo123
```

বা আপনার আসল employees দিয়ে login করুন (সব import হয়েছে)।
