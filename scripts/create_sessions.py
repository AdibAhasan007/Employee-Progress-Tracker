import sys
sys.path.insert(0, r"d:\Employee-Progress-Tracker\backend")

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from core.models import User, WorkSession, Company
from django.utils import timezone

# Get employee
user = User.objects.get(id=25)
print(f"User: {user.username}")
print(f"Company: {user.company}")

# Create work sessions for screenshots (session IDs: 1, 2, 4, 5 from local DB)
session_ids = [1, 2, 4, 5]

for sess_id in session_ids:
    session, created = WorkSession.objects.get_or_create(
        id=sess_id,
        defaults={
            'employee': user,
            'company': user.company,
            'started_at': timezone.now(),
            'ended_at': None,
        }
    )
    if created:
        print(f"✅ Created WorkSession ID={sess_id}")
    else:
        print(f"⚠️ WorkSession ID={sess_id} already exists")
        # Update employee if different
        if session.employee_id != user.id:
            session.employee = user
            session.company = user.company
            session.save()
            print(f"   Updated employee to ID={user.id}")

print(f"\n✅ Total sessions for employee 25: {WorkSession.objects.filter(employee=user).count()}")
