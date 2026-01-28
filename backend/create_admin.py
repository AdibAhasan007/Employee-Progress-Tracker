"""
Quick Admin User Creation Script for Render
Renders এ সহজে admin user তৈরি করুন
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracker_backend.settings')
django.setup()

from core.models import User

def create_admin():
    """Create admin user"""
    
    # Check if admin already exists
    if User.objects.filter(username='admin').exists():
        admin = User.objects.get(username='admin')
        print(f"✅ Admin user already exists!")
        print(f"   Username: {admin.username}")
        print(f"   Email: {admin.email}")
        print(f"   Role: {admin.role}")
        return
    
    # Create new admin
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@yourcompany.com',
        password='Admin@123',
        first_name='Administrator',
        last_name='User'
    )
    
    # Set as ADMIN role
    admin.role = 'ADMIN'
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    
    print("✅ Admin user created successfully!")
    print(f"\n📋 Admin Details:")
    print(f"   Username: {admin.username}")
    print(f"   Email: {admin.email}")
    print(f"   Password: Admin@123")
    print(f"   Role: {admin.role}")
    print(f"\n🔗 Login URLs:")
    print(f"   Admin Panel: https://your-app.onrender.com/admin/")
    print(f"   Web Login: https://your-app.onrender.com/login/")

def create_custom_admin(username, email, password):
    """Create custom admin user"""
    
    if User.objects.filter(username=username).exists():
        print(f"❌ User '{username}' already exists!")
        return
    
    admin = User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        first_name='Administrator',
        last_name='User'
    )
    
    admin.role = 'ADMIN'
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    
    print("✅ Admin user created successfully!")
    print(f"\n📋 Admin Details:")
    print(f"   Username: {admin.username}")
    print(f"   Email: {admin.email}")
    print(f"   Password: {password}")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--custom':
        # Custom admin
        if len(sys.argv) < 5:
            print("Usage: python create_admin.py --custom <username> <email> <password>")
            sys.exit(1)
        
        username = sys.argv[2]
        email = sys.argv[3]
        password = sys.argv[4]
        create_custom_admin(username, email, password)
    else:
        # Default admin
        create_admin()
