# Desktop App Configuration Guide

## 🔧 API Server Configuration

আপনার Desktop App এখন **Production** mode এ চলছে এবং Render server এর সাথে connected।

### Current Configuration:
- **Environment**: `production`
- **API URL**: `https://employee-progress-tracker.onrender.com/api`

---

## 🔄 Local এবং Production এর মধ্যে Switch করা

### Option 1: config.py Edit করুন (Manual)

**Production Mode (Render Server):**
```python
ENVIRONMENT = "production"
```

**Local Mode (Local Development):**
```python
ENVIRONMENT = "local"
```

File: `tracker/config.py` - Line 13

---

## 🚀 কিভাবে ব্যবহার করবেন:

### Production এ Run করতে (Render Server):
1. `tracker/config.py` খুলুন
2. `ENVIRONMENT = "production"` নিশ্চিত করুন
3. App restart করুন
4. Login করুন - এটি Render server এর সাথে connect হবে

### Local Development এ Run করতে:
1. Local Django server চালু করুন: `python manage.py runserver`
2. `tracker/config.py` তে `ENVIRONMENT = "local"` set করুন
3. App restart করুন
4. এখন local server এর সাথে connect হবে

---

## ✅ Test করুন:

### 1. App চালু করুন:
```bash
cd D:\Employee-Progress-Tracker\tracker
python main.py
```

Console এ দেখবেন:
```
🌐 Running in PRODUCTION mode
📡 API URL: https://employee-progress-tracker.onrender.com/api
```

### 2. Login করুন:
- আপনার employee email এবং password দিয়ে login করুন
- যদি connection successful হয়, তাহলে dashboard দেখতে পাবেন

---

## ⚠️ গুরুত্বপূর্ণ নোট:

### Render Free Tier সম্পর্কে:
1. **Cold Start**: 15 মিনিট inactive থাকার পর প্রথম request এ 30-60 seconds সময় লাগবে
2. **Solution**: প্রথমবার login এ একটু wait করুন

### Connection Test:
প্রথমে browser এ check করুন:
```
https://employee-progress-tracker.onrender.com/api/dashboard/
```

যদি API respond করে, তাহলে desktop app ও কাজ করবে।

---

## 🐛 Troubleshooting:

### "Connection Failed" Error:
1. Internet connection check করুন
2. Render service running আছে কিনা verify করুন
3. Browser এ API URL test করুন

### Login Error:
1. Employee account তৈরি হয়েছে কিনা check করুন
2. Password correct আছে কিনা verify করুন
3. Database migrate হয়েছে কিনা check করুন

---

## 📱 User এর জন্য Distribution:

যখন employees কে app distribute করবেন:

1. `ENVIRONMENT = "production"` set করা থাকবে
2. PyInstaller দিয়ে executable তৈরি করুন:
```bash
pyinstaller --onefile --windowed main.py
```
3. Distribute করুন

এভাবে সবাই automatically Production server এ connect হবে! 🎉
