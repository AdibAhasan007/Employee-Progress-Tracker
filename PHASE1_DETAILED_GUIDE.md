# 📋 DETAILED IMPLEMENTATION CHECKLIST - Phase 1 Critical Items

**Status:** Production-Ready Roadmap  
**Estimated Time:** 3-4 days for Phase 1  

---

## PHASE 1: CRITICAL (Next 3 Days) 🔴

### [ ] ITEM 1: Desktop Agent Heartbeat Endpoint
**Why Critical:** Owner can't track who's online, no way to verify agent is working  
**Estimated Time:** 30 minutes  
**Priority:** 🔴 CRITICAL  

**Files to Modify:**
- `backend/core/views.py` - Add heartbeat view
- `backend/core/urls.py` - Add route
- `backend/models.py` - Add `last_agent_sync_at` field to User model

**Code Changes:**

In `models.py`, add to User model:
```python
last_agent_sync_at = models.DateTimeField(null=True, blank=True, help_text="Last desktop app heartbeat")
```

In `views.py`, add:
```python
from django.views.decorators.http import require_http_methods
from django.utils import timezone

@require_http_methods(["POST"])
@login_required
def agent_heartbeat(request):
    """Desktop agent reports it's alive"""
    request.user.last_agent_sync_at = timezone.now()
    request.user.save(update_fields=['last_agent_sync_at'])
    
    return JsonResponse({
        'status': 'ok',
        'server_time': timezone.now().isoformat(),
        'company_status': request.user.company.status,
    })
```

In `urls.py`, add:
```python
path('api/agent/heartbeat/', agent_heartbeat, name='api-agent-heartbeat'),
```

**Desktop Agent Changes:**
```python
# In tracker/main.py or equivalent
import requests
import threading
from datetime import timedelta

def send_heartbeat():
    """Send heartbeat every 5 minutes"""
    while True:
        try:
            response = requests.post(
                'http://backend:8000/api/agent/heartbeat/',
                headers={'X-Company-Key': company_key}
            )
            if response.status_code == 200:
                print("Heartbeat sent")
        except Exception as e:
            print(f"Heartbeat failed: {e}")
        
        time.sleep(300)  # 5 minutes

# Start in background thread
heartbeat_thread = threading.Thread(target=send_heartbeat, daemon=True)
heartbeat_thread.start()
```

**Validation Checklist:**
- [ ] User model has `last_agent_sync_at` field
- [ ] Agent calls `/api/agent/heartbeat/` every 5 minutes
- [ ] Owner dashboard shows "Last Sync" time for each company
- [ ] Alert triggers if > 24 hours without heartbeat
- [ ] Database shows updated timestamps

---

### [ ] ITEM 2: Desktop Agent Policy Fetch Endpoint  
**Why Critical:** Agent behavior hardcoded, needs server-driven configuration  
**Estimated Time:** 1 hour  
**Priority:** 🔴 CRITICAL

**Files to Modify:**
- `backend/core/models.py` - Add CompanyPolicy model
- `backend/core/views.py` - Add policy fetch view
- `backend/core/urls.py` - Add route
- Update admin interface (if using Django admin)

**Step 1: Create CompanyPolicy Model**

In `models.py`, add:
```python
class CompanyPolicy(models.Model):
    """Policy settings that control desktop agent behavior"""
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='policy')
    
    # Feature toggles
    screenshots_enabled = models.BooleanField(default=True, help_text="Allow screenshot capture")
    website_tracking_enabled = models.BooleanField(default=True, help_text="Track visited websites")
    app_tracking_enabled = models.BooleanField(default=True, help_text="Track used applications")
    
    # Intervals (in seconds)
    screenshot_interval_seconds = models.IntegerField(
        default=600,  # 10 minutes
        help_text="Time between screenshots"
    )
    idle_threshold_seconds = models.IntegerField(
        default=300,  # 5 minutes
        help_text="Time inactive before counting as idle"
    )
    
    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Company Policy"
        verbose_name_plural = "Company Policies"
    
    def __str__(self):
        return f"Policy for {self.company.name}"
```

**Step 2: Create Signal to Auto-Create Policy**

In `models.py`, add at end:
```python
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Company)
def create_company_policy(sender, instance, created, **kwargs):
    """Auto-create policy when company is created"""
    if created:
        CompanyPolicy.objects.create(company=instance)

post_save.connect(create_company_policy, sender=Company)
```

**Step 3: Add Policy Fetch View**

