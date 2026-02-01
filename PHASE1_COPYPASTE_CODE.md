# 🔧 COPY-PASTE READY: Phase 1 Code Changes

This file contains EXACT code you can copy-paste to implement Phase 1.

---

## FILE 1: backend/core/models.py

### Add These Classes (after Company class, before/after Subscription)

```python
# ==========================================
# 3. AGENT POLICY & AUDIT
# ==========================================

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
        ('EMPLOYEE_REACTIVATED', 'Employee Reactivated'),
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

### Modify User Model

Find the User class and add this field:
```python
class User(AbstractUser):
    # ... existing fields ...
    last_agent_sync_at = models.DateTimeField(null=True, blank=True, help_text="Last desktop app heartbeat")
```

### Add Signal to Auto-Create Policy

Add at the END of models.py file:
```python
# Auto-create CompanyPolicy when Company is created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Company)
def create_company_policy(sender, instance, created, **kwargs):
    """Auto-create policy when company is created"""
    if created:
        CompanyPolicy.objects.create(company=instance)

post_save.connect(create_company_policy, sender=Company)
```

---

## FILE 2: backend/core/views.py

### Add These Imports at Top

```python
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
```

### Add These Views (at end of file)

```python
# ==========================================
# AGENT HEARTBEAT & POLICY
# ==========================================

