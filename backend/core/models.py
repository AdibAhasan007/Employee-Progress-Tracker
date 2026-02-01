from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid
import secrets

# ==========================================
# 0. Multi-Tenant Foundation
# ==========================================

class Plan(models.Model):
    """
    Subscription plans available (Free, Pro, Enterprise).
    """
    PLAN_TIER_CHOICES = (
        ('FREE', 'Free'),
        ('PRO', 'Professional'),
        ('ENTERPRISE', 'Enterprise'),
    )
    
    name = models.CharField(max_length=100, choices=PLAN_TIER_CHOICES, unique=True)
    description = models.TextField(blank=True)
    
    # Limits
    max_employees = models.IntegerField(default=5, help_text="Max employees allowed")
    max_storage_gb = models.IntegerField(default=10, help_text="Max storage in GB")
    screenshot_retention_days = models.IntegerField(default=30)
    
    # Pricing
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['max_employees']
    
    def __str__(self):
        return self.name


class Company(models.Model):
    """
    Represents a customer company using the software.
    """
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('SUSPENDED', 'Suspended'),
        ('TRIAL', 'Trial'),
    )
    
    name = models.CharField(max_length=255, unique=True)
    email = models.EmailField(blank=True)
    contact_person = models.CharField(max_length=255, blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    
    # Company identity for desktop sync
    company_key = models.CharField(max_length=64, unique=True, db_index=True)
    
    # Subscription
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TRIAL')
    
    # Billing/Lifecycle
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    subscription_expires_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    address = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sync_at = models.DateTimeField(null=True, blank=True, help_text="Last desktop app sync")
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.company_key:
            # Generate secure random key: "company_<32-char-hex>"
            self.company_key = f"company_{secrets.token_hex(16)}"
        super().save(*args, **kwargs)
    
    def is_active_subscription(self):
        """Check if company has active subscription (not suspended/expired)."""
        if self.status == 'SUSPENDED':
            return False
        if self.status == 'TRIAL' and self.trial_ends_at:
            return timezone.now() < self.trial_ends_at
        if self.status == 'ACTIVE' and self.subscription_expires_at:
            return timezone.now() < self.subscription_expires_at
        return True
    
    def __str__(self):
        return self.name


class Subscription(models.Model):
    """
    Tracks subscription history and renewals for auditing.
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    status = models.CharField(max_length=20, choices=(('ACTIVE', 'Active'), ('EXPIRED', 'Expired'), ('CANCELLED', 'Cancelled')), default='ACTIVE')
    
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.company.name} - {self.plan.name}"


class CompanyPolicy(models.Model):
    """
    Policy settings that control desktop agent behavior.
    Server-driven configuration for tracking.
    """
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
    """
    Complete audit trail for compliance and accountability.
    Immutable log of all administrative actions.
    """
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
    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True)  # Who performed action
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


# ==========================================
# 1. User & Employee Management
# ==========================================

class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Roles: Admin, Manager, Employee, Owner.
    """
    ROLE_CHOICES = (
        ('OWNER', 'Software Owner'),
        ('ADMIN', 'Company Admin'),
        ('MANAGER', 'Manager'),
        ('EMPLOYEE', 'Employee'),
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='EMPLOYEE')
    designation = models.CharField(max_length=100, blank=True, null=True, help_text='Job title (e.g., HR Manager, CEO, Developer)')
    
    # Multi-tenant support
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, related_name='users')
    
    # Legacy field (keep for backward compatibility, soft-deprecated)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    
    # Phase 4: Department assignment
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True, related_name='department_members')
    
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    timezone = models.CharField(max_length=50, default='Asia/Dhaka')
    
    # Tracker specific fields
    tracker_token = models.CharField(max_length=100, blank=True, null=True, unique=True)
    is_active_employee = models.BooleanField(default=True) # Separate from User.is_active
    last_agent_sync_at = models.DateTimeField(null=True, blank=True, help_text="Last desktop app heartbeat")
    
    def save(self, *args, **kwargs):
        if not self.tracker_token and self.role == 'EMPLOYEE':
            self.tracker_token = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"

