# 🚀 Phase 1 Features - Quick Reference Guide

## For OWNER Users

### 1. View Audit Logs
```python
# In Django admin or custom view
from core.models import AuditLog

# Get all audit logs for a company
logs = AuditLog.objects.filter(company=my_company).order_by('-timestamp')

# Filter by action type
company_created_logs = AuditLog.objects.filter(
    company=my_company,
    action_type='COMPANY_CREATED'
)

# Search by user
admin_actions = AuditLog.objects.filter(
    company=my_company,
    user=admin_user
)
```

### 2. Check Agent Connectivity
```python
from core.models import User
from django.utils import timezone
from datetime import timedelta

# Find agents that haven't synced in 15+ minutes
offline_threshold = timezone.now() - timedelta(minutes=15)
offline_agents = User.objects.filter(
    company=my_company,
    role='EMPLOYEE',
    last_agent_sync_at__lt=offline_threshold
)

# Or agents that have never synced
never_synced = User.objects.filter(
    company=my_company,
    role='EMPLOYEE',
    last_agent_sync_at__isnull=True
)
```

### 3. Configure Company Policy
```python
from core.models import CompanyPolicy

# Get policy (auto-created when company is created)
policy = CompanyPolicy.objects.get(company=my_company)

# Disable screenshots
policy.screenshots_enabled = False
policy.save()

# Change screenshot interval to 5 minutes
policy.screenshot_interval_seconds = 300
policy.save()

# Disable website tracking
policy.website_tracking_enabled = False
policy.save()
```

---

## For Desktop Agent Developers

### 1. Agent Heartbeat (every 5 minutes)
```python
import requests

def send_heartbeat(company_key, auth_token):
    """Send heartbeat to server every 5 minutes"""
    url = "http://your-server.com/api/agent/heartbeat/"
    headers = {
        "X-Company-Key": company_key,
        "Authorization": f"Token {auth_token}"
    }
    
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        
        # Check company status
        if data['company_status'] == 'SUSPENDED':
            print("⚠️ Company suspended - stopping tracking")
            stop_tracking()
        elif data['company_status'] == 'ACTIVE':
            print("✅ Company active - continue tracking")
            
        return data
    else:
        print(f"❌ Heartbeat failed: {response.status_code}")
        return None

# Call every 5 minutes
import time
while True:
    send_heartbeat(COMPANY_KEY, AUTH_TOKEN)
    time.sleep(300)  # 5 minutes
```

### 2. Fetch Company Policy (on startup + every hour)
```python
import requests

def fetch_company_policy(company_key, auth_token):
    """Fetch tracking policy from server"""
    url = "http://your-server.com/api/policy/"
    headers = {
        "X-Company-Key": company_key,
        "Authorization": f"Token {auth_token}"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        policy = response.json()
        
        # Apply policy
        SCREENSHOT_ENABLED = policy['screenshots_enabled']
        WEBSITE_TRACKING_ENABLED = policy['website_tracking_enabled']
        APP_TRACKING_ENABLED = policy['app_tracking_enabled']
        SCREENSHOT_INTERVAL = policy['screenshot_interval_seconds']
        IDLE_THRESHOLD = policy['idle_threshold_seconds']
        
        print(f"📋 Policy loaded:")
        print(f"  Screenshots: {'✅' if SCREENSHOT_ENABLED else '❌'}")
        print(f"  Website tracking: {'✅' if WEBSITE_TRACKING_ENABLED else '❌'}")
        print(f"  App tracking: {'✅' if APP_TRACKING_ENABLED else '❌'}")
        print(f"  Screenshot interval: {SCREENSHOT_INTERVAL}s")
        print(f"  Idle threshold: {IDLE_THRESHOLD}s")
        
        return policy
    else:
        print(f"❌ Policy fetch failed: {response.status_code}")
        return None

# Fetch on startup
policy = fetch_company_policy(COMPANY_KEY, AUTH_TOKEN)

# Refresh every hour
import time
while True:
    time.sleep(3600)  # 1 hour
    policy = fetch_company_policy(COMPANY_KEY, AUTH_TOKEN)
```

