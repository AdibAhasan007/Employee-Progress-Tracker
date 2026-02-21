import os
import django
import sys

# Add backend to path
sys.path.insert(0, 'C:\\Users\\prant\\OneDrive\\Desktop\\Tracker Modify\\backend')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracker_backend.settings')
django.setup()

from core.models import User

print("=" * 60)
print("CHECKING ADMIN USERS IN DATABASE...")
print("=" * 60)

all_users = User.objects.all()
print(f"\nTotal users: {all_users.count()}")

admin_users = User.objects.filter(role__in=['ADMIN', 'MANAGER'])
print(f"Admin/Manager users: {admin_users.count()}")

if admin_users.exists():
    print("\n✅ ADMIN USERS FOUND:")
    for user in admin_users:
        print(f"   - {user.username} ({user.role})")
else:
    print("\n❌ NO ADMIN USERS FOUND!")
    print("\nTo create an admin user, run:")
    print("   python manage.py createsuperuser")

print("\n" + "=" * 60)
