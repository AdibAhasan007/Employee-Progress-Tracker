#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracker_backend.settings')
django.setup()

from core.models import User

print("\n" + "="*60)
print("CHECKING AYMAN ACCOUNT IN LOCAL DATABASE")
print("="*60 + "\n")

try:
    user = User.objects.get(username='ayman')
    print('✅ Ayman user EXISTS in local DB\n')
    print(f'   Username:    {user.username}')
    print(f'   Email:       {user.email}')
    print(f'   Role:        {user.role}')
    print(f'   is_active:   {user.is_active}')
    print(f'   is_staff:    {user.is_staff}')
    print(f'   is_superuser:{user.is_superuser}')
    pwd_check = user.check_password('12345')
    print(f'   Password "12345" correct: {pwd_check}\n')
    
    if not pwd_check:
        print("❌ PASSWORD IS WRONG! Resetting...")
        user.set_password('12345')
        user.save()
        print("✅ Password reset to 12345\n")
        
except User.DoesNotExist:
    print('❌ Ayman does NOT exist in database!')
    print('Creating now...\n')
    user = User.objects.create_user(
        username='ayman',
        email='ayman@gmail.com',
        password='12345',
        role='OWNER',
        first_name='Ayman'
    )
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print('✅ Ayman created with all settings correct\n')

print("="*60)
print("ACCOUNT STATUS: READY ✅")
print("="*60 + "\n")
