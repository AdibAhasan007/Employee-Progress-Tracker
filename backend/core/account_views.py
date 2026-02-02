"""
Account management views for Admin and Employee users to change their credentials.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, update_session_auth_hash
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db import transaction
from .models import User
from .audit import log_audit


def admin_required(view_func):
    """Decorator to check if user is ADMIN."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'ADMIN':
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def employee_required(view_func):
    """Decorator to check if user is EMPLOYEE."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'EMPLOYEE':
            messages.error(request, 'Access denied. Employee privileges required.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


# ==========================================
# PASSWORD CHANGE
# ==========================================

@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def change_password(request):
    """
    Allow authenticated users (Admin/Employee) to change their password.
    
    GET: Display password change form
    POST: Verify current password and update to new password
    """
    user = request.user
    
    if request.method == 'GET':
        context = {
            'user': user,
            'page_title': 'Change Password'
        }
        return render(request, 'change_password.html', context)
    
    # POST: Process password change
    current_password = request.POST.get('current_password', '').strip()
    new_password = request.POST.get('new_password', '').strip()
    confirm_password = request.POST.get('confirm_password', '').strip()
    
    # Validation checks
    errors = []
    
    # Check if current password is provided
    if not current_password:
        errors.append('Current password is required.')
    
    # Check if new password is provided
    if not new_password:
        errors.append('New password is required.')
    
    # Check if passwords match
    if new_password and confirm_password and new_password != confirm_password:
        errors.append('New passwords do not match.')
    
    # Check password length
    if new_password and len(new_password) < 6:
        errors.append('New password must be at least 6 characters long.')
    
    # Verify current password
    if current_password and not user.check_password(current_password):
        errors.append('Current password is incorrect.')
    
    # Check that new password is different from current
    if new_password and current_password:
        if new_password == current_password:
            errors.append('New password must be different from current password.')
    
    if errors:
        context = {
            'user': user,
            'page_title': 'Change Password',
            'errors': errors,
            'current_password': current_password,
        }
        return render(request, 'change_password.html', context)
    
    # All validations passed - update password
    try:
        with transaction.atomic():
            user.set_password(new_password)
            user.save()
            
            # Log the password change
            log_audit(
                request,
                'PASSWORD_CHANGED',
                user.company,
                f"{user.get_role_display()} '{user.username}' changed their password",
                {'username': user.username, 'email': user.email}
            )
            
            # Update session to keep user logged in
            update_session_auth_hash(request, user)
            
            messages.success(request, '✅ Password changed successfully! Your new password is now active.')
            return redirect('change-password')
    
    except Exception as e:
        messages.error(request, f'Error changing password: {str(e)}')
        context = {
            'user': user,
            'page_title': 'Change Password',
            'errors': [str(e)]
        }
        return render(request, 'change_password.html', context)


# ==========================================
# USERNAME CHANGE
# ==========================================

@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def change_username(request):
    """
    Allow authenticated users (Admin/Employee) to change their username.
    
    GET: Display username change form
    POST: Verify current password and update username
    """
    user = request.user
    
    if request.method == 'GET':
        context = {
            'user': user,
            'page_title': 'Change Username'
        }
        return render(request, 'change_username.html', context)
    
    # POST: Process username change
    current_password = request.POST.get('current_password', '').strip()
    new_username = request.POST.get('new_username', '').strip()
    
    # Validation checks
    errors = []
    
    # Check if current password is provided
    if not current_password:
        errors.append('Current password is required to change username.')
    
    # Verify current password
    if current_password and not user.check_password(current_password):
        errors.append('Current password is incorrect.')
    
    # Check if new username is provided
    if not new_username:
        errors.append('New username is required.')
    
    # Check username length
    if new_username and (len(new_username) < 3 or len(new_username) > 150):
        errors.append('Username must be between 3 and 150 characters.')
    
    # Check username format (alphanumeric, underscore, hyphen)
    if new_username:
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', new_username):
            errors.append('Username can only contain letters, numbers, underscore, and hyphen.')
    
    # Check if new username is same as current
    if new_username and new_username == user.username:
        errors.append('New username must be different from current username.')
    
    # Check if new username already exists
    if new_username:
        if User.objects.filter(username=new_username).exclude(id=user.id).exists():
            errors.append(f'Username "{new_username}" is already taken. Please choose another.')
    
    if errors:
        context = {
            'user': user,
            'page_title': 'Change Username',
            'errors': errors,
            'new_username': new_username,
        }
        return render(request, 'change_username.html', context)
    
    # All validations passed - update username
    try:
        with transaction.atomic():
            old_username = user.username
            user.username = new_username
            user.save()
            
            # Log the username change
            log_audit(
                request,
                'USERNAME_CHANGED',
                user.company,
                f"{user.get_role_display()} changed username from '{old_username}' to '{new_username}'",
                {'old_username': old_username, 'new_username': new_username, 'email': user.email}
            )
            
            messages.success(request, f'✅ Username changed successfully! Your new username is "{new_username}".')
            return redirect('change-username')
    
    except Exception as e:
        messages.error(request, f'Error changing username: {str(e)}')
        context = {
            'user': user,
            'page_title': 'Change Username',
            'errors': [str(e)],
            'new_username': new_username,
        }
        return render(request, 'change_username.html', context)


# ==========================================
# ADMIN PROFILE/SETTINGS
# ==========================================

@admin_required
@require_http_methods(["GET"])
def admin_account_settings(request):
    """
    Admin dashboard showing account settings options.
    """
    user = request.user
    context = {
        'user': user,
        'page_title': 'Account Settings',
        'last_login': user.last_login,
        'email': user.email,
        'company': user.company,
    }
    return render(request, 'admin_account_settings.html', context)


# ==========================================
# EMPLOYEE PROFILE/SETTINGS
# ==========================================

@employee_required
@require_http_methods(["GET"])
def employee_account_settings(request):
    """
    Employee dashboard showing account settings options.
    """
    user = request.user
    context = {
        'user': user,
        'page_title': 'Account Settings',
        'last_login': user.last_login,
        'email': user.email,
        'company': user.company,
    }
    return render(request, 'employee_account_settings.html', context)


# ==========================================
# PROFILE PHOTO UPLOAD
# ==========================================

@login_required(login_url='login')
@require_http_methods(["POST"])
def upload_profile_photo(request):
    """
    Upload/update profile photo for authenticated users (Admin/Employee).
    Supports both regular form submission and AJAX requests.
    """
    user = request.user
    
    if 'profile_photo' not in request.FILES:
        error_msg = 'No photo file selected.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': error_msg})
        messages.error(request, error_msg)
        return redirect('employee-account-settings' if user.role == 'EMPLOYEE' else 'admin-account-settings')
    
    photo_file = request.FILES['profile_photo']
    
    # Validate file type
    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif'}
    file_extension = photo_file.name.split('.')[-1].lower()
    
    if file_extension not in allowed_extensions:
        error_msg = 'Only JPG, PNG, and GIF files are allowed.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': error_msg})
        messages.error(request, error_msg)
        return redirect('employee-account-settings' if user.role == 'EMPLOYEE' else 'admin-account-settings')
    
    # Validate file size (max 5MB)
    if photo_file.size > 5 * 1024 * 1024:  # 5MB
        error_msg = 'Photo size must be less than 5MB.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': error_msg})
        messages.error(request, error_msg)
        return redirect('employee-account-settings' if user.role == 'EMPLOYEE' else 'admin-account-settings')
    
    try:
        # Delete old photo if exists
        if user.profile_picture:
            user.profile_picture.delete()
        
        # Save new photo to profile_picture field (existing field in User model)
        user.profile_picture = photo_file
        user.save()
        
        # Log the action
        log_audit(
            request,
            'PROFILE_PHOTO_UPDATED',
            user.company,
            f"{user.get_role_display()} '{user.username}' updated profile photo",
            {'username': user.username, 'email': user.email}
        )
        
        # Return response based on request type
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': '✅ Profile photo updated successfully!',
                'photo_path': str(user.profile_picture),
                'photo_url': user.profile_picture.url if user.profile_picture else None
            })
        
        messages.success(request, '✅ Profile photo updated successfully!')
        return redirect('employee-account-settings' if user.role == 'EMPLOYEE' else 'admin-account-settings')
    
    except Exception as e:
        error_msg = f'Error uploading photo: {str(e)}'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': error_msg})
        messages.error(request, error_msg)
        return redirect('employee-account-settings' if user.role == 'EMPLOYEE' else 'admin-account-settings')
