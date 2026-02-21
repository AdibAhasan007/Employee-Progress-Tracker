# Hostinger Configuration - What Changed

## 📋 Summary of Updates

### Created Files:
1. ✅ `.env.production` - Production template with Hostinger settings
2. ✅ `.htaccess` - Apache rewrite rules for Hostinger
3. ✅ `requirements_hostinger.txt` - Dependencies with MySQL support
4. ✅ `HOSTINGER_DEPLOYMENT_GUIDE.md` - Complete deployment instructions
5. ✅ `HOSTINGER_SETUP_QUICK_REFERENCE.md` - Quick setup guide

### Modified Files:
1. ✅ `backend/tracker_backend/settings.py` - Multiple updates

---

## 🔄 Detailed Changes to settings.py

### 1. **ALLOWED_HOSTS** (Line ~18)
**Before:**
```python
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
```

**After:**
```python
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS]  # Remove whitespace

# Hostinger/cPanel support
if os.environ.get('ALLOW_SUBDOMAINS') == 'True':
    ALLOWED_HOSTS.append('*')
```

**Why:** Removes whitespace issues + supports wildcard subdomains for Hostinger

---

### 2. **DATABASE Configuration** (Line ~84)
**Before:**
```python
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR.parent / 'database' / 'db.sqlite3',
        }
    }
```

**After:**
```python
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
            engine='django.db.backends.mysql'  # For Hostinger MySQL support
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR.parent / 'database' / 'db.sqlite3',
        }
    }
```

**Why:** Explicitly supports MySQL backend for Hostinger

---

### 3. **MEDIA STORAGE Configuration** (Line ~135)
**Before:**
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# AWS S3 media storage for production
if not DEBUG:
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'ap-south-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_DEFAULT_ACL = None

    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
```

**After:**
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Media Storage Configuration
USE_LOCAL_STORAGE = os.environ.get('USE_LOCAL_STORAGE', 'True') == 'True'

if not DEBUG and not USE_LOCAL_STORAGE:
    # AWS S3 settings for media files (production with S3)
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'ap-south-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_DEFAULT_ACL = None
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}

    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
else:
    # Local file storage for Hostinger or development
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
```

**Why:** Allows local storage (Hostinger default) instead of forcing AWS S3

---

### 4. **CORS Settings** (Line ~161)
**Before:**
```python
CORS_ALLOW_ALL_ORIGINS = True
```

**After:**
```python
# CORS Settings
if DEBUG:
    # Development: Allow all origins
    CORS_ALLOW_ALL_ORIGINS = True
else:
    # Production: Only allow specific origins
    ALLOWED_CORS_ORIGINS = os.environ.get(
        'ALLOWED_CORS_ORIGINS', 
        'https://yourdomain.com,https://www.yourdomain.com'
    ).split(',')
    CORS_ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_CORS_ORIGINS]
    CORS_ALLOW_ALL_ORIGINS = False
```

**Why:** Restricts CORS to specific origins in production (security best practice)

---

### 5. **SECURITY Settings** (Line ~172)
**Before:**
```python
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
else:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
```

**After:**
```python
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # Additional Hostinger recommendations
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Cookie settings
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    CSRF_COOKIE_SAMESITE = 'Strict'
else:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
```

**Why:** Adds HSTS and stricter cookie security for production

---

## 🌍 Environment Variables Needed for Hostinger

Create `.env` file in `backend/` folder with:

```env
# Django Configuration
DEBUG=False
SECRET_KEY=<generate-new-strong-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (MySQL on Hostinger)
DATABASE_URL=mysql://tracker_user:password@localhost:3306/tracker_db_2026

# Media Storage
USE_LOCAL_STORAGE=True

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Email (Hostinger SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.hostinger.com
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_HOST_USER=your-email@yourdomain.com
EMAIL_HOST_PASSWORD=your-password

# CORS
ALLOWED_CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

---

## 📦 Dependencies Added to requirements.txt

### New Package:
```
mysqlclient>=2.2.0
```

**Why:** Required for MySQL database connections on Hostinger

---

## ✨ New Features Enabled:

| Feature | Status | Details |
|---------|--------|---------|
| MySQL Support | ✅ | Now compatible with Hostinger MySQL |
| Local Media Storage | ✅ | No AWS S3 required |
| HSTS Security | ✅ | Enforces HTTPS for 1 year |
| Stricter CORS | ✅ | Only allows specified origins |
| Cookie Security | ✅ | HttpOnly + SameSite=Strict |
| Apache Rewrite Rules | ✅ | Via .htaccess file |

---

## 🚀 Ready for Deployment!

All files are now configured for Hostinger deployment. Follow the steps in:
- `HOSTINGER_DEPLOYMENT_GUIDE.md` - Full guide
- `HOSTINGER_SETUP_QUICK_REFERENCE.md` - Quick setup

**Next actions:**
1. Transfer files to Hostinger via FTP
2. Create MySQL database in cPanel
3. Create `.env` file with your values
4. Run migrations
5. Collect static files
6. Setup Gunicorn via cPanel Application Manager
