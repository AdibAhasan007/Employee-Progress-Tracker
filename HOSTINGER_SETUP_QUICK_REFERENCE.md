# Hostinger Setup - Quick Reference

## 🎯 Files Created/Updated:

✅ `.env.production` - Production environment variables  
✅ `.htaccess` - Apache configuration for Hostinger  
✅ `settings.py` - Updated for production + MySQL + local storage  
✅ `requirements_hostinger.txt` - With MySQL support  
✅ `HOSTINGER_DEPLOYMENT_GUIDE.md` - Full deployment guide  

---

## 🔴 Critical Setup Steps:

### 1. **Create `.env` file on Hostinger** (in backend folder):
```
DEBUG=False
SECRET_KEY=<generate-new-strong-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=mysql://user:pass@localhost:3306/dbname
USE_LOCAL_STORAGE=True
```

### 2. **Create MySQL Database** (via cPanel):
- Database: `tracker_db_2026`
- User: `tracker_user`
- Password: `<strong-password>`

### 3. **Run Migrations**:
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### 4. **Setup Gunicorn** (via cPanel Application Manager):
- Entry point: `tracker_backend.wsgi:application`
- Python version: 3.11+

### 5. **Configure SSL**:
- Enable Let's Encrypt (free in cPanel)

---

## 📊 Configuration Summary:

| Setting | Value |
|---------|-------|
| **Database** | MySQL (Hostinger) |
| **Media Storage** | Local `/media/` folder |
| **Static Files** | Collected in `/staticfiles/` |
| **Security** | HTTPS enforced, HSTS enabled |
| **CORS** | Restricted to your domain |
| **Debug** | Disabled in production |

---

## 🛠️ Important Files Location:

```
backend/
├── .env (CREATE this on Hostinger with your values)
├── settings.py (UPDATED - already done ✓)
├── requirements_hostinger.txt (NEW - with MySQL)
├── staticfiles/ (collect_static here)
├── media/ (user uploads here)
└── manage.py
```

---

## ⚠️ Common Issues & Fixes:

### MySQLdb ImportError:
```bash
pip install mysqlclient==2.2.0
# If fails, use:
pip install mysql-connector-python
```

### Static files missing:
```bash
python manage.py collectstatic --clear --noinput
chmod -R 755 staticfiles/
```

### Media upload permission error:
```bash
chmod -R 777 media/
chmod -R 777 staticfiles/
```

### 500 Internal Server Error:
```bash
# Check error logs
tail -f ~/logs/error_log
tail -f ~/logs/access_log
```

---

## 📋 Pre-Deployment Checklist:

- [ ] Update `.env` with real database credentials
- [ ] Generate new SECRET_KEY
- [ ] Set ALLOWED_HOSTS to your domain
- [ ] Create MySQL database
- [ ] Run migrations
- [ ] Collect static files
- [ ] Set up Gunicorn in cPanel
- [ ] Enable SSL certificate
- [ ] Test with HTTPS

---

## 🚀 After Deployment:

1. **Access admin panel:**
   ```
   https://yourdomain.com/admin/
   ```

2. **Create company:**
   - Login as superuser
   - Add Company with Plan

3. **Add employees:**
   - Create user accounts
   - Assign to company

4. **Test desktop app:**
   - Download desktop app
   - Login with employee credentials

---

## 📞 Next Steps:

1. Read `HOSTINGER_DEPLOYMENT_GUIDE.md` for detailed instructions
2. Contact Hostinger support if issues with cPanel
3. Monitor error logs after first deployment
4. Set up automated backups

**All configuration ready! 🎉**
