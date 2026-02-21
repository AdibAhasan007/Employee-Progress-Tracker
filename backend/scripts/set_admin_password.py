import os
import django
import sys

sys.path.insert(0, 'C:\\Users\\prant\\OneDrive\\Desktop\\Tracker Modify\\backend')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracker_backend.settings')
django.setup()

from core.models import User

# Set admin password
admin = User.objects.get(username='admin@gmail.com')
admin.set_password('Admin@12345')  # Strong password: Capital letter, number, special char, 8+ chars
admin.save()

print("✅ Admin password updated!")
print(f"Username: admin@gmail.com")
print(f"Password: Admin@12345")
print("\nYou can now login to the admin panel.")
