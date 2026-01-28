import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracker_backend.settings')
django.setup()

from core.models import User

def fix_admin_role():
    try:
        # Find the superuser (admin)
        admin_user = User.objects.filter(is_superuser=True).first()
        
        if admin_user:
            print(f"Found admin user: {admin_user.username}")
            admin_user.role = 'ADMIN'
            admin_user.save()
            print(f"SUCCESS: Role for '{admin_user.username}' has been updated to 'ADMIN'.")
            print("You can now log in to the dashboard.")
        else:
            print("ERROR: No superuser found. Please run 'python manage.py createsuperuser' first.")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    fix_admin_role()