"""
Custom DRF permissions for multi-tenant data isolation.
Ensures OWNER role can only access aggregated company data (CompanyUsageDaily),
not individual employee tracking data.
"""

from rest_framework.permissions import BasePermission
from .models import Company


class IsOwner(BasePermission):
    """
    Allows access only to users with OWNER role.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'OWNER'


class IsCompanyAdmin(BasePermission):
    """
    Allows access only to users with ADMIN role within their company.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ADMIN'
    
    def has_object_permission(self, request, view, obj):
        # Check if object belongs to user's company
        if hasattr(obj, 'company'):
            return obj.company == request.user.company
        return False


class IsSameCompanyUser(BasePermission):
    """
    Ensures users can only access data from their own company.
    Employees can only see their own data.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # OWNER can never access individual employee data
        if request.user.role == 'OWNER':
            return False
        
        # Check if object belongs to user's company
        if hasattr(obj, 'company'):
            return obj.company == request.user.company
        
        # Check if it's related through employee
        if hasattr(obj, 'employee'):
            return obj.employee.company == request.user.company
        
        return False


class CanViewAggregateDataOnly(BasePermission):
    """
    OWNER can view CompanyUsageDaily (aggregated) but NOT individual employee data.
    """
    
    EMPLOYEE_DATA_MODELS = [
        'WorkSession',
        'ApplicationUsage',
        'WebsiteUsage',
        'ActivityLog',
        'Screenshot',
        'Task',
        'User',  # Can't view employee list
    ]
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # OWNER can only view aggregated data
        if request.user.role == 'OWNER':
            # Check the model being accessed
            if hasattr(view, 'queryset') and view.queryset is not None:
                model_name = view.queryset.model.__name__
                if model_name in self.EMPLOYEE_DATA_MODELS:
                    return False
            return True
        
        return True


class IsEmployeeOrAdmin(BasePermission):
    """
    Allows EMPLOYEE to view own data, ADMIN to view company data.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'OWNER':
            return False
        
        if request.user.role == 'ADMIN':
            # Admin can see any data from their company
            return getattr(obj, 'company', None) == request.user.company
        
        if request.user.role == 'EMPLOYEE':
            # Employee can only see their own data
            if hasattr(obj, 'employee'):
                return obj.employee == request.user
            if isinstance(obj, type(request.user)):
                return obj == request.user
        
        return False
