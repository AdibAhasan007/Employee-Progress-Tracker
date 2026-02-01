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