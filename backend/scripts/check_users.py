#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracker_backend.settings')
django.setup()

from core.models import User

# Check all users
print("=" * 60)
print("ALL USERS IN SYSTEM:")
print("=" * 60)

all_users = User.objects.all()
if not all_users:
    print("❌ NO USERS FOUND IN DATABASE!")
else:
    for user in all_users:
        print(f"\n👤 Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Role: {user.role}")
        print(f"   Is Staff: {user.is_staff}")
        print(f"   Is Admin: {user.is_superuser}")

# Check admin users specifically
print("\n" + "=" * 60)
print("ADMIN/MANAGER USERS:")
print("=" * 60)

admin_users = User.objects.filter(role__in=['ADMIN', 'MANAGER'])
if not admin_users:
    print("❌ NO ADMIN USERS FOUND!")
    print("\n💡 Need to create an admin user? Run:")
    print("   python manage.py createsuperuser")
else:
    for user in admin_users:
        print(f"✅ {user.username} ({user.role})")

print("\n" + "=" * 60)
