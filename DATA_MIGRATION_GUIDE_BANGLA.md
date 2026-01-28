# 🗄️ Database Migration Guide - SQLite থেকে PostgreSQL এ

## আপনার Data Render এ Transfer করার সম্পূর্ণ প্রক্রিয়া

---

## পদ্ধতি ১: Django Dumpdata/Loaddata (সুপারিশকৃত) ✅

### ধাপ ১: Local Database থেকে Data Export করুন

আপনার local machine এ backend folder এ যান:

```bash
cd D:\Employee-Progress-Tracker\backend

# Data export করুন
python export_data.py
```

এটি একটি `data_backup.json` file তৈরি করবে যাতে সব data থাকবে।

### ধাপ ২: Backup File GitHub এ Upload করুন

```bash
git add data_backup.json
git commit -m "Add database backup for migration"
git push
```

### ধাপ ৩: Render এ Deploy করুন

প্রথমে আপনার application Render এ deploy করুন (RENDER_DEPLOYMENT_GUIDE_BANGLA.md দেখুন)।

### ধাপ ৪: Render Shell থেকে Data Import করুন

1. Render dashboard এ যান
2. আপনার Web Service select করুন
3. **Shell** tab এ click করুন
4. এই commands চালান:

```bash
# Migrations run করুন (যদি না হয়ে থাকে)
python manage.py migrate

# Data import করুন
python import_data.py
```

✅ **সম্পন্ন!** আপনার সব data এখন PostgreSQL এ আছে।

---

## পদ্ধতি ২: Manual Django Commands

### Local থেকে Export:

```bash
python manage.py dumpdata --natural-foreign --natural-primary --indent 2 \
  --exclude contenttypes --exclude auth.permission \
  --exclude admin.logentry --exclude sessions.session \
  > data_backup.json
```

### Render Shell এ Import:

```bash
python manage.py loaddata data_backup.json
```

---

## পদ্ধতি ৩: শুধু Admin User তৈরি করুন (Fresh Start)

যদি আপনি পুরনো data না চান এবং fresh start করতে চান:

### Render Shell এ:

```bash
# Admin user তৈরি করুন
python manage.py createsuperuser

# Company settings তৈরি করুন (optional)
python manage.py shell
```

Python shell এ:
```python
from core.models import CompanySettings

CompanySettings.objects.create(
    company_name="Your Company Name",
    company_tagline="Employee Activity Tracker",
    daily_target_hours=8.0
)
exit()
```

---

## 📸 Media Files (Screenshots, Profile Pictures) Migration

### ⚠️ গুরুত্বপূর্ণ সতর্কতা:

Render free tier **persistent file storage** support করে না। অর্থাৎ:
- Server restart হলে uploaded files হারিয়ে যাবে
- Screenshots এবং profile pictures save থাকবে না

### 💡 সমাধান: Cloud Storage ব্যবহার করুন

#### Option 1: AWS S3 (Recommended)

1. **AWS S3 bucket** তৈরি করুন
2. Django-storages install করুন:

```bash
# requirements.txt এ add করুন
django-storages
boto3
```

3. **settings.py** update করুন:

```python
# AWS S3 Configuration
if not DEBUG:
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = 'ap-south-1'
    
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
```

#### Option 2: Cloudinary (Free Tier Available)

```bash
# requirements.txt এ add করুন
cloudinary
django-cloudinary-storage
```

**settings.py:**
```python
INSTALLED_APPS = [
    # ...
    'cloudinary_storage',
    'cloudinary',
]

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET')
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

---

## 🔍 Media Files List দেখুন

Local এ কি কি media files আছে দেখার জন্য:

```bash
python migrate_media_files.py
```

---

## ✅ Migration Checklist

### Before Migration:
- [ ] SQLite database backup নিন (`data_backup.json`)
- [ ] Media files এর list তৈরি করুন
- [ ] Cloud storage setup করুন (যদি media files আছে)

### During Migration:
- [ ] Code GitHub এ push করুন
- [ ] Render এ deploy করুন
- [ ] Database migrations run করুন
- [ ] Data import করুন

### After Migration:
- [ ] Admin user login করুন
- [ ] Data verify করুন
- [ ] All features test করুন
- [ ] Desktop app এর API URL update করুন

---

## 🔧 Troubleshooting

### Data Import এ Error?

**Problem:** `IntegrityError` বা duplicate key error

**Solution:**
```bash
# Database reset করুন (⚠️ সাবধান - সব data মুছে যাবে)
python manage.py flush --no-input

# আবার import করুন
python import_data.py
```

### Migration Run হচ্ছে না?

```bash
# Migration files check করুন
python manage.py showmigrations

# Migrations run করুন
python manage.py migrate --run-syncdb
```

### Specific App এর Data Import করুন:

```bash
# শুধু users
python manage.py dumpdata core.User > users.json
python manage.py loaddata users.json

# শুধু tasks
python manage.py dumpdata core.Task > tasks.json
python manage.py loaddata tasks.json
```

---

## 📞 Support

কোনো সমস্যা হলে:
1. Render logs check করুন
2. Django error messages পড়ুন
3. Database connection verify করুন

---

## 🎯 Quick Commands Summary

```bash
# Local এ data export
python export_data.py

# Render Shell এ
python manage.py migrate
python import_data.py
python manage.py createsuperuser

# Media files list
python migrate_media_files.py
```

---

**সফল Migration এর জন্য শুভকামনা!** 🚀
