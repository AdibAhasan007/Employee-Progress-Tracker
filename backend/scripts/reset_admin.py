import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracker_backend.settings')
django.setup()

from core.models import User

def reset_admin():
    username = "admin"
    password = "admin123"
    
    try:
        # Try to get the user, or create if doesn't exist
        user, created = User.objects.get_or_create(username=username)
        
        # Set attributes
        user.set_password(password)
        user.email = "admin@example.com"
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.role = 'ADMIN'
        
        user.save()
        
        if created:
            print(f"SUCCESS: Created new user '{username}'.")
        else:
            print(f"SUCCESS: Updated existing user '{username}'.")
            
        print(f"Username: {username}")
        print(f"Password: {password}")
        print(f"Role: {user.role}")
        print("You can now log in at: http://127.0.0.1:8000/api/admin/login/")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    reset_admin()