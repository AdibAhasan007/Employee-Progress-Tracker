# Multi-Tenant OWNER Portal - Detailed Code Changes

## Files Modified/Created Summary

### NEW FILES (5)
1. `backend/core/middleware.py` - Company key validation
2. `backend/core/permissions.py` - Custom DRF permissions
3. `backend/core/owner_views.py` - OWNER portal views (320 lines)
4. `backend/core/migrations/0007_add_multitenant_foundation.py` - Database migration
5. `backend/core/tests_multitenant.py` - 17 comprehensive tests

### TEMPLATES (3 NEW)
6. `backend/templates/owner_dashboard.html` - Main OWNER dashboard
7. `backend/templates/owner_company_detail.html` - Company analytics
8. `backend/templates/owner_reports.html` - Analytics reports

### MODIFIED FILES (3)
9. `backend/core/models.py` - Added 4 new models, updated 8 existing models
10. `backend/core/urls.py` - Added 8 new OWNER routes
11. `backend/tracker_backend/settings.py` - Added middleware to pipeline

---

## 📝 DETAILED CHANGES BY FILE

### 1. `backend/core/models.py`

#### NEW MODELS (4 additions, ~150 lines)

**Plan Model** (Lines ~1-35)
```python
class Plan(models.Model):
    name = models.CharField(max_length=100, choices=PLAN_TIER_CHOICES, unique=True)
    description = models.TextField(blank=True)
    max_employees = models.IntegerField(default=5)
    max_storage_gb = models.IntegerField(default=10)
    screenshot_retention_days = models.IntegerField(default=30)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Company Model** (Lines ~38-100)
```python
class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    email = models.EmailField(blank=True)
    contact_person = models.CharField(max_length=255, blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    company_key = models.CharField(max_length=64, unique=True, db_index=True)
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TRIAL')
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    subscription_expires_at = models.DateTimeField(null=True, blank=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.company_key:
            self.company_key = f"company_{secrets.token_hex(16)}"
        super().save(*args, **kwargs)
    
    def is_active_subscription(self):
        # Check if subscription is valid and not expired
```

**Subscription Model** (Lines ~103-125)
```python
class Subscription(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
```

**CompanyUsageDaily Model** (Lines ~333-365)
```python
class CompanyUsageDaily(models.Model):
    """Aggregated daily metrics - OWNER READ-ONLY"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='daily_usage')
    date = models.DateField(db_index=True)
    total_active_seconds = models.IntegerField(default=0)
    total_idle_seconds = models.IntegerField(default=0)
    num_employees_active = models.IntegerField(default=0)
    num_sessions = models.IntegerField(default=0)
    num_screenshots = models.IntegerField(default=0)
    storage_used_mb = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('company', 'date')
        ordering = ['-date']
        indexes = [models.Index(fields=['company', 'date'])]
```

#### UPDATED MODELS (8 modifications)

**User Model** (Lines ~128-192)
- Added: `company = ForeignKey(Company, null=True, blank=True)`
- Updated ROLE_CHOICES: Added `('OWNER', 'Software Owner')`
- Kept: `company_name` for backward compatibility

**CompanySettings Model** (Lines ~168-172)
- Added: `company = OneToOneField(Company, null=True, blank=True)`

**WorkSession Model** (Line ~198)
- Added: `company = ForeignKey(Company, on_delete=models.CASCADE)`

**ApplicationUsage Model** (Line ~235)
- Added: `company = ForeignKey(Company, on_delete=models.CASCADE)`

**WebsiteUsage Model** (Line ~252)
- Added: `company = ForeignKey(Company, on_delete=models.CASCADE)`

**ActivityLog Model** (Line ~269)
- Added: `company = ForeignKey(Company, on_delete=models.CASCADE)`

**Screenshot Model** (Line ~283)
- Added: `company = ForeignKey(Company, on_delete=models.CASCADE)`

**Task Model** (Line ~299)
- Added: `company = ForeignKey(Company, on_delete=models.CASCADE)`

---

### 2. `backend/core/middleware.py` (NEW FILE, 65 lines)

```python
class CompanyKeyValidationMiddleware:
    """Validates X-Company-Key header on protected API endpoints."""
    
    PROTECTED_PATHS = [
        '/api/login',
        '/api/login-check',
        '/api/work-session/',
        '/api/check-session-active',
        '/api/upload/',
        '/api/screenshot/',
        '/api/tasks/',
    ]
    
    def __call__(self, request):
        # Check if protected endpoint
        # Validate X-Company-Key header
        # Check company.status != SUSPENDED
        # Check subscription not expired
        # Update company.last_sync_at
        # Attach request.company
```

**Key Features**:
- Intercepts all API requests
- Validates company_key from X-Company-Key header
- Checks subscription status and expiration
- Returns proper JSON error messages
- Updates last_sync_at for tracking

---

### 3. `backend/core/permissions.py` (NEW FILE, 110 lines)

```python
class IsOwner(BasePermission):
    """OWNER role only"""

class IsCompanyAdmin(BasePermission):
    """ADMIN within own company"""

class IsSameCompanyUser(BasePermission):
    """Users scoped by company"""

class CanViewAggregateDataOnly(BasePermission):
    """OWNER CANNOT access individual employee data"""
    EMPLOYEE_DATA_MODELS = [
        'WorkSession', 'ApplicationUsage', 'WebsiteUsage',
        'ActivityLog', 'Screenshot', 'Task', 'User'
    ]

class IsEmployeeOrAdmin(BasePermission):
    """Employees see own, ADMINs see company-wide"""
```

**Key Feature**: `CanViewAggregateDataOnly` explicitly forbids OWNER from reading employee tracking data.

---

### 4. `backend/core/owner_views.py` (NEW FILE, 320 lines)

**8 Views Implemented**:

1. **`owner_dashboard`** - Main dashboard, lists all companies
2. **`company_detail`** - Analytics for single company
3. **`create_company`** - POST: Create new trial company
4. **`change_plan`** - POST: Upgrade/downgrade plan
5. **`suspend_company`** - POST: Disable company
6. **`reactivate_company`** - POST: Re-enable company
7. **`rotate_company_key`** - POST: Generate new key
8. **`owner_reports`** - Analytics dashboard

**Key Functions**:
- `@owner_required` decorator ensures OWNER role
- Queries only aggregate data (CompanyUsageDaily)
- Returns JSON for AJAX calls
- All actions logged via Subscription model

---

### 5. `backend/core/migrations/0007_add_multitenant_foundation.py` (NEW FILE, 170 lines)

**Operations** (in order):
1. CreateModel Plan
2. CreateModel Company
3. CreateModel Subscription
4. AddField User.company
5. AlterField User.role (add OWNER)
6. AddField CompanySettings.company
7. AddField WorkSession.company
8. AddField ApplicationUsage.company
9. AddField WebsiteUsage.company
10. AddField ActivityLog.company
11. AddField Screenshot.company
12. AddField Task.company
13. CreateModel CompanyUsageDaily
14. AddIndex on CompanyUsageDaily(company, date)

**All fields set to null=True initially** to allow migration without data loss.

---

### 6. `backend/core/tests_multitenant.py` (NEW FILE, 370 lines)

**Test Classes**:

1. **MultiTenantFoundationTests** (5 tests)
   - Company creation & key generation
   - Key uniqueness
   - Subscription status checks
   - Subscription tracking

2. **OwnerDataIsolationTests** (4 tests)
   - OWNER user creation
   - Company scoping
   - Aggregate table creation
   - Unique constraints

3. **OwnerPortalViewTests** (3 tests)
   - Login required
   - Access control
   - OWNER access works

4. **CompanyKeyValidationTests** (3 tests)
   - Valid key acceptance
   - Invalid key rejection
   - Suspended company rejection

5. **PlanManagementTests** (2 tests)
   - Plan upgrade
   - Subscription audit trail

**Run**: `python manage.py test core.tests_multitenant -v 2`

---

### 7. `backend/core/urls.py` (MODIFIED, +16 lines)

**Added Imports**:
```python
from .owner_views import (
    owner_dashboard, company_detail, create_company, change_plan,
    suspend_company, reactivate_company, rotate_company_key, owner_reports
)
```

**Added URL Patterns** (8 new routes):
```python
path('owner/dashboard/', owner_dashboard, name='owner-dashboard'),
path('owner/company/<int:company_id>/', company_detail, name='owner-company-detail'),
path('owner/company/create/', create_company, name='owner-create-company'),
path('owner/company/<int:company_id>/change-plan/', change_plan, name='owner-change-plan'),
path('owner/company/<int:company_id>/suspend/', suspend_company, name='owner-suspend-company'),
path('owner/company/<int:company_id>/reactivate/', reactivate_company, name='owner-reactivate-company'),
path('owner/company/<int:company_id>/rotate-key/', rotate_company_key, name='owner-rotate-key'),
path('owner/reports/', owner_reports, name='owner-reports'),
```

---

### 8. `backend/tracker_backend/settings.py` (MODIFIED, +1 line)

**Added to MIDDLEWARE list**:
```python
'core.middleware.CompanyKeyValidationMiddleware',
```

**Location**: End of MIDDLEWARE list (before closing bracket)

**Effect**: Activates company key validation on all requests

---

### 9-11. TEMPLATES (3 NEW HTML FILES)

#### `backend/templates/owner_dashboard.html` (~130 lines)
- Shows key metrics (total, active, trial companies)
- Companies table with status, plan, usage, sync time
- "View" buttons for each company
- "New Company" button

#### `backend/templates/owner_company_detail.html` (~210 lines)
- Company info & subscription details
- Plan selector dropdown
- Company key display & copy button
- Key rotation button
- Usage metrics cards (employees, sessions, screenshots, storage)
- Daily usage line chart (90 days)
- Suspend/reactivate buttons

#### `backend/templates/owner_reports.html` (~150 lines)
- Status summary (Active, Trial, Suspended counts)
- Top 10 companies by usage
- Plan distribution pie chart
- Revenue potential calculation
- Subscription health % metric

---

## 🔗 Integration Points

### Desktop App ↔ Backend
```
Desktop App sends X-Company-Key header
  ↓
CompanyKeyValidationMiddleware intercepts
  ↓
Validates company exists & subscription active
  ↓
Rejects with 401/403 if invalid
  ↓
Attaches request.company to request object
  ↓
View uses request.company to scope queries
```

### OWNER Dashboard ↔ Database
```
OWNER logs in (role='OWNER')
  ↓
Accesses /owner/dashboard/
  ↓
Views queries CompanyUsageDaily (aggregate only)
  ↓
Cannot access WorkSession, Screenshot tables (permission denied)
  ↓
Can trigger admin actions (create, plan change, suspend)
```

---

## 📊 Data Flow Examples

### Example 1: Company Key Validation (Desktop App)
```
1. Desktop app starts, sends:
   POST /api/login
   Headers: {'X-Company-Key': 'company_abc123...'}
   Body: {'email': 'emp@company.com', 'password': 'pass'}

2. Middleware intercepts, checks:
   - Company exists? If not → 401
   - Status != SUSPENDED? If suspended → 403
   - Trial/subscription not expired? If expired → 403

3. If valid:
   - Updates company.last_sync_at
   - Attaches request.company
   - Allows request through

4. View receives request with company scope
   - Creates/updates tracking records with company_id
```

### Example 2: OWNER Changing Plan
```
1. OWNER clicks "Change Plan" button on company detail page
2. Selects new plan from dropdown
3. Form submits POST to /owner/company/5/change-plan/
4. View checks request.user.role == 'OWNER'
5. Fetches Company(id=5)
6. Updates company.plan = Plan(id=2)
7. Returns JSON: {"status": true, "plan": "PRO"}
8. Frontend reloads page to show new plan

Audit Trail: Subscription table unchanged (create new record on renewal)
```

### Example 3: Querying Aggregates (OWNER Dashboard)
```
1. OWNER accesses /owner/dashboard/
2. View queries:
   companies = Company.objects.all()
   for company:
       daily_usage = company.daily_usage.filter(date__gte=30_days_ago)
       total_minutes = daily_usage.aggregate(Sum('total_active_seconds'))
       num_screenshots = daily_usage.aggregate(Sum('num_screenshots'))

3. CANNOT directly query:
   - WorkSession.objects.all() → Would show ALL work (VIOLATION!)
   - Screenshot.objects.all() → Would show ALL screenshots (VIOLATION!)
   - Instead: Uses CompanyUsageDaily which only has aggregates

4. Returns to template with company list + aggregates
```

---

## ✅ Backward Compatibility

### Existing Installations
1. Migration 0007 adds new fields with `null=True`
2. Existing data continues to work with `company=NULL`
3. Recommend data migration to set `company` FK
4. OWNER role is optional - existing systems work without it

### Desktop App
- If old app doesn't send X-Company-Key header → 401 error
- Update config: `COMPANY_KEY = "company_xyz..."`
- Add header to all API calls

### Existing Users/Admins
- Still work as before
- ROLE remains ADMIN/EMPLOYEE
- Assigned to default company via migration
- No UI changes for them

---

## 🚀 Deployment Order

1. **Backup database** (critical)
2. **Deploy code changes** (all files listed above)
3. **Run migration**: `python manage.py migrate core 0007`
4. **Create plans**: `python manage.py shell < setup_plans.py`
5. **Run data migration** (if needed): Assign existing data to default company
6. **Create OWNER user**: `python manage.py createsuperuser --role=OWNER`
7. **Test locally**: Run smoke tests
8. **Deploy to staging**: Full testing
9. **Deploy to production**: Monitor last_sync_at updates
10. **Update desktop app**: Add X-Company-Key to requests

---

**Total Lines Added**: ~1,500  
**Total Lines Modified**: ~100  
**Total Files**: 11 (8 new, 3 modified)  
**Test Coverage**: 17 tests  
**Time to Deploy**: ~30 minutes

