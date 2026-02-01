# Owner Dashboard - Quick Reference

## 🚀 Access Owner Dashboard
```
URL: http://127.0.0.1:8000/api/owner/dashboard/
Username: ayman
Password: 12345
```

---

## 📊 What You'll See

### Dashboard KPIs
- **Total Companies**: Count of all companies
- **Active**: Companies with active subscriptions
- **Trial**: Companies in trial period
- **Suspended**: Blocked companies

### Company Cards
Each company shows:
- Company name & email
- Current plan (BASIC/PRO/ENTERPRISE)
- Employee seats used (e.g., 15/25)
- Last 30 days: Active minutes, Screenshots, Storage
- Last sync timestamp
- Action buttons

---

## ⚡ Quick Actions

### Create New Company
```
[+ Create Company] button
→ Fill: Name, Email, Contact, Phone, Plan
→ System creates TRIAL (30 days)
→ Auto-generates API Key
```

### Change Plan
```
[📦 Plan] button on company card
→ Select: BASIC / PRO / ENTERPRISE
→ Effective immediately
```

### Suspend Company
```
[🚫 Suspend] button
→ Blocks all access (web + desktop)
→ Changes status to SUSPENDED
```

### Reactivate Company
```
[✅ Reactivate] button (on suspended company)
→ Restores access
→ Extends subscription 30 days
```

### Rotate API Key
```
[🔑 Rotate Key] button
→ Generates new company_key
→ Invalidates old key
→ Company must update desktop config
```

---

## 📈 Analytics
```
[📊 Analytics] button
→ Top 10 companies by usage
→ Plan distribution chart
→ Subscription status summary
```

---

## 🔒 Data Privacy Rules

### Owner CAN See ✅
- Company name, email, contact info
- Subscription plan & status
- Seat count (used vs. limit)
- **Aggregate stats only:**
  - Total minutes tracked
  - Total screenshots count
  - Total storage usage
  - Number of active employees (count only)
- Last sync timestamp

### Owner CANNOT See ❌
- Employee names or emails
- Individual work sessions
- Screenshots (any)
- Websites visited
- Apps used
- Per-employee activity
- Tasks or personal data

---

## 🎯 Key Features

| Feature | Purpose |
|---------|---------|
| Dashboard | Overview of all companies & stats |
| Company Detail | Deep dive into one company's metrics |
| Create Company | Onboard new customer (trial) |
| Change Plan | Upgrade/downgrade subscription |
| Suspend | Block company access (non-payment, etc) |
| Reactivate | Restore access after suspension |
| Rotate Key | Security: invalidate old API key |
| Reports | Analytics on all companies |

---

## 💡 Pro Tips

1. **Monitor Last Sync** - If > 7 days, company might have issues
2. **Check Seat Limit** - Alert company if approaching max
3. **Subscription Dates** - Set reminder before expiry
4. **Rotate Keys Regularly** - Security best practice (monthly)
5. **Use Reports** - Identify top/inactive companies

---

## 🔑 Important Numbers

- **Trial Period**: 30 days
- **Seat Limits**: 
  - BASIC: 5 employees
  - PRO: 25 employees
  - ENTERPRISE: Unlimited
- **Screenshot Retention**: Plan-dependent
- **Sync Check Interval**: Every 10 seconds (desktop app)

---

## 📞 Support Contacts

If a company needs help:
- **Web Access**: Blocked? Check status (SUSPENDED?)
- **Desktop Sync**: Check API key validity & company status
- **Storage Full**: Upgrade plan or request storage cleanup
- **Seat Limit Hit**: Upgrade plan to PRO/ENTERPRISE

---

## ✅ Owner Dashboard Checklist

- [x] View all companies
- [x] Create trial companies
- [x] Monitor usage stats (aggregate only)
- [x] Manage subscription plans
- [x] Suspend companies
- [x] Reactivate companies
- [x] Rotate API keys
- [x] View analytics
- [x] NO access to employee data
- [x] Complete data privacy