@require_http_methods(["POST"])
@login_required
def agent_heartbeat(request):
    """
    Desktop agent reports it's alive.
    Call every 5 minutes to track online status.
    """
    try:
        request.user.last_agent_sync_at = timezone.now()
        request.user.save(update_fields=['last_agent_sync_at'])
        
        return JsonResponse({
            'status': 'ok',
            'server_time': timezone.now().isoformat(),
            'company_status': request.user.company.status,
            'message': 'Heartbeat received'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@require_http_methods(["GET"])
@login_required
def get_company_policy(request):
    """
    Desktop agent fetches policy to configure tracking behavior.
    Call on startup and every 60 minutes.
    """
    try:
        # Get or create policy
        policy, _ = request.user.company.policy, None
        try:
            policy = request.user.company.policy
        except:
            from .models import CompanyPolicy
            policy = CompanyPolicy.objects.create(company=request.user.company)
        
        return JsonResponse({
            'success': True,
            'policy': {
                'company_key': request.user.company.company_key,
                'company_status': request.user.company.status,
                'is_active_subscription': request.user.company.is_active_subscription(),
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
            },
            'policy_updated_at': policy.updated_at.isoformat(),
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)
```

---

## FILE 3: backend/core/urls.py

### Add These Imports

If not already present, add:
```python
from .views import (
    LoginView, LoginCheckView, 
    StartSessionView, StopSessionView, CheckSessionActiveView,
    UploadActivityView, UploadScreenshotView,
    GetTasksView, UpdateTaskStatusView,
    agent_heartbeat, get_company_policy  # ADD THIS LINE
)
```

### Add These URL Patterns

Find the `# API Endpoints (Desktop App)` section and add:
```python
    path('api/agent/heartbeat/', agent_heartbeat, name='api-agent-heartbeat'),
    path('api/policy/', get_company_policy, name='api-get-policy'),
```

Example:
```python
urlpatterns = [
    # ===========================
    # API Endpoints (Desktop App)
    # ===========================
    path('login', LoginView.as_view(), name='api-login'),
    path('login-check', LoginCheckView.as_view(), name='api-login-check'),
    path('work-session/create', StartSessionView.as_view(), name='api-session-create'),
    path('work-session/stop', StopSessionView.as_view(), name='api-session-stop'),
    path('check-session-active', CheckSessionActiveView.as_view(), name='api-check-session-active'),
    path('upload/employee-activity', UploadActivityView.as_view(), name='api-upload-activity'),
    path('screenshot/upload', UploadScreenshotView.as_view(), name='api-upload-screenshot'),
    path('tasks/get', GetTasksView.as_view(), name='api-tasks-get'),
    path('tasks/update', UpdateTaskStatusView.as_view(), name='api-tasks-update'),
    path('api/session/<int:session_id>/active_time/', session_active_time_api, name='api-session-active-time'),
    
    # NEW LINES
    path('api/agent/heartbeat/', agent_heartbeat, name='api-agent-heartbeat'),
    path('api/policy/', get_company_policy, name='api-get-policy'),
    
    # ... rest of URLs ...
]
```

---

## FILE 4: backend/core/audit.py (NEW FILE)

Create new file: `backend/core/audit.py`

```python
"""
Audit logging utilities for tracking administrative actions.
"""

from django.utils import timezone
from .models import AuditLog


def get_client_ip(request):
    """Extract client IP from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_audit(request, action_type, company, description, details=None):
    """
    Log an administrative action to audit trail.
    
    Args:
        request: Django request object
        action_type: One of AuditLog.ACTION_TYPES
        company: Company object
        description: Human-readable description
        details: Optional dict with old/new values, reasons, etc.
    """
    AuditLog.objects.create(
        action_type=action_type,
        company=company,
        user=request.user,
        description=description,
        details=details or {},
        ip_address=get_client_ip(request),
        timestamp=timezone.now(),
    )
```

---

## FILE 5: backend/core/owner_views.py

### Add This Import at Top

```python
from .audit import log_audit
```

### Update suspend_company()

Find the function and replace it with:
```python
@login_required
def suspend_company(request, company_id):
    """Suspend a company (stops tracking)"""
    if request.user.role != 'OWNER':
        return redirect('dashboard')
    
    try:
        company = Company.objects.get(id=company_id)
    except Company.DoesNotExist:
        messages.error(request, 'Company not found.')
        return redirect('owner-dashboard')
    
    company.status = 'SUSPENDED'
    company.save()
    
    # Log the action
    log_audit(
        request,
        'COMPANY_SUSPENDED',
        company,
        f"Company {company.name} suspended by {request.user.get_full_name()}",
        {'reason': 'Admin action', 'timestamp': timezone.now().isoformat()}
    )
    
    messages.success(request, f'{company.name} has been suspended.')
    return redirect('owner-dashboard')
```

### Update reactivate_company()

```python
@login_required
def reactivate_company(request, company_id):
    """Reactivate a suspended company"""
    if request.user.role != 'OWNER':
        return redirect('dashboard')
    
    try:
        company = Company.objects.get(id=company_id)
    except Company.DoesNotExist:
        messages.error(request, 'Company not found.')
        return redirect('owner-dashboard')
    
    company.status = 'ACTIVE'
    company.save()
    
    # Log the action
    log_audit(
        request,
        'COMPANY_REACTIVATED',
        company,
        f"Company {company.name} reactivated by {request.user.get_full_name()}",
    )
    
    messages.success(request, f'{company.name} has been reactivated.')
    return redirect('owner-dashboard')
```

### Update change_plan()

Find the function and add logging:
```python
@login_required
def change_plan(request, company_id):
    """Change company plan"""
    if request.user.role != 'OWNER':
        return redirect('dashboard')
    
    try:
        company = Company.objects.get(id=company_id)
    except Company.DoesNotExist:
        messages.error(request, 'Company not found.')
        return redirect('owner-dashboard')
    
    if request.method == 'POST':
        plan_id = request.POST.get('plan_id')
        try:
            new_plan = Plan.objects.get(id=plan_id)
        except Plan.DoesNotExist:
            messages.error(request, 'Invalid plan.')
            return redirect('change-plan', company_id=company_id)
        
        old_plan = company.plan.name
        company.plan = new_plan
        company.save()
        
        # Log the action
        log_audit(
            request,
            'PLAN_CHANGED',
            company,
            f"Plan changed from {old_plan} to {new_plan.name} for {company.name}",
            {'old_plan': old_plan, 'new_plan': new_plan.name, 'price': str(new_plan.price_monthly)}
        )
        
        messages.success(request, f'Plan changed to {new_plan.name}.')
        return redirect('owner-dashboard')
    
    plans = Plan.objects.all()
    return render(request, 'owner_change_plan.html', {
        'company': company,
        'plans': plans,
    })
```

### Update rotate_company_key()

```python
@login_required
def rotate_company_key(request, company_id):
    """Rotate company API key"""
    if request.user.role != 'OWNER':
        return redirect('dashboard')
    
    try:
        company = Company.objects.get(id=company_id)
    except Company.DoesNotExist:
        messages.error(request, 'Company not found.')
        return redirect('owner-dashboard')
    
    import secrets
    old_key = company.company_key
    company.company_key = f"company_{secrets.token_hex(16)}"
    company.save()
    
    # Log the action
    log_audit(
        request,
        'KEY_ROTATED',
        company,
        f"API key rotated for {company.name} by {request.user.get_full_name()}",
        {'old_key': old_key[:8]+'***...', 'new_key': company.company_key[:8]+'***...'}
    )
    
    messages.success(request, 'API key rotated successfully.')
    return redirect('owner-dashboard')
```

---

## FILE 6: backend/core/web_views.py

### Add This Import at Top

```python
from .audit import log_audit
```

### Find employee_toggle_status_view() and Add Logging

```python
@login_required
def employee_toggle_status_view(request, emp_id):
    """Toggle employee active status"""
    if request.user.role not in ['ADMIN', 'MANAGER']:
        return redirect('dashboard')
    
    try:
        employee = User.objects.get(id=emp_id, company=request.user.company)
    except User.DoesNotExist:
        messages.error(request, 'Employee not found.')
        return redirect('employee-list')
    
    old_status = employee.is_active_employee
    employee.is_active_employee = not employee.is_active_employee
    employee.save()
    
    # Log the action
    action = 'EMPLOYEE_DEACTIVATED' if not employee.is_active_employee else 'EMPLOYEE_REACTIVATED'
    log_audit(
        request,
        action,
        request.user.company,
        f"Employee {employee.get_full_name()} {'deactivated' if not employee.is_active_employee else 'reactivated'}",
        {'employee_id': employee.id, 'old_status': old_status, 'new_status': employee.is_active_employee}
    )
    
    status_text = 'deactivated' if not employee.is_active_employee else 'reactivated'
    messages.success(request, f'Employee {status_text}.')
    return redirect('employee-list')
```

---

## FILE 7: backend/templates/owner_dashboard.html

### Add No-Sync Alert (after the h1, before company list)

```html
<!-- Add this after <h2>Dashboard</h2> and before company cards -->

{% if not_synced_count > 0 %}
<div class="alert alert-warning alert-dismissible fade show" role="alert">
    <strong>⚠️ Sync Issues Detected</strong>
    <p class="mb-2">{{ not_synced_count }} company/companies haven't synced in the last 24 hours:</p>
    <ul class="mb-0">
    {% for company in not_synced_companies %}
        <li>
            <a href="{% url 'company-detail' company.id %}">{{ company.name }}</a>
            (Last sync: <code>{{ company.last_sync_at|default:"Never" }}</code>)
        </li>
    {% endfor %}
    </ul>
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
</div>
{% endif %}
```

### Update owner_dashboard view

In `owner_views.py`, find the `owner_dashboard` function and add this before the return statement:

```python
# Find companies not synced in 24 hours
from datetime import timedelta
cutoff = timezone.now() - timedelta(hours=24)
not_synced = Company.objects.filter(
    status='ACTIVE',
    last_sync_at__isnull=False,
    last_sync_at__lt=cutoff
)

context['not_synced_count'] = not_synced.count()
context['not_synced_companies'] = not_synced[:5]
```

---

## MIGRATION COMMANDS

Run in terminal:

```bash
cd backend

# 1. Create migration files
python manage.py makemigrations core

# 2. Review migrations (check the files)
ls core/migrations/000*.py

# 3. Apply to database
python manage.py migrate core

# 4. Test (if you have tests)
python manage.py test core
```

---

## QUICK TEST

```bash
# 1. Start server
python manage.py runserver

# 2. Test heartbeat (replace with real company key)
curl -X POST http://localhost:8000/api/agent/heartbeat/ \
  -H "X-Company-Key: company_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# Response should be:
# {"status": "ok", "server_time": "2026-02-01T...", "company_status": "ACTIVE", "message": "Heartbeat received"}

# 3. Test policy fetch
curl -X GET http://localhost:8000/api/policy/ \
  -H "X-Company-Key: company_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# Response should include policy settings

# 4. Check audit log
python manage.py shell
>>> from core.models import AuditLog
>>> AuditLog.objects.count()  # Should show logs created
>>> AuditLog.objects.latest('timestamp').description
```

---

## SUMMARY

✅ Added CompanyPolicy model (server controls agent behavior)  
✅ Added AuditLog model (tracks all admin actions)  
✅ Added agent_heartbeat endpoint (agent reports alive every 5 min)  
✅ Added get_company_policy endpoint (agent fetches settings)  
✅ Updated all owner views with logging  
✅ Updated employee toggle with logging  
✅ Added no-sync alert to dashboard  

**Time to implement:** 2-3 hours  
**Lines of code added:** ~400  
**Files modified:** 7  
**Files created:** 1  

Next: Create admin policy settings view (backend/core/web_views.py + template)

