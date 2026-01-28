from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid

# ==========================================
# 1. User & Employee Management
# ==========================================

class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Roles: Admin, Manager, Employee.
    """
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('MANAGER', 'Manager'),
        ('EMPLOYEE', 'Employee'),
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='EMPLOYEE')
    designation = models.CharField(max_length=100, blank=True, null=True, help_text='Job title (e.g., HR Manager, CEO, Developer)')
    company_name = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    timezone = models.CharField(max_length=50, default='Asia/Dhaka')
    
    # Tracker specific fields
    tracker_token = models.CharField(max_length=100, blank=True, null=True, unique=True)
    is_active_employee = models.BooleanField(default=True) # Separate from User.is_active
    
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