class CompanySettings(models.Model):
    """
    Global settings for the company/admin including branding.
    """
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='settings', null=True, blank=True)
    
    # Company Information
    company_name = models.CharField(max_length=200)
    company_tagline = models.CharField(max_length=500, blank=True, default="Employee Activity Tracker")
    address = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=30, blank=True, null=True)
    map_embed_url = models.URLField(max_length=500, blank=True, null=True, help_text="Optional custom map embed URL")
    terms_url = models.URLField(max_length=500, blank=True, null=True)
    privacy_url = models.URLField(max_length=500, blank=True, null=True)
    cookies_url = models.URLField(max_length=500, blank=True, null=True)
    
    # Branding
    logo = models.ImageField(upload_to='company/', blank=True, null=True, help_text="Company logo (recommended: 200x200px)")
    favicon = models.ImageField(upload_to='company/', blank=True, null=True, help_text="Website favicon (recommended: 32x32px)")
    primary_color = models.CharField(max_length=7, default="#667eea", help_text="Primary brand color (hex)")
    secondary_color = models.CharField(max_length=7, default="#764ba2", help_text="Secondary brand color (hex)")
    
    # Work Settings
    daily_target_hours = models.FloatField(default=8.0)
    idle_threshold_minutes = models.IntegerField(default=5)
    screenshot_retention_days = models.IntegerField(default=30)
    employee_limit = models.IntegerField(default=20)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Company Settings"
    
    def __str__(self):
        return self.company_name

# ==========================================
# 2. Work Sessions
# ==========================================

class WorkSession(models.Model):
    """
    Represents a single work session (Start -> Stop).
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='work_sessions')
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='work_sessions')
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    
    # Aggregated stats (calculated on stop)
    total_seconds = models.IntegerField(default=0)
    active_seconds = models.IntegerField(default=0)
    idle_seconds = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.username} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"

# ==========================================
# 3. Activity Tracking (Apps & Websites)
# ==========================================

class ApplicationUsage(models.Model):
    """
    Logs usage of desktop applications.
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='app_usages')
    work_session = models.ForeignKey(WorkSession, on_delete=models.CASCADE, related_name='app_usages')
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    app_name = models.CharField(max_length=255)
    window_title = models.CharField(max_length=500, blank=True)
    active_seconds = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.app_name} ({self.active_seconds}s)"

class WebsiteUsage(models.Model):
    """
    Logs usage of websites.
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='website_usages')
    work_session = models.ForeignKey(WorkSession, on_delete=models.CASCADE, related_name='website_usages')
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    domain = models.CharField(max_length=255)
    url = models.TextField(blank=True, null=True, help_text="Full URL path including query parameters")
    active_seconds = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.domain} ({self.active_seconds}s)"

class ActivityLog(models.Model):
    """
    Granular logs for Active vs Idle time (e.g., every minute).
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='activity_logs')
    work_session = models.ForeignKey(WorkSession, on_delete=models.CASCADE, related_name='activity_logs')
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    minute_type = models.CharField(max_length=20, choices=(('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')))
    duration_seconds = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

# ==========================================
# 4. Screenshots
# ==========================================

class Screenshot(models.Model):
    """
    Stores metadata and paths for captured screenshots.
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='screenshots')
    work_session = models.ForeignKey(WorkSession, on_delete=models.CASCADE, related_name='screenshots')
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='screenshots/%Y/%m/%d/')
    capture_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Screenshot {self.id} - {self.employee.username}"

# ==========================================
# 5. Task Management
# ==========================================

class Task(models.Model):
    """
    Tasks assigned to employees.
    """
    STATUS_CHOICES = (
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('DONE', 'Done'),
    )
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    
    start_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    success_note = models.TextField(blank=True, help_text="Employee's note upon completion")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# ==========================================
# 6. Aggregate Data for OWNER (Read-Only)
# ==========================================

class CompanyUsageDaily(models.Model):
    """
    Aggregated daily usage metrics per company.
    OWNER can ONLY view this table (not raw employee data).
    Updated via daily aggregation job.
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='daily_usage')
    date = models.DateField(db_index=True)
    
    # Aggregates (numbers only, no individual employee identifiers)
    total_active_seconds = models.IntegerField(default=0)
    total_idle_seconds = models.IntegerField(default=0)
    num_employees_active = models.IntegerField(default=0)  # How many employees tracked data that day
    num_sessions = models.IntegerField(default=0)
    num_screenshots = models.IntegerField(default=0)
    
    # Storage
    storage_used_mb = models.IntegerField(default=0)  # Screenshots + media
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('company', 'date')
        ordering = ['-date']
        indexes = [
            models.Index(fields=['company', 'date']),
        ]
    
    def __str__(self):
        return f"{self.company.name} - {self.date}"


# ==========================================
# 7. PHASE 3: Stripe Billing & Subscriptions
# ==========================================