### 3. Example Agent Main Loop
```python
import requests
import time
from datetime import datetime, timedelta

class EmployeeTracker:
    def __init__(self, company_key, auth_token):
        self.company_key = company_key
        self.auth_token = auth_token
        self.base_url = "http://your-server.com"
        self.headers = {
            "X-Company-Key": company_key,
            "Authorization": f"Token {auth_token}"
        }
        
        # Load initial policy
        self.policy = self.fetch_policy()
        self.last_heartbeat = datetime.now()
        self.last_policy_fetch = datetime.now()
        
    def fetch_policy(self):
        """Fetch company tracking policy"""
        response = requests.get(f"{self.base_url}/api/policy/", headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return None
        
    def send_heartbeat(self):
        """Send heartbeat to server"""
        response = requests.post(f"{self.base_url}/api/agent/heartbeat/", headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            if data['company_status'] == 'SUSPENDED':
                return False  # Stop tracking
        return True
        
    def run(self):
        """Main tracking loop"""
        while True:
            # Send heartbeat every 5 minutes
            if datetime.now() - self.last_heartbeat > timedelta(minutes=5):
                if not self.send_heartbeat():
                    print("🛑 Company suspended - stopping")
                    break
                self.last_heartbeat = datetime.now()
            
            # Refresh policy every hour
            if datetime.now() - self.last_policy_fetch > timedelta(hours=1):
                self.policy = self.fetch_policy()
                self.last_policy_fetch = datetime.now()
            
            # Perform tracking based on policy
            if self.policy['screenshots_enabled']:
                self.capture_screenshot()
            
            if self.policy['app_tracking_enabled']:
                self.track_applications()
            
            if self.policy['website_tracking_enabled']:
                self.track_websites()
            
            # Sleep based on screenshot interval
            time.sleep(self.policy['screenshot_interval_seconds'])
    
    def capture_screenshot(self):
        # Your screenshot logic here
        pass
    
    def track_applications(self):
        # Your app tracking logic here
        pass
    
    def track_websites(self):
        # Your website tracking logic here
        pass

# Usage
tracker = EmployeeTracker(
    company_key="your_company_key_here",
    auth_token="your_auth_token_here"
)
tracker.run()
```

---

## For Admins

### 1. Activate/Deactivate Employees (Web UI)
When you toggle an employee's status in the web dashboard (`/employee/<id>/toggle-status/`), the action is automatically logged:

**Logged Data**:
- Action type: `EMPLOYEE_DEACTIVATED` or `EMPLOYEE_REACTIVATED`
- Who: Admin username
- When: Timestamp
- IP: Admin's IP address
- Details: `{'employee_id': 123, 'old_status': True, 'new_status': False}`

**View Logs**:
```python
# In Django shell or custom view
from core.models import AuditLog

# Get employee status change logs
logs = AuditLog.objects.filter(
    company=my_company,
    action_type__in=['EMPLOYEE_DEACTIVATED', 'EMPLOYEE_REACTIVATED']
)

for log in logs:
    print(f"{log.timestamp}: {log.description} by {log.user.username}")
```

### 2. Check Policy Settings (Web UI)
```python
from core.models import CompanyPolicy

policy = CompanyPolicy.objects.get(company=request.user.company)

context = {
    'screenshots_enabled': policy.screenshots_enabled,
    'website_tracking_enabled': policy.website_tracking_enabled,
    'app_tracking_enabled': policy.app_tracking_enabled,
    'screenshot_interval': policy.screenshot_interval_seconds,
    'idle_threshold': policy.idle_threshold_seconds,
}
```

---

## Audit Log Action Types

