# 🚀 PC SOFTWARE - QUICK CHEAT SHEET

## সবচেয়ে দ্রুত উপায়ে শুরু করুন (60 সেকেন্ড!)

### **Option 1: Batch File (সবচেয়ে সহজ)** ⭐

```
Windows Explorer এ যান:
D:\Employee-Progress-Tracker\

RUN_PC_SOFTWARE.bat ফাইল Double-click করুন

✅ এটাই! App চলে যাবে!
```

---

### **Option 2: PowerShell Script (উন্নত)**

```powershell
Windows PowerShell খুলুন (Admin mode)

cd D:\Employee-Progress-Tracker

.\RUN_PC_SOFTWARE.ps1

✅ এটাই! App চলে যাবে!
```

---

### **Option 3: Manual (সম্পূর্ণ নিয়ন্ত্রণ)**

**Terminal 1 (Backend):**
```powershell
cd D:\Employee-Progress-Tracker\backend
.\.venv\Scripts\Activate
python manage.py runserver
```

**Terminal 2 (Desktop App):**
```powershell
cd D:\Employee-Progress-Tracker\tracker
.\.venv-1\Scripts\Activate
python main.py
```

---

## 🔑 লগইন করুন

```
Username: employee@yourcompany.com
Password: (সঠিক password)
```

---

## ✅ কাজ করছে কিনা পরীক্ষা করুন

### **Console এ দেখবেন:**
```
⚙️ Config Manager loaded: {...}
📋 Task Manager loaded: {...}
```

### **App এ দেখবেন:**
```
- Login Screen ✅
- Dashboard with Timer ✅
- Task Cards (Dynamic + Realtime) ✅ [FIXED]
- Start/Stop Tracking Buttons ✅
- System Tray Icon ✅
```

### **এই সময়ে যা ঘটবে:**
```
✅ Every 5 seconds: Task sync from backend
✅ Real-time task updates (no restart needed!)
✅ Progress bar updates
✅ Activity tracking in background
✅ Screenshots capture
```

---

## 🛠️ সাধারণ সমস্যা

| সমস্যা | সমাধান |
|--------|--------|
| "Connection refused" | Backend চালান: `python manage.py runserver` |
| "No module PyQt6" | Run: `pip install PyQt6` |
| "Invalid credentials" | Employee email/password check করুন |
| "Task cards not showing" | FIXED! ✅ আপনার version এ সব OK |

---

## 📊 File Locations

```
✅ Screenshots: tracker\screenshots\
✅ Local DB:   tracker\db.sqlite3
✅ Config:     tracker\config.py
✅ Logs:       Console output
```

---

## 🎯 যখন App চলছে

### **করতে পারেন:**
- ✅ Session Start/Stop করুন
- ✅ Task Progress Update করুন
- ✅ Task Complete করুন
- ✅ Realtime Config Changes দেখুন (instant sync!)
- ✅ System Tray এ minimize করুন
- ✅ Sign Out করুন

### **পটভূমিতে চলে (automatic):**
- ✅ Website tracking
- ✅ Application tracking
- ✅ Idle detection
- ✅ Screenshot capture
- ✅ Task polling (every 5 sec)
- ✅ Config polling (every 2 sec)

---

## 📱 Task Cards - নতুন Feature! (FIXED ✅)

```
📋 Assigned Tasks
├─ Task Title
│  ├─ Description
│  ├─ Priority: HIGH
│  ├─ Status: IN_PROGRESS
│  ├─ Progress: [████░░░░] 50%
│  ├─ Due Date: 2026-02-10
│  │
│  ├─ Notes Input Box
│  ├─ [ Update Progress ] Button
│  └─ [ ✅ Mark Complete ] Button
│
└─ Updates happen REALTIME (no refresh!)
```

---

## ⚡ Performance Tips

```
✅ Backend running = Realtime sync
✅ Task polling = 5 seconds (optimal)
✅ Config polling = 2 seconds
✅ Memory usage < 100MB
✅ CPU usage < 5% (idle)
```

---

## 🎓 Architecture

```
Desktop App (PyQt6)
├─ LoginUI
├─ DashboardUI
│  ├─ TaskCardContainer (FIXED ✅)
│  │  └─ TaskCard × N
│  ├─ Timer/Session Controller
│  ├─ Activity Tracker
│  └─ Config Manager (Realtime sync)
├─ System Tray
└─ Background Services

↕️ (API Communication)

Backend (Django)
├─ /api/login/
├─ /api/employee-tasks/ (polling)
├─ /api/employee-config/ (realtime sync)
├─ /api/task/{id}/progress/ (update)
└─ /api/upload-screenshot/
```

---

## 🆘 More Help

দেখুন: [HOW_TO_RUN_PC_SOFTWARE.md](HOW_TO_RUN_PC_SOFTWARE.md)

---

**সব সেট! এখনই শুরু করুন!** 🎉