In `views.py`, add:
```python
@require_http_methods(["GET"])
@login_required
def get_company_policy(request):
    """Desktop agent fetches policy to configure tracking behavior"""
    try:
        policy = request.user.company.policy
    except CompanyPolicy.DoesNotExist:
        # Fallback to defaults
        policy = CompanyPolicy.objects.create(company=request.user.company)
    
    return JsonResponse({
        'success': True,
        'policy': {
            'screenshots': {
                'enabled': policy.screenshots_enabled,
                'interval_seconds': policy.screenshot_interval_seconds,
            },
            'website_tracking': {
                'enabled': policy.website_tracking_enabled,
            },
            'app_tracking': {
                'enabled': policy.app_tracking_enabled,
            },
            'idle_threshold_seconds': policy.idle_threshold_seconds,
            'company_status': request.user.company.status,
            'is_active_subscription': request.user.company.is_active_subscription(),
        },
        'policy_updated_at': policy.updated_at.isoformat(),
    })
```

**Step 4: Add Route**

In `urls.py`, add:
```python
path('api/policy/', get_company_policy, name='api-get-policy'),
```

**Step 5: Desktop Agent Implementation**

```python
import requests
import json
from datetime import datetime, timedelta

class PolicyManager:
    def __init__(self, company_key, server_url='http://backend:8000'):
        self.company_key = company_key
        self.server_url = server_url
        self.policy = None
        self.last_fetch = None
    
    def fetch_policy(self):
        """Fetch policy from server, cache for 1 hour"""
        # Check if we need to refresh (fetch at startup + every 1 hour)
        if self.last_fetch and datetime.now() - self.last_fetch < timedelta(hours=1):
            return self.policy
        
        try:
            response = requests.get(
                f'{self.server_url}/api/policy/',
                headers={'X-Company-Key': self.company_key},
                timeout=5
            )
            
            if response.status_code == 200:
                self.policy = response.json()['policy']
                self.last_fetch = datetime.now()
                print(f"Policy fetched: {self.policy}")
                return self.policy
            else:
                print(f"Failed to fetch policy: {response.status_code}")
                return None
        except Exception as e:
            print(f"Policy fetch error: {e}")
            return None
    
    def is_tracking_enabled(self):
        """Check if tracking is enabled"""
        if not self.policy:
            return True  # Default to enabled
        return self.policy.get('is_active_subscription', True)
    
    def get_screenshot_interval(self):
        """Get interval between screenshots in seconds"""
        if not self.policy:
            return 600  # Default 10 minutes
        return self.policy['screenshots']['interval_seconds']

# Usage in main app
policy_mgr = PolicyManager(company_key='company_XXX')

# At startup
policy_mgr.fetch_policy()

# In tracking loop
if policy_mgr.is_tracking_enabled():
    if policy_mgr.policy['screenshots']['enabled']:
        take_screenshot()
    
    interval = policy_mgr.get_screenshot_interval()
    time.sleep(interval)

# Every hour
if should_refresh_policy():
    policy_mgr.fetch_policy()
```

**Validation Checklist:**
- [ ] CompanyPolicy model created and migrated
- [ ] Signal auto-creates policy for new companies
- [ ] Admin can view/edit policy in Django admin
- [ ] `/api/policy/` endpoint returns correct format
- [ ] Agent fetches policy on startup
- [ ] Agent re-fetches every 60 minutes
- [ ] Agent respects `screenshots_enabled`, `interval_seconds`
- [ ] Company status is included in response
- [ ] Agent stops tracking when company is SUSPENDED

---

### [ ] ITEM 3: Audit Log Model Implementation
**Why Critical:** No accountability trail, required for SaaS/compliance  
**Estimated Time:** 2 hours  
**Priority:** 🔴 CRITICAL

**Files to Modify:**
- `backend/core/models.py` - Add AuditLog model
- `backend/core/owner_views.py` - Add logging calls
- `backend/core/web_views.py` - Add logging to admin actions
- `backend/templates/owner_audit_log.html` - Update to fetch from DB

**Step 1: Create AuditLog Model**

In `models.py`, add:
```python
class AuditLog(models.Model):
    """Complete audit trail for compliance and accountability"""
    ACTION_TYPES = (
        ('COMPANY_CREATED', 'Company Created'),
        ('COMPANY_SUSPENDED', 'Company Suspended'),
        ('COMPANY_REACTIVATED', 'Company Reactivated'),
        ('PLAN_CHANGED', 'Plan Changed'),
        ('POLICY_CHANGED', 'Policy Changed'),
        ('EMPLOYEE_ADDED', 'Employee Added'),
        ('EMPLOYEE_REMOVED', 'Employee Removed'),
        ('EMPLOYEE_DEACTIVATED', 'Employee Deactivated'),
        ('KEY_ROTATED', 'API Key Rotated'),
        ('REPORT_EXPORTED', 'Report Exported'),
        ('SETTINGS_CHANGED', 'Settings Changed'),
        ('PASSWORD_RESET', 'Password Reset'),
    )
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='audit_logs', db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Who performed action
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES, db_index=True)
    description = models.TextField()  # Human-readable description
    details = models.JSONField(default=dict, blank=True)  # { 'old_value': X, 'new_value': Y, ... }
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['company', '-timestamp']),
            models.Index(fields=['action_type', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.get_action_type_display()} by {self.user} at {self.timestamp}"
```