class SubscriptionTier(models.Model):
    """
    Subscription tier definitions with Stripe integration.
    """
    TIER_CHOICES = (
        ('FREE', 'Free'),
        ('PRO', 'Professional'),
        ('ENTERPRISE', 'Enterprise'),
    )
    
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, unique=True)
    name = models.CharField(max_length=100, help_text="Display name")
    description = models.TextField(blank=True)
    
    # Stripe Integration
    stripe_price_id = models.CharField(max_length=255, blank=True, help_text="Stripe Price ID (e.g., price_1ABC...)")
    
    # Pricing
    monthly_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Monthly cost in USD")
    annual_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Annual cost in USD (if applicable)")
    
    # Limits
    max_employees = models.IntegerField(default=5, help_text="Max concurrent employees")
    max_agents = models.IntegerField(default=5, help_text="Max active desktop agents")
    max_storage_gb = models.IntegerField(default=10, help_text="Max screenshot storage in GB")
    screenshot_retention_days = models.IntegerField(default=30, help_text="Days to keep screenshots")
    
    # Features
    features = models.JSONField(
        default=dict,
        blank=True,
        help_text="Features JSON: {screenshots: bool, website_tracking: bool, app_tracking: bool, ...}"
    )
    
    # Metadata
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0, help_text="Display order in UI")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order']
    
    def __str__(self):
        return f"{self.name} (${self.monthly_cost}/month)"


class StripeCustomer(models.Model):
    """
    Links Company to Stripe Customer ID.
    """
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='stripe_customer')
    stripe_customer_id = models.CharField(max_length=255, unique=True, db_index=True)
    email_synced = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.company.name} ({self.stripe_customer_id})"


class StripeBillingSubscription(models.Model):
    """
    Active subscription linked to Stripe.
    """
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('PAST_DUE', 'Past Due'),
        ('INACTIVE', 'Inactive'),
        ('CANCELLED', 'Cancelled'),
    )
    
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='stripe_subscription')
    tier = models.ForeignKey(SubscriptionTier, on_delete=models.PROTECT)
    
    # Stripe References
    stripe_subscription_id = models.CharField(max_length=255, unique=True, db_index=True)
    stripe_customer_id = models.CharField(max_length=255, db_index=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    # Billing Dates
    current_period_start = models.DateTimeField(help_text="Current billing period start")
    current_period_end = models.DateTimeField(help_text="Current billing period end")
    
    # Auto-renewal
    auto_renewal = models.BooleanField(default=True)
    
    # Payment Method
    default_payment_method_id = models.CharField(max_length=255, blank=True, help_text="Stripe Payment Method ID")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.company.name} - {self.tier.name}"
    
    def is_active_subscription(self):
        """Check if subscription is currently active."""
        return self.status == 'ACTIVE' and self.current_period_end > timezone.now()


class StripeInvoice(models.Model):
    """
    Payment invoices from Stripe.
    """
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('OPEN', 'Open'),
        ('PAID', 'Paid'),
        ('VOID', 'Void'),
        ('UNCOLLECTIBLE', 'Uncollectible'),
    )
    
    subscription = models.ForeignKey(StripeBillingSubscription, on_delete=models.CASCADE, related_name='invoices')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='stripe_invoices')
    
    # Stripe References
    stripe_invoice_id = models.CharField(max_length=255, unique=True, db_index=True)
    
    # Invoice Details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='USD')
    
    # Dates
    issued_date = models.DateTimeField(help_text="When invoice was created")
    due_date = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # Links
    hosted_invoice_url = models.URLField(blank=True, help_text="Stripe hosted invoice URL")
    pdf_url = models.URLField(blank=True, help_text="PDF invoice URL")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-issued_date']
        indexes = [
            models.Index(fields=['company', '-issued_date']),
            models.Index(fields=['status', '-issued_date']),
        ]
    
    def __str__(self):
        return f"Invoice {self.stripe_invoice_id} - {self.company.name}"


