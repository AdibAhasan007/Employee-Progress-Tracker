from core.models import User, WorkSession
from django.utils import timezone

u = User.objects.get(id=25)
print(f"User: {u.username}")

sessions = [1, 2, 4, 5]
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
        if session.employee_id != u.id:
            session.employee = u
            session.company = u.company
            session.save()
            print(f"   Updated to employee {u.id}")

print(f"\n✅ Total sessions: {WorkSession.objects.filter(employee=u).count()}")