**Step 2: Create Audit Helper Function**

In `models.py`, add after AuditLog class:
```python
def create_audit_log(action_type, company, description, user=None, details=None, ip_address=None):
    """Helper to create audit logs"""
    AuditLog.objects.create(
        action_type=action_type,
        company=company,
        user=user,
        description=description,
        details=details or {},
        ip_address=ip_address,
    )
```

Or in a new file `backend/core/audit.py`:
```python
from .models import AuditLog
from django.utils import timezone

def get_client_ip(request):
    """Extract client IP from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_audit(request, action_type, company, description, details=None):
    """Log an action to audit trail"""
    AuditLog.objects.create(
        action_type=action_type,
        company=company,
        user=request.user,
        description=description,
        details=details or {},
        ip_address=get_client_ip(request),
    )
```

**Step 3: Add Logging to Owner Views**

In `owner_views.py`, add imports:
```python
from .audit import log_audit, get_client_ip
```

Update `suspend_company()`:
```python
def suspend_company(request, company_id):
    # ... existing code ...
    company.status = 'SUSPENDED'
    company.save()
    
    log_audit(
        request,
        'COMPANY_SUSPENDED',
        company,
        f"Company {company.name} suspended by {request.user.get_full_name()}",
        {'reason': 'Admin action'}
    )
    
    messages.success(request, f'{company.name} suspended.')
    return redirect('owner-dashboard')
```

Update `reactivate_company()`:
```python
def reactivate_company(request, company_id):
    # ... existing code ...
    company.status = 'ACTIVE'
    company.save()
    
    log_audit(
        request,
        'COMPANY_REACTIVATED',
        company,
        f"Company {company.name} reactivated by {request.user.get_full_name()}",
    )
    
    messages.success(request, f'{company.name} reactivated.')
    return redirect('owner-dashboard')
```

Update `change_plan()`:
```python
def change_plan(request, company_id):
    # ... existing code ...
    old_plan = company.plan.name
    company.plan = new_plan
    company.save()
    
    log_audit(
        request,
        'PLAN_CHANGED',
        company,
        f"Plan changed from {old_plan} to {new_plan.name}",
        {'old_plan': old_plan, 'new_plan': new_plan.name}
    )
    
    messages.success(request, f'Plan changed to {new_plan.name}.')
    return redirect('owner-dashboard')
```

Update `rotate_company_key()`:
```python
def rotate_company_key(request, company_id):
    # ... existing code ...
    old_key = company.company_key
    # Generate new key
    company.company_key = f"company_{secrets.token_hex(16)}"
    company.save()
    
    log_audit(
        request,
        'KEY_ROTATED',
        company,
        f"API key rotated for {company.name}",
        {'old_key': old_key[:8]+'***', 'new_key': company.company_key[:8]+'***'}
    )
    
    messages.success(request, 'API key rotated successfully.')
    return redirect('owner-dashboard')
```

**Step 4: Add Admin Action Logging**

In `web_views.py`, add logging to employee management:
```python
# When deactivating employee
def employee_toggle_status_view(request, emp_id):
    # ... existing code ...
    employee.is_active_employee = not employee.is_active_employee
    employee.save()
    
    log_audit(
        request,
        'EMPLOYEE_DEACTIVATED' if not employee.is_active_employee else 'EMPLOYEE_REACTIVATED',
        request.user.company,
        f"Employee {employee.get_full_name()} status changed",
        {'is_active': employee.is_active_employee}
    )
    
    return redirect('employee-list')
```

**Step 5: Create Owner Audit Log View**

In `owner_views.py`, add:
```python
@login_required
def owner_audit_log_view(request):
    """View audit log for owner"""
    if request.user.role != 'OWNER':
        return redirect('dashboard')
    
    # Get all audit logs for all companies
    logs = AuditLog.objects.select_related('company', 'user').order_by('-timestamp')
    
    # Filter by action type if provided
    action_filter = request.GET.get('action_type')
    if action_filter:
        logs = logs.filter(action_type=action_filter)
    
    # Filter by company if provided
    company_filter = request.GET.get('company_id')
    if company_filter:
        logs = logs.filter(company_id=company_filter)
    
    # Filter by date range
    from_date = request.GET.get('from_date')
    if from_date:
        logs = logs.filter(timestamp__gte=from_date)
    
    to_date = request.GET.get('to_date')
    if to_date:
        logs = logs.filter(timestamp__lte=to_date)
    
    context = {
        'logs': logs[:500],  # Last 500
        'action_types': dict(AuditLog.ACTION_TYPES),
        'all_companies': Company.objects.all(),
    }
    
    return render(request, 'owner_audit_log.html', context)
```

