# Employee Progress Tracker - Render Deployment Guide

## 📋 Render এ Host করার সম্পূর্ণ প্রক্রিয়া

### ✅ যে Files তৈরি করা হয়েছে:

1. **requirements.txt** - সব Python packages
2. **build.sh** - Deployment script
3. **render.yaml** - Render configuration
4. **.gitignore** - Git files ignore করার জন্য
5. **settings.py** - Production এর জন্য update করা হয়েছে

---

## 🚀 Render এ Deploy করার ধাপসমূহ:

### ধাপ ১: GitHub Repository তৈরি করুন

1. **GitHub.com** এ যান এবং login করুন
2. **New Repository** তৈরি করুন (নাম: employee-progress-tracker)
3. **Public** বা **Private** যেকোনো একটি select করুন

### ধাপ ২: Code GitHub এ Push করুন

আপনার project folder এ যান এবং এই commands চালান:

```bash
# Backend folder এ যান
cd D:\Employee-Progress-Tracker\backend

# Git initialize করুন
git init

# সব files add করুন
git add .

# Commit করুন
git commit -m "Initial commit for Render deployment"

# GitHub repository add করুন (আপনার username দিয়ে replace করুন)
git remote add origin https://github.com/YOUR_USERNAME/employee-progress-tracker.git

# Push করুন
git branch -M main
git push -u origin main
```

### ধাপ ৩: Render Account তৈরি করুন

1. **https://render.com** এ যান
2. **Sign Up** করুন (GitHub দিয়ে sign up করা best)
3. Free tier select করুন

### ধাপ ৪: PostgreSQL Database তৈরি করুন

1. Render dashboard এ **New +** বাটনে click করুন
2. **PostgreSQL** select করুন
3. এই information দিন:
   - **Name**: employee-tracker-db
   - **Database**: employee_tracker
   - **User**: employee_tracker_user
   - **Region**: Singapore (অথবা যেকোনো কাছের region)
   - **Plan**: Free
4. **Create Database** click করুন
5. Database তৈরি হওয়া পর্যন্ত অপেক্ষা করুন

### ধাপ ৫: Web Service তৈরি করুন

1. Render dashboard এ আবার **New +** click করুন
2. **Web Service** select করুন
3. আপনার GitHub repository connect করুন
4. Repository select করুন: **employee-progress-tracker**
5. এই configuration দিন:

   **Basic Settings:**
   - **Name**: employee-tracker
   - **Region**: Singapore
   - **Branch**: main
   - **Root Directory**: (খালি রাখুন যদি backend folder ই root হয়)
   - **Runtime**: Python 3
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn tracker_backend.wsgi:application`

   **Environment Variables:**
   Click **Advanced** → **Add Environment Variable**
   
   নিচের variables add করুন:
   ```
   PYTHON_VERSION = 3.11.0
   DEBUG = False
   SECRET_KEY = [Generate করুন বা random string দিন]
   DATABASE_URL = [আপনার PostgreSQL connection string]
   DJANGO_SETTINGS_MODULE = tracker_backend.settings
   ```

6. **Create Web Service** click করুন

### ধাপ ৬: Database URL যোগ করুন

1. PostgreSQL database page এ যান
2. **Internal Database URL** copy করুন
3. Web Service এর **Environment** tab এ যান
4. `DATABASE_URL` variable এ paste করুন
5. **Save Changes** click করুন

---

## 🔧 Build.sh File Executable করুন

Local machine এ (যদি Linux/Mac হয়):
```bash
chmod +x build.sh
git add build.sh
git commit -m "Make build.sh executable"
git push
```

Windows এ এটা করার দরকার নেই, Render automatically handle করবে।

---

## 📊 Deployment Check করুন

1. Render dashboard এ **Logs** দেখুন
2. Build সফল হলে আপনার site live হবে
3. URL হবে: `https://employee-tracker.onrender.com`

---

## 🔐 Admin User তৈরি করুন

Deploy হওয়ার পর, Render Shell থেকে admin create করুন:

1. Web Service page এ যান
2. **Shell** tab click করুন
3. এই command চালান:

```bash
python manage.py createsuperuser
```

Username, email এবং password দিন।

---

## ⚠️ Important Notes:

1. **Free tier** 15 মিনিট inactive থাকলে sleep mode এ যায়
2. **Database**: Free tier এ 90 days পর delete হয়ে যায়
3. **Media files**: Render free tier persistent storage support করে না
   - Media files এর জন্য **AWS S3** বা **Cloudinary** use করতে হবে
4. **Build time**: First deployment 5-10 মিনিট সময় নিতে পারে

---

## 🔄 Code Update করার প্রক্রিয়া:

আপনার code change করার পর:

```bash
git add .
git commit -m "Your update message"
git push
```

Render automatically নতুন code deploy করবে।

---

## 🆘 Troubleshooting:

### Build Failed?
- Render logs check করুন
- requirements.txt সব packages আছে কিনা verify করুন

### Database Connection Error?
- DATABASE_URL সঠিক আছে কিনা check করুন
- PostgreSQL database running আছে কিনা verify করুন

### Static Files না দেখাচ্ছে?
- `python manage.py collectstatic` command run হয়েছে কিনা check করুন
- STATIC_ROOT setting ঠিক আছে কিনা verify করুন

---

## 📱 Desktop App এর জন্য API URL:

আপনার desktop app এ API URL update করুন:
```
https://employee-tracker.onrender.com/api/
```

---

## ✨ সফল Deployment এর জন্য শুভকামনা!

কোনো সমস্যা হলে Render logs দেখুন অথবা আমাকে জিজ্ঞাসা করুন। 🚀
