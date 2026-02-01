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
        user=request.user if request.user.is_authenticated else None,
        description=description,
        details=details or {},
        ip_address=get_client_ip(request),
        timestamp=timezone.now(),
    )