In `urls.py`, add:
```python
path('owner/audit-log/', owner_audit_log_view, name='owner-audit-log'),
```

**Step 6: Update Audit Log Template**

In `owner_audit_log.html`, update to show actual data:
```html
{% extends 'base.html' %}
{% load humanize %}

{% block title %}Audit Log - Owner Panel{% endblock %}

{% block content %}
<div class="container-fluid mt-5">
    <h2>System Audit Log</h2>
    <p class="text-muted">All administrative actions across all companies</p>
    
    <!-- Filters -->
    <form method="GET" class="row g-3 mb-4">
        <div class="col-md-3">
            <select name="action_type" class="form-select">
                <option value="">All Actions</option>
                {% for key, label in action_types.items %}
                    <option value="{{ key }}" {% if request.GET.action_type == key %}selected{% endif %}>
                        {{ label }}
                    </option>
                {% endfor %}
            </select>
        </div>
        
        <div class="col-md-3">
            <select name="company_id" class="form-select">
                <option value="">All Companies</option>
                {% for company in all_companies %}
                    <option value="{{ company.id }}" {% if request.GET.company_id == company.id|stringformat:"s" %}selected{% endif %}>
                        {{ company.name }}
                    </option>
                {% endfor %}
            </select>
        </div>
        
        <div class="col-md-2">
            <input type="date" name="from_date" class="form-control" value="{{ request.GET.from_date }}">
        </div>
        
        <div class="col-md-2">
            <input type="date" name="to_date" class="form-control" value="{{ request.GET.to_date }}">
        </div>
        
        <div class="col-md-2">
            <button type="submit" class="btn btn-primary">Filter</button>
            <a href="{% url 'owner-audit-log' %}" class="btn btn-secondary">Reset</a>
        </div>
    </form>
    
    <!-- Table -->
    <div class="table-responsive">
        <table class="table table-striped table-hover">
            <thead class="table-dark">
                <tr>
                    <th>Timestamp</th>
                    <th>Company</th>
                    <th>User</th>
                    <th>Action</th>
                    <th>Description</th>
                    <th>IP Address</th>
                </tr>
            </thead>
            <tbody>
                {% for log in logs %}
                <tr>
                    <td>{{ log.timestamp|naturaltime }}</td>
                    <td><strong>{{ log.company.name }}</strong></td>
                    <td>{{ log.user.get_full_name|default:"System" }}</td>
                    <td>
                        <span class="badge bg-info">{{ log.get_action_type_display }}</span>
                    </td>
                    <td>{{ log.description }}</td>
                    <td><code>{{ log.ip_address }}</code></td>
                </tr>
                {% empty %}
                <tr>
                    <td colspan="6" class="text-center text-muted">No audit logs found</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
```

**Validation Checklist:**
- [ ] AuditLog model migrated successfully
- [ ] Audit logs created for all owner actions
- [ ] Audit logs created for admin actions (employee deactivate, etc.)
- [ ] Can view all logs in `/owner/audit-log/`
- [ ] Can filter by action type, company, date range
- [ ] Cannot delete/edit audit logs (immutable)
- [ ] IP address captured correctly

---

## QUICK START: Run Phase 1 Now

```bash
# 1. Add models
# Edit backend/core/models.py - add CompanyPolicy, AuditLog

# 2. Create migrations
cd backend
python manage.py makemigrations core

# 3. Apply migrations
python manage.py migrate core

# 4. Update views
# Edit backend/core/views.py - add agent_heartbeat, get_company_policy
# Edit backend/core/owner_views.py - add logging to all methods
# Edit backend/core/web_views.py - add logging to admin actions

# 5. Update URLs
# Edit backend/core/urls.py - add new routes

# 6. Update template
# Edit backend/templates/owner_audit_log.html - fetch from DB

# 7. Test
python manage.py test  # If tests exist

# 8. Run server
python manage.py runserver

# 9. Test endpoints
curl -X GET http://localhost:8000/api/policy/ \
  -H "X-Company-Key: company_XXX"

curl -X POST http://localhost:8000/api/agent/heartbeat/ \
  -H "X-Company-Key: company_XXX"
```

**Estimated Total Time:** 4 hours (30min + 1hour + 2hours + testing)

When complete, move to PHASE 2 items (no-sync alert, employee My Day, background jobs).

