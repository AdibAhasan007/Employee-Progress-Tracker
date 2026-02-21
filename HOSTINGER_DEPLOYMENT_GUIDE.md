# Hostinger Deployment Guide - Employee Progress Tracker

## 📋 Pre-Deployment Checklist

- [ ] Hostinger account with cPanel access
- [ ] Multiple Python version support enabled
- [ ] MySQL database created
- [ ] FTP/SFTP access credentials
- [ ] SSL certificate (free via Let's Encrypt)
- [ ] Domain configured and pointed to Hostinger

---

## 🚀 Step 1: Database Setup (MySQL)

### In cPanel:
1. Go to **MySQL Databases**
2. Create new database: `tracker_db_2026`
3. Create new user: `tracker_user`
4. Set strong password
5. Add user to database with ALL privileges

**Your DATABASE_URL will be:**
```
mysql://tracker_user:password@localhost:3306/tracker_db_2026
```

---

## 🔧 Step 2: Setup Python Application

### 1. SSH into Hostinger via Terminal:
```bash
ssh cpanelusername@yourhostingerip
```

### 2. Navigate to public_html:
```bash
cd ~/public_html
```

### 3. Clone repository (or upload via FTP):
```bash
git clone https://github.com/yourusername/Employee-Progress-Tracker.git .
# or
# Upload files via FTP to /public_html
```

### 4. Create Python virtual environment:
```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 5. Install dependencies:
```bash
pip install --upgrade pip
pip install -r backend/requirements.txt
```

**Important:** Add MySQLdb support:
```bash
pip install mysqlclient==2.2.0
# Or use mysql-connector-python instead:
pip install mysql-connector-python
```

---

## 📝 Step 3: Environment Configuration

### Create `.env` in backend folder:
```bash
cd backend
nano .env.production
```

**Add this content (update with your values):**
```
DEBUG=False
SECRET_KEY=generate-using-python-secrets-module
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=mysql://tracker_user:YourPassword123@localhost:3306/tracker_db_2026

# Local storage (Hostinger doesn't need AWS)
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
EMAIL_HOST_PASSWORD=YourEmailPassword
```

### Generate a strong SECRET_KEY:
```bash
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(50))"
```

---

## 🗄️ Step 4: Database Migration

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

---

## ⚙️ Step 5: Gunicorn Setup

### Create gunicorn systemd service or use Hosinger's application manager

**Via cPanel Application Manager (Recommended):**
1. Go to cPanel → **Application Manager** (or **Node.js Manager** - Python apps similar)
2. Create new application pointing to `/home/username/public_html/backend`
3. Set Python version to 3.11
4. Entry file: `tracker_backend.wsgi:application`
5. Port: Auto-assigned (usually 3000+)

**Manual setup with Gunicorn:**
```bash
cd ~/public_html/backend
gunicorn tracker_backend.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

---

## 🔗 Step 6: Reverse Proxy via Apache

### cPanel Configuration or .htaccess:

In `public_html/.htaccess`:
```apache
<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteRule ^(.*)$ http://127.0.0.1:8000/$1 [P,L]
</IfModule>
```

**Better approach:** Use cPanel's **Auto Installer** or **Application Manager** for Django apps.

---

## 🔒 Step 7: SSL Certificate

### Via cPanel:
1. Go to **AutoSSL** or **Let's Encrypt SSL**
2. Select your domain
3. Install certificate (free)
4. Verify in browser: `https://yourdomain.com`

---

## 📂 Step 8: Media & Static Files

### Create directories:
```bash
mkdir -p ~/public_html/backend/staticfiles
mkdir -p ~/public_html/backend/media
chmod 755 ~/public_html/backend/staticfiles
chmod 755 ~/public_html/backend/media
```

### Nginx configuration (if applicable):
```nginx
location /static/ {
    alias /home/user/public_html/backend/staticfiles/;
}

location /media/ {
    alias /home/user/public_html/backend/media/;
}
```

---

## 🔄 Step 9: Background Jobs (Cron)

### For periodic tasks (if needed):
```bash
# In cPanel → Cron Jobs
# Run cleanup every day at 2 AM
0 2 * * * /home/username/public_html/venv/bin/python /home/username/public_html/backend/manage.py cleanup_old_screenshots
```

---

## 🧪 Step 10: Testing

### Test locally first:
```bash
cd backend
python manage.py runserver
```

### Test on Hostinger:
```bash
# SSH into Hostinger
curl http://localhost:8000
curl https://yourdomain.com
```

### Check logs:
```bash
# Application logs
tail -f ~/logs/access_log
tail -f ~/logs/error_log

# Django logs (if configured)
tail -f ~/public_html/backend/logs/django.log
```

---

## 🚨 Troubleshooting

### 1. ModuleNotFoundError
```bash
source ~/public_html/venv/bin/activate
pip install -r requirements.txt
```

### 2. Static files not loading
```bash
python manage.py collectstatic --clear --noinput
```

### 3. Database connection error
- Verify DATABASE_URL format
- Check MySQL credentials in cPanel
- Test: `mysql -u tracker_user -p -h localhost tracker_db_2026`

### 4. Permission denied
```bash
chmod -R 755 ~/public_html/backend
chmod -R 777 ~/public_html/backend/media
```

### 5. 500 Internal Server Error
```bash
# Enable debug logs
DEBUG=True in .env (temporarily)
# Check error_log in ~/logs/
```

---

## 📊 Performance Optimization

### 1. Enable mod_deflate (gzip):
```apache
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/html text/css text/javascript application/json
</IfModule>
```

### 2. Cache headers:
```python
# In settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'tracker-cache',
    }
}
```

### 3. Gunicorn workers optimization:
```bash
# Formula: (2 × Number of CPUs) + 1
gunicorn tracker_backend.wsgi:application --workers 5
```

---

## 🔐 Security Hardening

- [ ] Set `DEBUG=False` in production
- [ ] Use strong `SECRET_KEY`
- [ ] Enable SSL/HTTPS
- [ ] Configure firewall
- [ ] Regular backups (Hostinger automatic backups)
- [ ] Monitor error logs
- [ ] Update dependencies regularly

---

## 📞 Support

If issues persist:
1. Check Hostinger knowledge base
2. Contact Hostinger support (24/7 available)
3. SSH into server and check actual error logs
4. Ensure Python 3.11+ is selected in cPanel

---

**Installation Complete! 🎉**
Your Django application should now be running on Hostinger.
