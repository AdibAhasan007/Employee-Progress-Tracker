# 🎯 REAL-TIME TASK MANAGEMENT - QUICK START GUIDE

## 🚀 5-Minute Setup

### Step 1: Verify Database Migration Applied

```bash
cd backend
python manage.py migrate
```

Expected output:
```
Applying core.0007_taskprogress_alter_task_options_and_more... OK
```

### Step 2: Start Backend Server

```bash
python manage.py runserver 0.0.0.0:8000
```

### Step 3: Start Desktop App

```bash
cd ../tracker
python main.py
```

---

## 👨‍💼 Admin Quick Start

### Assign Your First Task

1. Open browser → `http://localhost:8000/dashboard/tasks/assign/`
2. Fill in:
   - **Task Title:** "Test Project Delivery"
   - **Employee:** Select an employee
   - **Priority:** HIGH
   - **Due Date:** Tomorrow
3. Click "Assign Task"
4. ✅ Task created!

### Monitor Task Progress

1. Go to `http://localhost:8000/dashboard/tasks/monitor/`
2. Watch the task appear on the grid
3. See progress updates in real-time
4. Click filter buttons to organize

### Check Analytics

1. Go to `http://localhost:8000/dashboard/tasks/statistics/`
2. View completion rates, employee performance, occupancy data

---

## 💼 Employee Quick Start

### View Your Tasks

1. Open desktop app → Dashboard
2. You'll see "📋 Assigned Tasks" section
3. Tasks refresh automatically every 5 seconds

### Update Progress

1. Click on a task card
2. Click progress bar OR use quick buttons (25%, 50%, 75%, 100%)
3. Add optional notes
4. Click "Update Progress"
5. ✅ Changes appear in admin dashboard within 5 seconds

### Complete a Task

1. When finished, click "✓ Mark Complete"
2. Task moves to "Completed" section
3. Appears in admin analytics

---

## 📊 Real-time Features at a Glance

| Feature | Location | Auto-Refresh |
|---------|----------|--------------|
| Task Assignment | `/dashboard/tasks/assign/` | N/A |
| Task Monitoring | `/dashboard/tasks/monitor/` | Every 5 sec |
| Task Progress | Desktop App | Every 5 sec |
| Analytics | `/dashboard/tasks/statistics/` | Manual |
| Occupancy Status | Admin Dashboard | Every 5 sec |

---

## 🔧 Customization

### Change Polling Interval

Edit `tracker/dashboard_ui.py`:
```python
# Change from 5000ms to 3000ms (3 seconds)
self.task_check_timer.start(3000)
```

### Offline Mode

- Tasks automatically cached in `~/.tracker_app/task_cache.json`
- Works when network is down
- Auto-syncs when online

### Priority Colors

Edit `tracker/task_ui.py` to customize colors:
```python
# LOW = green, MEDIUM = yellow, HIGH = red, URGENT = purple
```

---

## 🐛 Troubleshooting

### Tasks Not Showing in Admin Dashboard?

1. ✅ Check migration was applied: `python manage.py migrate`
2. ✅ Verify employee has role='EMPLOYEE'
3. ✅ Check task.status in [PENDING, OPEN, IN_PROGRESS]
4. ✅ Refresh browser (F5)

### Progress Not Updating?

1. ✅ Check network connection
2. ✅ Verify auth token is valid
3. ✅ Check API endpoint: `GET http://localhost:8000/api/employee-tasks/`
4. ✅ Look at browser console (F12) for errors

### Desktop App Not Getting Tasks?

1. ✅ Restart desktop app
2. ✅ Check `~/.tracker_app/task_cache.json` exists
3. ✅ Verify employee_id in app matches database
4. ✅ Check firewall isn't blocking port 8000

---

## 📚 API Quick Reference

### Get Employee Tasks
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/employee-tasks/
```

### Update Task Progress
```bash
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"progress_percentage": 75, "notes": "On track"}' \
  http://localhost:8000/api/task/1/progress/
```

### Mark Task Complete
```bash
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"completion_notes": "Finished!"}' \
  http://localhost:8000/api/task/1/complete/
```

### Get Admin Task Status
```bash
curl -H "Authorization: Bearer ADMIN_TOKEN" \
  http://localhost:8000/api/admin/task-status/
```

---

## ✨ Key Insights

### Progress Auto-Status Updates

```
Progress: 0%     → Status: PENDING
Progress: 1-99%  → Status: IN_PROGRESS  (auto-changed)
Progress: 100%   → Status: DONE         (auto-changed)
```

### Occupancy Tracking

```
Active Time    → occupancy_status: ACTIVE    (🟢 Green)
Idle Time      → occupancy_status: IDLE      (🟠 Orange)
Offline        → occupancy_status: OFFLINE   (⚫ Gray)
```

### Audit Trail

Every progress update creates a TaskProgress entry:
- Previous percentage
- New percentage
- Update timestamp
- Notes
- Occupancy status
- Who made the update

View in admin panel under "Recent Updates"

---

## 🎓 Best Practices

### For Admins

1. **Set realistic deadlines** - Consider task complexity
2. **Use priority levels** - URGENT for critical, LOW for nice-to-haves
3. **Provide clear descriptions** - Employees need to understand requirements
4. **Check progress regularly** - Monitor via dashboard, catch blockers early
5. **Review analytics** - Identify trends, optimize team workload

### For Employees

1. **Update progress regularly** - Don't wait until completion
2. **Add meaningful notes** - Help admin understand blockers
3. **Be honest with progress** - 50% means actually halfway done
4. **Complete one task at a time** - Focus on quality
5. **Communicate blockers** - Use notes field to flag issues

---

## 📞 Support

| Issue | Solution |
|-------|----------|
| Task not assigned | Check employee role is 'EMPLOYEE' |
| Progress not syncing | Verify API endpoint is running |
| Offline not working | Check cache directory exists |
| Wrong progress shown | Check browser cache (Ctrl+Shift+Delete) |

---

## 🎉 You're Ready!

Start assigning tasks and tracking progress in real-time!

**Questions?** Check the full documentation:
- `REALTIME_TASK_MANAGEMENT_IMPLEMENTATION.md` - Complete technical docs
- API endpoints - `/api/` prefix on all routes
- Admin panel - `/dashboard/tasks/` routes

Enjoy! 🚀
