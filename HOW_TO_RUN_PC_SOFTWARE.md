# 🚀 PC SOFTWARE চালানোর সম্পূর্ণ গাইড

**Date:** February 3, 2026
**Status:** ✅ Ready to Run

---

## 📋 **প্রয়োজনীয় জিনিস**

### **1. Backend Server চলছে কি?**
```bash
❌ Backend চালু না থাকলে → Error হবে
✅ Backend চালু থাকলে → সব কাজ করবে
```

### **2. Python Requirements**
```
✅ Python 3.10+
✅ PyQt6
✅ requests
✅ Pillow
✅ pygetwindow
✅ wmi
✅ lz4
```

---

## 🔧 **Step 1: Backend Setup করুন**

### **Windows PowerShell এ:**

```powershell
# Backend ফোল্ডারে যান
cd D:\Employee-Progress-Tracker\backend

# Virtual environment activate করুন (যদি নেই তো তৈরি করুন)
python -m venv .venv
.\.venv\Scripts\Activate

# Dependencies install করুন
pip install -r requirements.txt

# Database migrate করুন (প্রথমবার)
python manage.py migrate

# Django server চালান
python manage.py runserver
```

**ফলাফল যা দেখা উচিত:**
```
Watching for file changes with StatReloader
Starting development server at http://127.0.0.1:8000/
```

✅ Backend চলছে! (এই terminal বন্ধ করবেন না)

---

## 📱 **Step 2: Desktop App Setup করুন**

### **নতুন PowerShell Terminal খুলুন:**

```powershell
# Tracker ফোল্ডারে যান
cd D:\Employee-Progress-Tracker\tracker

# Virtual environment activate করুন
# (একই venv ব্যবহার করুন যা backend এ আছে)
cd D:\Employee-Progress-Tracker
.\.venv-1\Scripts\Activate

# Tracker requirements install করুন
cd tracker
pip install -r requirements.txt
```

**প্রয়োজনীয় packages:**
```
PyQt6
requests
Pillow
pygetwindow
wmi
lz4
```

---

## ▶️ **Step 3: Desktop App চালান**

### **তিনটি উপায়:**

#### **Way 1: Terminal থেকে চালান (সবচেয়ে ভাল)**

```powershell
cd D:\Employee-Progress-Tracker\tracker
python main.py
```

**আপনি দেখবেন:**
```
⚙️ Config Manager loaded: {...}
📋 Task Manager loaded: {...}
✅ Application started successfully
```

#### **Way 2: Direct File থেকে**

Windows Explorer এ যান:
```
D:\Employee-Progress-Tracker\tracker\main.py
```

Double-click করুন → App চলবে

#### **Way 3: VS Code থেকে**

1. `main.py` ফাইল খুলুন
2. Right-click করুন
3. "Run Python File" বেছে নিন

---

## 🎯 **এখন কী ঘটবে?**

### **1. Login Screen দেখা যাবে**

```
┌─────────────────────────────────┐
│                                 │
│   🔐 Employee Login              │
│                                 │
│   Username: [____________]      │
│   Password: [____________]      │
│                                 │
│   [ Login ]                     │
│                                 │
└─────────────────────────────────┘
```

### **2. Employee Credentials দিন**

```
Username: john@example.com
Password: (সঠিক password)
```

### **3. Dashboard দেখা যাবে**

```
┌──────────────────────────────────┐
│   👤 Employee Name               │
│   ⏱️ Timer: 00:00:00              │
│                                  │
│   [ START TRACKING ]             │
│                                  │
│   📋 Assigned Tasks              │
│   ├─ Task 1 [50%]                │
│   ├─ Task 2 [25%]                │
│   └─ Task 3 [NEW]                │
│                                  │
│   [Sign Out]                     │
└──────────────────────────────────┘
```

---

## 🔑 **Login করার আগে জানুন**

### **কোন ধরনের Users Login করতে পারে:**

| User Type | Email Pattern | Password |
|-----------|---------------|----------|
| Employee | emp@company.com | ✅ Can login |
| Admin | admin@company.com | ❌ Cannot (Desktop এ) |
| Owner | owner@company.com | ❌ Cannot (Desktop এ) |

**Note:** Desktop app শুধুমাত্র **Employees** এর জন্য।

---

## 📊 **Desktop App Folder Structure**

```
D:\Employee-Progress-Tracker\tracker\
├── main.py                    ← 🚀 এটা রান করবেন
├── login_ui.py               ← Login screen
├── dashboard_ui.py           ← Main dashboard
├── task_ui.py                ← Task cards (FIXED ✅)
├── task_manager.py           ← Realtime task sync
├── config_manager.py         ← Config sync
├── activity_tracker.py       ← Monitor activity
├── screenshot_controller.py  ← Screenshot capture
├── work_session_controller.py ← Session management
├── website_usage.py          ← Website tracking
├── application_usage.py      ← App tracking
├── config.py                 ← Configuration
├── db_init.py                ← Database setup
├── requirements.txt          ← Dependencies
└── README.md                 ← Documentation
```

---

## 🛠️ **যদি Error হয়?**

### **Error 1: `ModuleNotFoundError: No module named 'PyQt6'`**

```powershell
# সমাধান:
pip install PyQt6
```

### **Error 2: `Connection refused` (Backend সংযোগ ব্যর্থ)**

```
❌ Backend server চলছে না!
✅ Backend terminal এ যান এবং চালান:
   python manage.py runserver
```