| Action Type | Description | When It's Logged |
|-------------|-------------|------------------|
| `COMPANY_CREATED` | New company created | Owner creates company |
| `COMPANY_SUSPENDED` | Company suspended | Owner suspends company |
| `COMPANY_REACTIVATED` | Company reactivated | Owner reactivates company |
| `PLAN_CHANGED` | Subscription plan changed | Owner changes plan |
| `POLICY_CHANGED` | Tracking policy changed | Admin changes policy |
| `EMPLOYEE_ADDED` | New employee added | Admin adds employee |
| `EMPLOYEE_REMOVED` | Employee removed | Admin deletes employee |
| `EMPLOYEE_DEACTIVATED` | Employee deactivated | Admin deactivates employee |
| `EMPLOYEE_REACTIVATED` | Employee reactivated | Admin reactivates employee |
| `KEY_ROTATED` | Company API key rotated | Owner rotates key |
| `REPORT_EXPORTED` | Report exported | Admin exports report |
| `SETTINGS_CHANGED` | Company settings changed | Admin changes settings |
| `PASSWORD_RESET` | Password reset | User resets password |

---

## Database Queries

### Most Common Queries

```python
from core.models import AuditLog, CompanyPolicy, User
from django.utils import timezone
from datetime import timedelta

# 1. Get today's audit logs
today = timezone.now().date()
today_logs = AuditLog.objects.filter(
    company=my_company,
    timestamp__date=today
)

# 2. Get all policy changes
policy_changes = AuditLog.objects.filter(
    company=my_company,
    action_type='POLICY_CHANGED'
).order_by('-timestamp')

# 3. Find agents offline for 15+ minutes
offline_threshold = timezone.now() - timedelta(minutes=15)
offline = User.objects.filter(
    company=my_company,
    role='EMPLOYEE',
    last_agent_sync_at__lt=offline_threshold
)

# 4. Get user's recent activity
user_activity = AuditLog.objects.filter(
    company=my_company,
    user=some_user
).order_by('-timestamp')[:20]

# 5. Count actions by type
from django.db.models import Count
action_stats = AuditLog.objects.filter(
    company=my_company
).values('action_type').annotate(
    count=Count('id')
).order_by('-count')
```

---

## API Response Examples

### Heartbeat Response
```json
{
    "status": "success",
    "message": "Heartbeat recorded",
    "last_sync_at": "2026-02-01T18:36:09.005347Z",
    "company_status": "ACTIVE"
}
```

### Policy Response
```json
{
    "screenshots_enabled": true,
    "website_tracking_enabled": true,
    "app_tracking_enabled": true,
    "screenshot_interval_seconds": 600,
    "idle_threshold_seconds": 300
}
```

---

## Migration & Deployment

### Fresh Deployment
```bash
cd backend

# Run migrations
python manage.py migrate

# Create superuser (OWNER)
python manage.py createsuperuser
# Username: ayman
# Email: ayman@example.com
# Role: OWNER

# Test Phase 1
python test_phase1.py
```

### Existing Deployment (with old data)
```bash
cd backend

# Clean old data
python clean_db_direct.py

# Reset migrations
python manage.py migrate core zero

# Delete old migration files
cd core/migrations
rm *.py
# Keep __init__.py

# Create fresh migrations
cd ../..
python manage.py makemigrations core
python manage.py migrate

# Test
python test_phase1.py
```

---

## Troubleshooting

### Issue: Heartbeat returns 403 Forbidden
**Cause**: Missing or invalid `X-Company-Key` header  
**Fix**: Check that `X-Company-Key` matches company's `company_key` field

### Issue: Policy returns empty response
**Cause**: CompanyPolicy doesn't exist  
**Fix**: Signal should auto-create. If not, manually create:
```python
from core.models import CompanyPolicy
CompanyPolicy.objects.create(company=my_company)
```

### Issue: Audit logs not appearing
**Cause**: `log_audit()` not called or error occurred  
**Fix**: Check that view imports `from .audit import log_audit` and calls it after action

### Issue: last_agent_sync_at not updating
**Cause**: Heartbeat endpoint not being called or failing  
**Fix**: Check agent code and server logs. Verify endpoint URL is correct

---

## Next Steps

After Phase 1, you can:

1. **Add Policy UI** - Let admins change tracking settings via web dashboard
2. **Add Audit Log Viewer** - Show audit logs in web dashboard with filtering
3. **Add No-Sync Alerts** - Dashboard indicator for offline agents
4. **Add Stripe Billing** - Integrate subscription payments
5. **Add Advanced Charts** - Productivity metrics visualizations

But **you can launch now** with Phase 1 features! 🚀
