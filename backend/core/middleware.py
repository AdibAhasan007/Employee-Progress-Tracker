"""
Multi-tenant middleware to validate company_key from X-Company-Key header.
Ensures desktop app belongs to an active company with valid subscription.
"""

from django.http import JsonResponse
from django.utils import timezone
from .models import Company


class CompanyKeyValidationMiddleware:
    """
    Validates X-Company-Key header on API endpoints.
    Rejects requests if:
    - Company is SUSPENDED
    - Company trial/subscription is EXPIRED
    - Key is invalid or missing (for protected endpoints)
    """
    
    # Endpoints that REQUIRE company_key (Desktop app API)
    PROTECTED_PATHS = [
        '/api/login',
        '/api/login-check',
        '/api/work-session/',
        '/api/check-session-active',
        '/api/upload/',
        '/api/screenshot/',
        '/api/desktop-tasks/',  # Desktop app tasks API
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if this is a protected endpoint
        is_protected = any(
            request.path.startswith(path) for path in self.PROTECTED_PATHS
        )
        
        if is_protected:
            company_key = request.headers.get('X-Company-Key')
            
            if not company_key:
                return JsonResponse({
                    'status': False,
                    'message': 'X-Company-Key header required'
                }, status=401)
            
            try:
                company = Company.objects.get(company_key=company_key)
            except Company.DoesNotExist:
                return JsonResponse({
                    'status': False,
                    'message': 'Invalid company key'
                }, status=401)
            
            # Check subscription status
            if company.status == 'SUSPENDED':
                return JsonResponse({
                    'status': False,
                    'message': 'Company subscription is suspended'
                }, status=403)
            
            # Check trial/subscription expiration
            if not company.is_active_subscription():
                return JsonResponse({
                    'status': False,
                    'message': 'Company subscription expired'
                }, status=403)
            
            # Update last_sync timestamp
            company.last_sync_at = timezone.now()
            company.save(update_fields=['last_sync_at'])
            
            # Attach company to request for use in views
            request.company = company
        
        response = self.get_response(request)
        return response
