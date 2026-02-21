from core.models import User, WorkSession
from django.utils import timezone

u = User.objects.get(id=25)
print(f"User: {u.username}")

# Additional session IDs needed
sessions = [3, 13, 18, 19]
for sid in sessions:
    session, created = WorkSession.objects.get_or_create(
        id=sid,
        defaults={
            'employee': u,
            'company': u.company,
            'start_time': timezone.now(),
        }
    )
    if created:
        print(f"✅ Created WorkSession ID={sid}")
    else:
        print(f"⚠️ WorkSession ID={sid} exists")

print(f"\n✅ Total sessions: {WorkSession.objects.filter(employee=u).count()}")
