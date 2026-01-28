# Web Dashboard Requirements (Admin & User Panels)

## ✅ Admin Panel

### 1. Admin Dashboard (Overview)
*   **KPI Cards**:
    *   Total Employees (Active/Inactive)
    *   Today Total Time / Active Time / Idle Time
    *   Weekly & Monthly Summary
    *   Productivity % (Active ÷ Total)
*   **Recent Activity**:
    *   Latest screenshots (thumbnail + time + employee)
    *   Latest sessions started/stopped
*   **Daily Limits / Compliance**:
    *   Employee-wise Today/Week/Month time
    *   Threshold alert (e.g., high idle time, low work time)

### 2. Employee Management
*   **Add Employee**:
    *   Name, Email, Password (auto-create user login)
    *   Timezone (default Asia/Dhaka)
    *   Photo upload
    *   Status: Active/Inactive
*   **Employee List**:
    *   Search/Filter/Sort + pagination
    *   Actions: View / Edit / Deactivate
*   **Employee Limit Banner**:
    *   Example: limit 20, used 14, remaining 6
*   **Actions**:
    *   Reset Password / Re-issue Token (tracker token)

### 3. Work Sessions Management
*   **Session List (Global)**:
    *   Filter: employee + date range + status (running/stopped)
    *   Columns: Start/End/Total/Active/Idle
    *   Action: Details
*   **Session Details**:
    *   Timeline of activity
    *   App usage breakdown
    *   Website usage breakdown
    *   Screenshots for that session
    *   Manual Session Add/Edit (optional)

### 4. Screenshots Management
*   **Screenshot Gallery**:
    *   Filter: employee + date range
    *   Grid view + zoom
    *   Download (authorized only)
*   **Retention Setting**:
    *   Screenshot auto-delete after X days (30/60/90)

### 5. Activity & Usage Reports
*   **Daily Activity Report**:
    *   Date select → employee-wise total/active/idle
    *   Export: Print / Excel / PDF
*   **Monthly Employee Report**:
    *   Employee + Month + Year
    *   Worked days + totals
    *   Export: Print / Excel / PDF
*   **Top Apps Report**:
    *   Per employee / per date range
*   **Top Websites Report**:
    *   Per employee / per date range
*   **Idle/Inactive Report**:
    *   Excessive idle time detection

### 6. Task Management
*   **Assign Tasks**:
    *   Multiple task items
    *   Issue date / end date
    *   Success report / status (open/done)
*   **Task List**:
    *   Employee-wise tasks
    *   Edit/delete

### 7. Admin / System Settings
*   Company profile (name, address, map link)
*   Work hour policy (daily target hours)
*   Idle threshold (e.g., 5 minutes inactivity = idle)
*   Timezone default
*   Employee limit
*   Screenshot retention days

### 8. Security / Audit
*   Role-based access (Admin/Manager/User)
*   Audit log (who edited employee/session)
*   Block/disable users instantly
*   Token expiry / re-issue

---

## ✅ User Panel (Employee)

### 1. User Dashboard
*   **KPI Cards**:
    *   Today: Total/Active/Idle
    *   Weekly summary
    *   Monthly summary
    *   Productivity %
*   **My Screenshots**:
    *   Latest screenshots (thumbnail + time)
    *   “View all” (date range filter)
*   **My App Usage**:
    *   Top apps + time (today / date range)
*   **My Website Usage**:
    *   Top domains + time (today / date range)
*   **My Activity Log**:
    *   Active vs Idle breakdown

### 2. Work Sessions (My Sessions)
*   Date range filter + search
*   Table: start/end/total/active/idle
*   Session details: apps/websites/screenshot gallery

### 3. Reports (Self)
*   Daily report (my data only)
*   Monthly report (my data only)
*   Export options

### 4. Tasks
*   Assigned tasks list
*   Mark done / add success note
*   Due date highlight

### 5. Profile & Settings
*   Update name
*   Update timezone
*   Change password
*   Logout