### **Error 3: `Invalid credentials`**

```
❌ Email বা password ভুল
✅ Django admin থেকে employee verify করুন:
   python manage.py createsuperuser
```

### **Error 4: `No module named 'requests'`**

```powershell
# সমাধান:
pip install requests Pillow pygetwindow wmi lz4
```

---

## ✅ **সফলভাবে চলছে কিনা তা জানুন**

### **Console Output দেখুন:**

```
✅ সবকিছু OK:
⚙️ Config Manager loaded: {'employee_id': 1, 'cached_tasks': 0, ...}
📋 Task Manager loaded: {'employee_id': 1, 'cached_tasks': 0, ...}
📋 3 new task(s) assigned
✅ 1 task(s) completed/removed
Offline mode - Using 2 cached tasks
Task check error: ...  ← কিছু থেকে কম গুরুত্বপূর্ণ

❌ কোন সমস্যা আছে:
Traceback (most recent call last):  ← Critical error!
Connection refused             ← Backend যোগাযোগ ব্যর্থ
ModuleNotFoundError            ← Package missing
```

---

## 🎮 **Desktop App এ কী করা যায়?**

### **1. Work Session Management**
```
[ START TRACKING ]  ← সেশন শুরু করুন
(Timer চলবে, স্ক্রিনশট capture হবে)
[ STOP ]            ← সেশন বন্ধ করুন
```

### **2. Task Management (🆕 FIXED)**
```
📋 Assigned Tasks
├─ Task Title
│  └─ Progress: [████░░░░] 50%
│  └─ Status: IN_PROGRESS
│  └─ Priority: HIGH
│  └─ [ Update Progress ]
│  └─ [ ✅ Mark Complete ]
```

### **3. Activity Tracking**
```
Background monitoring:
✅ Active window tracking
✅ Website usage
✅ Application usage
✅ Idle time detection
✅ Screenshot capture
```

### **4. System Tray**
```
Right-click system tray icon:
├─ Show App
├─ Status
└─ Exit
```

### **5. Real-time Configuration Sync**
```
Admin যা settings change করবে:
├─ Screenshot size
├─ Screenshot quality
├─ Tracking enabled/disabled
├─ Idle detection
└─ সব কিছু instantly apply হবে (নোরিস্টার্ট!)
```

---

## 🔄 **Realtime Task Cards এখন কাজ করবে**

### **Flow:**
```
Admin Dashboard
    ↓
   (Task assign/update)
    ↓
Backend API
    ↓
Desktop App (Every 5 seconds polling)
    ↓
TaskCardContainer (PyQt6 - FIXED ✅)
    ↓
Task Card Display
    ↓
Employee Updates Progress
    ↓
Changes Saved to Backend
```

---

## 🚨 **গুরুত্বপূর্ণ Notes**

### **1. Backend অবশ্যই চলছে থাকতে হবে**
```
যদি Backend বন্ধ হয়:
- Task sync কাজ করবে না
- Config sync কাজ করবে না
- Session save হবে না
- Local cache থেকে data show হবে (fallback)
```

### **2. Multiple Instances**
```
একই user থেকে আলাদা PC তে:
✅ একই সময়ে চলতে পারে
✅ প্রতিটির নিজস্ব session থাকবে
✅ প্রতিটির নিজস্ব config থাকবে
```

### **3. Offline Mode**
```
Internet নেই?
✅ Local cache থেকে tasks দেখা যাবে
✅ Activity tracking চলবে
✅ Internet ফিরলে sync হবে
```

### **4. Screenshots**
```
সংরক্ষিত হয়:
📁 D:\Employee-Progress-Tracker\tracker\screenshots\
```

### **5. Database**
```
Local DB:
📁 D:\Employee-Progress-Tracker\tracker\db.sqlite3
```

---

## 📝 **Quick Start (সংক্ষিপ্ত)**

```powershell
# Terminal 1 - Backend
cd D:\Employee-Progress-Tracker\backend
.\.venv\Scripts\Activate
python manage.py runserver

# Terminal 2 - Desktop App
cd D:\Employee-Progress-Tracker\tracker
.\.venv-1\Scripts\Activate
python main.py
```

**এটাই!** ✅ App চলবে!

---

## 🎯 **যা করার পরে দেখুন**

1. ✅ **Login করুন** - Employee credentials ব্যবহার করুন
2. ✅ **Dashboard দেখুন** - Timer এবং Tasks দৃশ্যমান হবে
3. ✅ **Task Card Display** - Dynamic cards দেখা যাবে (FIXED!)
4. ✅ **Start Tracking** - Session শুরু করুন
5. ✅ **Update Tasks** - Progress update করুন
6. ✅ **Check Sync** - Real-time updates কাজ করছে কিনা যাচাই করুন

---

## 🆘 **Help দরকার?**

### **যদি কোন সমস্যা হয়:**

1. **Console output দেখুন** - কী error আছে?
2. **Backend চলছে কিনা check করুন** - `http://127.0.0.1:8000/` খুলুন
3. **Database আছে কিনা দেখুন** - `db.sqlite3` file দেখুন
4. **Logs দেখুন** - Console output থেকে exact error message খুঁজুন

---

**আপনার PC Software এখন সম্পূর্ণভাবে প্রস্তুত এবং Dynamic Task Cards সহ চলবে!** 🎉

