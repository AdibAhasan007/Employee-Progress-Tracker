import sys
sys.path.insert(0, r"d:\Employee-Progress-Tracker\backend")

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from core.models import User

# Find user with employee_id=2
print("=== Checking Users ===")
users = User.objects.all()
print(f"Total users: {users.count()}\n")

for user in users:
    print(f"ID: {user.id}")
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")
    print(f"is_active: {user.is_active}")
    print(f"is_active_employee: {user.is_active_employee}")
    print(f"is_employee: {user.is_employee}")
    print(f"is_admin: {user.is_admin}")
    print(f"is_owner: {user.is_owner}")
    print(f"tracker_token: {user.tracker_token[:20] if user.tracker_token else 'None'}...")
    print(f"Company: {user.company}")
    print("-" * 50)
