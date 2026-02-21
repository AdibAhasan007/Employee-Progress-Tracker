#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracker_backend.settings')
django.setup()

from core.models import User

try:
    user = User.objects.get(username='ayman')
    print('✅ User Found: ayman')
    print(f'   Email: {user.email}')
    print(f'   Role: {user.role}')
    print(f'   is_staff: {user.is_staff}')
    print(f'   is_superuser: {user.is_superuser}')
    print(f'   Password Hash: {user.password[:20]}...')
    print()
    
    result = user.check_password('12345')
    print(f'Password "12345" check: {result}')
    
    if not result:
        print()
        print('❌ Password MISMATCH!')
        print('Resetting password to 12345...')
        user.set_password('12345')
        user.save()
        print('✅ Password reset successful')
        print('Try login again: ayman / 12345')
    else:
        print('✅ Password is CORRECT')
        print('Account should work - check browser form')
        
except User.DoesNotExist:
    print('❌ User ayman does NOT exist')
    print('Creating it now...')
    user = User.objects.create_user(username='ayman', password='12345', email='ayman@gmail.com', role='OWNER', first_name='Ayman')
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print('✅ Created successfully')
