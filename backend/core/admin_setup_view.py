"""
Admin setup view for first-time setup
Accessible only if no admin exists
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from core.models import User

@require_http_methods(["GET", "POST"])
def admin_setup_view(request):
    """
    View to create first admin user when database is empty
    """
    # Check if any admin already exists
    admin_exists = User.objects.filter(role='ADMIN').exists()
    
    if admin_exists and request.method == "GET":
        # If admin exists, redirect to login
        return redirect('admin-login-main')
    
    if request.method == "POST":
        username = request.POST.get('username', 'admin')
        email = request.POST.get('email', 'admin@yourcompany.com')
        first_name = request.POST.get('first_name', 'Administrator')
        last_name = request.POST.get('last_name', 'User')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        # Validate
        if not password or password != password2:
            return render(request, 'admin_setup.html', {
                'error': 'Passwords do not match or are empty',
                'admin_exists': admin_exists
            })
        
        if len(password) < 8:
            return render(request, 'admin_setup.html', {
                'error': 'Password must be at least 8 characters',
                'admin_exists': admin_exists
            })
        
        if User.objects.filter(username=username).exists():
            return render(request, 'admin_setup.html', {
                'error': f'Username "{username}" already exists',
                'admin_exists': admin_exists
            })
        
        # Create admin user
        admin = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        admin.role = 'ADMIN'
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()
        
        # Redirect to login
        return redirect('admin-login-main')
    
    return render(request, 'admin_setup.html', {
        'admin_exists': admin_exists
    })
