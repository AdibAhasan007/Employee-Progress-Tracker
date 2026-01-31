# Multi-Tenant OWNER Portal - Quick Reference Guide

## 🚀 Quick Start for Deployment

### 1. Apply Migrations
```bash
cd backend
python manage.py migrate core 0007
```

### 2. Create Plans (One-Time Setup)
```python
from core.models import Plan

plans = [
    Plan.objects.create(
        name='FREE',
        max_employees=5,
        max_storage_gb=10,
        screenshot_retention_days=30,
        price_monthly=0
    ),
    Plan.objects.create(
        name='PRO',
        max_employees=50,
        max_storage_gb=100,
        screenshot_retention_days=90,
        price_monthly=99
    ),
    Plan.objects.create(
        name='ENTERPRISE',
        max_employees=999,
        max_storage_gb=1000,
        screenshot_retention_days=365,
        price_monthly=499
    ),
]
```

### 3. Create OWNER User
```python
from core.models import User

owner = User.objects.create_user(
    username='owner',
    email='owner@company.com',
    password='secure-password',
    role='OWNER'
)
# Note: OWNER user has NO company assigned
```

### 4. Create First Test Company
```python
from core.models import Company, Plan
from datetime import timedelta
from django.utils import timezone

plan = Plan.objects.get(name='TRIAL')
company = Company.objects.create(
    name='Acme Corp',
    email='admin@acme.com',
    contact_person='John Doe',
    contact_phone='+1234567890',
    plan=plan,
    status='TRIAL',
    trial_ends_at=timezone.now() + timedelta(days=30)
)

print(f"Company Key: {company.company_key}")
```

### 5. Create Admin for Company
```python
admin = User.objects.create_user(
    username='acme-admin',
    email='admin@acme.com',
    password='admin-password',
    role='ADMIN',
    company=company,
    is_active=True
)
```

### 6. Migrate Existing Data (If Applicable)
```python
from core.models import Company
from django.db.models import Q

# Get or create default company for existing data
default_company, created = Company.objects.get_or_create(
    name='Default Company',
    defaults={
        'plan': Plan.objects.get(name='FREE'),
        'status': 'ACTIVE'
    }
)

# Update existing records without company_id
User.objects.filter(company__isnull=True, role__in=['ADMIN', 'EMPLOYEE']).update(
    company=default_company
)
WorkSession.objects.filter(company__isnull=True).update(company=default_company)
ApplicationUsage.objects.filter(company__isnull=True).update(company=default_company)
WebsiteUsage.objects.filter(company__isnull=True).update(company=default_company)
ActivityLog.objects.filter(company__isnull=True).update(company=default_company)
Screenshot.objects.filter(company__isnull=True).update(company=default_company)
Task.objects.filter(company__isnull=True).update(company=default_company)
```

---

## 📱 Desktop App Integration

### Send Company Key in API Requests

```python
# tracker/loginController.py or similar
import requests

COMPANY_KEY = "company_abc123xyz..."  # Get from OWNER/Admin
API_BASE = "https://api.myapp.com/api"

headers = {
    'X-Company-Key': COMPANY_KEY,
    'Content-Type': 'application/json'
}

# Login
response = requests.post(
    f"{API_BASE}/login",
    json={
        'email': 'employee@company.com',
        'password': 'password'
    },
    headers=headers
)

if response.status_code == 401:
    print("Invalid company key or company suspended")
elif response.status_code == 403:
    print("Company subscription expired")
else:
    data = response.json()
    active_token = data['data']['active_token']
```

### Error Handling

```python
def handle_api_response(response):
    if response.status_code == 401:
        # Missing or invalid company key
        show_dialog("Error", "Invalid company key. Contact admin.")
    elif response.status_code == 403:
        # Company suspended or subscription expired
        show_dialog("Error", "Company subscription expired. Contact admin.")
    elif response.status_code == 200:
        return response.json()
    else:
        show_dialog("Error", f"Server error: {response.status_code}")
```

---

## 👑 OWNER Portal Routes & Actions

### Dashboard
- **URL**: `/owner/dashboard/`
- **Shows**: All companies, status, usage stats
- **Login Required**: Yes (OWNER role only)

### Company Detail
- **URL**: `/owner/company/<id>/`
- **Shows**: Detailed analytics, 90-day history
- **Actions**: Change plan, suspend, reactivate, rotate key

### Create Company
- **Method**: POST to `/owner/company/create/`
- **Body**: `name`, `email`, `contact_person`, `contact_phone`, `plan_id`
- **Returns**: company_id, company_key

### Change Plan
- **Method**: POST to `/owner/company/<id>/change-plan/`
- **Body**: `plan_id`
- **Effect**: Upgrades/downgrades seats & storage

### Suspend Company
- **Method**: POST to `/owner/company/<id>/suspend/`
- **Effect**: Blocks all API calls from company
- **Reverses With**: Reactivate button

### Reactivate Company
- **Method**: POST to `/owner/company/<id>/reactivate/`
- **Effect**: Allows API calls again, extends subscription

### Rotate Key
- **Method**: POST to `/owner/company/<id>/rotate-key/`
- **Effect**: Generates new company_key
- **Return**: Old key + new key (notify company of change)