class AlertNotification(models.Model):
    """
    Real-time alerts for admins (offline agents, payment failures, etc.).
    """
    ALERT_TYPE_CHOICES = (
        ('AGENT_OFFLINE', 'Agent Offline'),
        ('AGENT_NEVER_SYNCED', 'Agent Never Synced'),
        ('PAYMENT_FAILED', 'Payment Failed'),
        ('SUBSCRIPTION_EXPIRING', 'Subscription Expiring'),
        ('USAGE_HIGH', 'High Usage'),
        ('POLICY_CHANGED', 'Policy Changed'),
        ('SYSTEM_ERROR', 'System Error'),
    )
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='alert_notifications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='alerts_received')
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Related object (for linking to specific entity)
    related_employee_id = models.IntegerField(null=True, blank=True, help_text="Related User ID if agent-related")
    related_data = models.JSONField(default=dict, blank=True, help_text="Additional context as JSON")
    
    # Status
    is_read = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', '-created_at']),
            models.Index(fields=['is_read', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.company.name}"


# ==========================================
# PHASE 4: ENTERPRISE FEATURES
# ==========================================

class Department(models.Model):
    """
    Department/Division structure within a company.
    Supports hierarchical organization.
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Hierarchy
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subdepartments')
    
    # Department Head
    head = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_departments')
    
    # Budget & Cost Center
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Monthly budget")
    cost_center_code = models.CharField(max_length=50, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['company', 'name']
        unique_together = [['company', 'name']]
        indexes = [
            models.Index(fields=['company', 'is_active']),
            models.Index(fields=['parent']),
        ]
    
    def __str__(self):
        return f"{self.company.name} - {self.name}"
    
    def get_full_path(self):
        """Get full department path (e.g., 'Engineering > Backend > API')"""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name
    
    def get_all_employees(self):
        """Get all employees in this department and subdepartments"""
        from django.db.models import Q
        dept_ids = [self.id] + list(self.subdepartments.values_list('id', flat=True))
        return User.objects.filter(Q(department_id__in=dept_ids) | Q(teams__department_id__in=dept_ids)).distinct()


class Team(models.Model):
    """
    Team within a department.
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='teams')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Team Lead
    lead = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='led_teams')
    
    # Team Members (many-to-many)
    members = models.ManyToManyField(User, related_name='teams', blank=True)
    
    # Team Settings
    max_members = models.IntegerField(default=10, help_text="Maximum team size")
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['department', 'name']
        unique_together = [['company', 'name']]
        indexes = [
            models.Index(fields=['company', 'is_active']),
            models.Index(fields=['department']),
        ]
    
    def __str__(self):
        return f"{self.department.name} - {self.name}"
    
    def get_member_count(self):
        """Get current team size"""
        return self.members.count()


class ProductivityMetric(models.Model):
    """
    Daily productivity metrics aggregated by user/team/department.
    """
    METRIC_LEVEL_CHOICES = (
        ('USER', 'User'),
        ('TEAM', 'Team'),
        ('DEPARTMENT', 'Department'),
        ('COMPANY', 'Company'),
    )
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='productivity_metrics')
    metric_level = models.CharField(max_length=20, choices=METRIC_LEVEL_CHOICES)
    
    # Entity References
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='productivity_metrics')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True, related_name='productivity_metrics')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True, related_name='productivity_metrics')
    
    # Date
    date = models.DateField()
    
    # Time Metrics (in minutes)
    total_work_time = models.IntegerField(default=0, help_text="Total work time in minutes")
    productive_time = models.IntegerField(default=0, help_text="Productive time in minutes")
    idle_time = models.IntegerField(default=0, help_text="Idle time in minutes")
    break_time = models.IntegerField(default=0, help_text="Break time in minutes")
    
    # Activity Metrics
    total_activities = models.IntegerField(default=0)
    app_switches = models.IntegerField(default=0)
    website_visits = models.IntegerField(default=0)
    
    # Productivity Score (0-100)
    productivity_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', 'company']
        unique_together = [['company', 'metric_level', 'date', 'user', 'team', 'department']]
        indexes = [
            models.Index(fields=['company', 'date']),
            models.Index(fields=['metric_level', 'date']),
            models.Index(fields=['user', 'date']),
            models.Index(fields=['team', 'date']),
            models.Index(fields=['department', 'date']),
        ]
    
    def __str__(self):
        entity = self.user or self.team or self.department or self.company
        return f"{entity} - {self.date}"
    
    def calculate_productivity_score(self):
        """Calculate productivity score based on time metrics"""
        if self.total_work_time == 0:
            return 0
        
        # Productivity = (productive_time / total_work_time) * 100
        score = (self.productive_time / self.total_work_time) * 100
        self.productivity_score = min(100, max(0, score))
        return self.productivity_score


