import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracker_backend.settings')
django.setup()

from core.models import User

print("=== All Users ===")
users = User.objects.all()
if users.exists():
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}, Role: {user.role}, Email: {user.email}")
else:
    print("No users found")