### Analytics
- **URL**: `/owner/reports/`
- **Shows**: Top companies by usage, plan distribution, revenue insights

---

## 🔐 Permission Quick Reference

| Endpoint | OWNER | ADMIN | EMPLOYEE |
|----------|-------|-------|----------|
| `/owner/*` | ✅ | ❌ | ❌ |
| `/dashboard/admin/` | ❌ | ✅ (own company) | ❌ |
| `/employees/` | ❌ | ✅ (own company) | ❌ |
| `/sessions/` | ❌ | ✅ (own company) | ✅ (own) |
| `/screenshots/` | ❌ | ✅ (own company) | ✅ (own) |
| `/api/CompanyUsageDaily` | ✅ | ✅ (own company) | ❌ |
| `/api/WorkSession` | ❌ | ✅ (own company) | ✅ (own) |
| `/api/ApplicationUsage` | ❌ | ✅ (own company) | ✅ (own) |

---

## 🧪 Running Tests

```bash
# Run all multi-tenant tests
python manage.py test core.tests_multitenant -v 2

# Run specific test class
python manage.py test core.tests_multitenant.MultiTenantFoundationTests

# Run with coverage
coverage run --source='core' manage.py test core.tests_multitenant
coverage report
```

---

## 📊 Aggregation Job (To Implement)

This should run nightly via Celery or APScheduler:

```python
# core/tasks.py
from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Count
from .models import Company, CompanyUsageDaily, WorkSession, Screenshot

@shared_task
def aggregate_company_usage_daily():
    """Run nightly: Aggregate previous day's usage into CompanyUsageDaily."""
    yesterday = timezone.now().date() - timedelta(days=1)
    
    for company in Company.objects.all():
        sessions = WorkSession.objects.filter(
            company=company,
            start_time__date=yesterday
        )
        
        total_active = sessions.aggregate(
            total=Sum('active_seconds')
        )['total'] or 0
        
        total_idle = sessions.aggregate(
            total=Sum('idle_seconds')
        )['total'] or 0
        
        num_employees = sessions.values('employee').distinct().count()
        
        screenshots = Screenshot.objects.filter(
            company=company,
            capture_time__date=yesterday
        ).count()
        
        CompanyUsageDaily.objects.update_or_create(
            company=company,
            date=yesterday,
            defaults={
                'total_active_seconds': total_active,
                'total_idle_seconds': total_idle,
                'num_employees_active': num_employees,
                'num_sessions': sessions.count(),
                'num_screenshots': screenshots,
            }
        )
    
    print(f"✅ Aggregation complete for {yesterday}")
```

**Schedule** (Celery Beat):
```python
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'aggregate-daily-usage': {
        'task': 'core.tasks.aggregate_company_usage_daily',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight UTC
    },
}
```

---

## 🔄 Subscription Lifecycle

### TRIAL Status
- Duration: 30 days
- trial_ends_at: Set on creation
- Feature: All features included
- Upgrade: OWNER changes to PRO/ENTERPRISE

### ACTIVE Status
- Duration: Per-plan (monthly/yearly)
- subscription_expires_at: Set on purchase
- Feature: Full access
- Auto-Suspend: When expires_at passes (implement scheduled task)

### SUSPENDED Status
- Trigger: OWNER clicks suspend, or subscription expires
- Effect: Immediate - all API calls return 403
- Recovery: OWNER clicks reactivate

### EXPIRED Status (Subscription record)
- Trigger: subscription.expires_at passes
- Effect: Audit trail (why it expired)
- Action: Can create new Subscription when renewing

---

## 🚨 Troubleshooting

### "X-Company-Key header required" on Desktop App
**Fix**: Ensure desktop app sends header on ALL protected endpoints
```python
# Every API call needs this:
headers = {'X-Company-Key': company_key}
```

### "Company subscription is suspended"
**Fix**: OWNER must reactivate in `/owner/company/<id>/reactivate/`

### "Company subscription expired"
**Fix**: Trial/subscription date passed. Either:
- OWNER extends date: `company.trial_ends_at = future_date`
- Or create new Subscription record

### OWNER can see WorkSession data (BUG)
**Fix**: Verify `CompanyKeyValidationMiddleware` is NOT allowing access
- Check permissions.py - `CanViewAggregateDataOnly` should block
- Check views use proper permission_classes

---

## 📈 Monitoring

### Check Company Subscription Status
```python
from core.models import Company

company = Company.objects.get(id=1)
print(f"Status: {company.status}")
print(f"Is Active: {company.is_active_subscription()}")
print(f"Last Sync: {company.last_sync_at}")
```

### Check Usage Aggregates
```python
from core.models import CompanyUsageDaily
from datetime import timedelta
from django.utils import timezone

company = Company.objects.get(id=1)
thirty_days_ago = timezone.now().date() - timedelta(days=30)

usage = company.daily_usage.filter(date__gte=thirty_days_ago)
total_minutes = usage.aggregate(Sum('total_active_seconds'))['total__sum'] or 0

print(f"30-day active minutes: {total_minutes // 60}")
print(f"Employees active: {usage.aggregate(Sum('num_employees_active'))}")
```

---

**Ready to deploy!** 🚀
