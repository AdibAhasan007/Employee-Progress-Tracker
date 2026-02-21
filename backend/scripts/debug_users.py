import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracker_backend.settings')
django.setup()

from core.models import User, Company

# Show all companies
print('=== ALL COMPANIES ===')
for c in Company.objects.all():
    print(f'ID: {c.id} | Name: {c.name}')

print('\n=== ALL USERS ===')
for u in User.objects.all():
    company_name = u.company.name if u.company else 'NO COMPANY'
    print(f'{u.username} | {u.email} | Role: {u.role} | Company: {company_name} (ID: {u.company_id})')

# Find admin user
print('\n=== ADMIN USER ===')
admin = User.objects.filter(username='arts@gmail.com').first()
if admin:
    print(f'Username: {admin.username}')
    print(f'Role: {admin.role}')
    company_name = admin.company.name if admin.company else 'None'
    print(f'Company: {company_name} (ID: {admin.company_id})')
    
    # Count employees in admin's company
    if admin.company:
        emp_count = User.objects.filter(company=admin.company, role='EMPLOYEE').count()
        print(f'\nEmployees in {admin.company.name}: {emp_count}')
        
        for emp in User.objects.filter(company=admin.company, role='EMPLOYEE'):
            print(f'  - {emp.get_full_name() or emp.username} ({emp.email})')