class CompanyBranding(models.Model):
    """
    Custom branding settings for white-label support.
    """
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='branding')
    
    # Logo
    logo = models.ImageField(upload_to='branding/logos/', null=True, blank=True)
    logo_url = models.URLField(max_length=500, blank=True, help_text="External logo URL")
    
    # Colors
    primary_color = models.CharField(max_length=7, default='#007bff', help_text="Hex color code")
    secondary_color = models.CharField(max_length=7, default='#6c757d', help_text="Hex color code")
    accent_color = models.CharField(max_length=7, default='#28a745', help_text="Hex color code")
    
    # Typography
    font_family = models.CharField(max_length=100, default='Arial, sans-serif')
    
    # Custom Domain
    custom_domain = models.CharField(max_length=255, blank=True, help_text="e.g., tracker.yourcompany.com")
    
    # Email Branding
    email_from_name = models.CharField(max_length=100, blank=True)
    email_from_address = models.EmailField(blank=True)
    email_footer_text = models.TextField(blank=True)
    
    # Login Page
    login_page_title = models.CharField(max_length=100, default='Employee Tracker Login')
    login_page_subtitle = models.CharField(max_length=200, blank=True)
    login_background_image = models.ImageField(upload_to='branding/backgrounds/', null=True, blank=True)
    
    # Footer
    company_website = models.URLField(max_length=500, blank=True)
    support_email = models.EmailField(blank=True)
    support_phone = models.CharField(max_length=20, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Company Brandings'
    
    def __str__(self):
        return f"Branding - {self.company.name}"


class SSOConfiguration(models.Model):
    """
    Single Sign-On (SSO) configuration for SAML/OAuth providers.
    """
    PROVIDER_CHOICES = (
        ('SAML2', 'SAML 2.0'),
        ('AZURE_AD', 'Azure Active Directory'),
        ('GOOGLE', 'Google Workspace'),
        ('OKTA', 'Okta'),
        ('CUSTOM', 'Custom OAuth2'),
    )
    
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='sso_config')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    
    # SSO Enabled
    is_enabled = models.BooleanField(default=False)
    enforce_sso = models.BooleanField(default=False, help_text="Require SSO for all users")
    
    # SAML Configuration
    saml_entity_id = models.CharField(max_length=500, blank=True)
    saml_sso_url = models.URLField(max_length=500, blank=True, help_text="Identity Provider SSO URL")
    saml_slo_url = models.URLField(max_length=500, blank=True, help_text="Single Logout URL")
    saml_x509_cert = models.TextField(blank=True, help_text="X.509 Certificate")
    
    # OAuth Configuration
    oauth_client_id = models.CharField(max_length=255, blank=True)
    oauth_client_secret = models.CharField(max_length=255, blank=True)
    oauth_authorization_url = models.URLField(max_length=500, blank=True)
    oauth_token_url = models.URLField(max_length=500, blank=True)
    oauth_user_info_url = models.URLField(max_length=500, blank=True)
    
    # Role Mapping (JSON)
    role_mapping = models.JSONField(default=dict, blank=True, help_text="Map SSO roles to app roles")
    
    # Auto-Provisioning
    auto_provision_users = models.BooleanField(default=False, help_text="Auto-create users on first login")
    default_role = models.CharField(max_length=20, default='EMPLOYEE')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'SSO Configuration'
        verbose_name_plural = 'SSO Configurations'
    
    def __str__(self):
        return f"SSO - {self.company.name} ({self.provider})"


class AnalyticsReport(models.Model):
    """
    Saved analytics reports for scheduled generation and export.
    """
    REPORT_TYPE_CHOICES = (
        ('PRODUCTIVITY', 'Productivity Report'),
        ('TIME_UTILIZATION', 'Time Utilization'),
        ('DEPARTMENT_COMPARISON', 'Department Comparison'),
        ('ACTIVITY_HEATMAP', 'Activity Heatmap'),
        ('CUSTOM', 'Custom Report'),
    )
    
    FORMAT_CHOICES = (
        ('PDF', 'PDF'),
        ('CSV', 'CSV'),
        ('EXCEL', 'Excel'),
        ('JSON', 'JSON'),
    )
    
    FREQUENCY_CHOICES = (
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('MANUAL', 'Manual Only'),
    )
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='analytics_reports')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_reports')
    
    # Report Configuration
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPE_CHOICES)
    
    # Scope
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)
    
    # Date Range
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Export Settings
    export_format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='PDF')
    
    # Scheduling
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='MANUAL')
    next_run_at = models.DateTimeField(null=True, blank=True)
    
    # Recipients (email addresses)
    recipients = models.JSONField(default=list, blank=True, help_text="List of email addresses")
    
    # Generated Report
    file = models.FileField(upload_to='reports/', null=True, blank=True)
    file_size = models.BigIntegerField(default=0, help_text="File size in bytes")
    
    # Status
    is_active = models.BooleanField(default=True)
    last_generated_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', '-created_at']),
            models.Index(fields=['report_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.company.name}"


# ==========================================
# Signals
# ==========================================

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Company)
def create_company_policy(sender, instance, created, **kwargs):
    """Auto-create policy when company is created"""
    if created:
        CompanyPolicy.objects.create(company=instance)

post_save.connect(create_company_policy, sender=Company)