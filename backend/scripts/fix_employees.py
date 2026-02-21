import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracker_backend.settings')
django.setup()

from core.models import User, Company

# Get the Arts of Tech company
company = Company.objects.get(id=9, name='Arts of Tech')
print(f'Company: {company.name} (ID: {company.id})')

# FIX 1: Update existing employee to have company
existing_emp = User.objects.filter(username='adib@gmail.com', role='EMPLOYEE').first()
if existing_emp:
    existing_emp.company = company
    existing_emp.first_name = 'Adib'
    existing_emp.last_name = 'Ahasan'
    existing_emp.save()
    print(f'✓ UPDATED: {existing_emp.username} - Added to company')

# FIX 2: Create additional employees
employees_data = [
    {'username': 'momtaz.moon', 'email': 'momtaz@artoftech.com', 'first_name': 'Momtaz', 'last_name': 'Moon'},
    {'username': 'tanzim.tomal', 'email': 'tanzim@artoftech.com', 'first_name': 'Tanzim', 'last_name': 'Tomal'},
    {'username': 'hafiz.uddin', 'email': 'hafiz@artoftech.com', 'first_name': 'Hafiz', 'last_name': 'Uddin'},
]

for emp_data in employees_data:
    user, created = User.objects.get_or_create(
        email=emp_data['email'],
        defaults={
            'username': emp_data['username'],
            'first_name': emp_data['first_name'],
            'last_name': emp_data['last_name'],
            'company': company,
            'role': 'EMPLOYEE',
            'is_active': True
        }
    )
    if created:
        user.set_password('Password@123')
        user.save()
        print(f'✓ CREATED: {emp_data["first_name"]} {emp_data["last_name"]} ({emp_data["email"]})')
    else:
        # Update existing to ensure company is set
        user.company = company
        user.role = 'EMPLOYEE'
        user.save()
        print(f'✓ UPDATED: {emp_data["first_name"]} {emp_data["last_name"]} ({emp_data["email"]})')

# VERIFY
print('\n=== VERIFICATION ===')
emp_count = User.objects.filter(company=company, role='EMPLOYEE').count()
print(f'Total Employees in {company.name}: {emp_count}')

for emp in User.objects.filter(company=company, role='EMPLOYEE'):
    print(f'  ✓ {emp.get_full_name() or emp.username} ({emp.email}) - Company ID: {emp.company_id}')
