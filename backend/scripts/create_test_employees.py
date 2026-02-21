import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracker_backend.settings')
django.setup()

from core.models import User, Company

# Get the Arts of Tech company
company = Company.objects.get(name='Arts of Tech')
print(f'Company: {company.name}')

# Create 4 sample employees
employees_data = [
    {'username': 'adib_ahasan', 'email': 'adib@artoftech.com', 'first_name': 'Adib', 'last_name': 'Ahasan Choudhury'},
    {'username': 'momtaz_moon', 'email': 'momtaz@artoftech.com', 'first_name': 'Momtaz', 'last_name': 'Moon'},
    {'username': 'tanzim_tomal', 'email': 'tanzim@artoftech.com', 'first_name': 'Tanzim', 'last_name': 'Tomal'},
    {'username': 'hafiz_uddin', 'email': 'hafiz@artoftech.com', 'first_name': 'Hafiz', 'last_name': 'Uddin'},
]

for emp_data in employees_data:
    user, created = User.objects.get_or_create(
        username=emp_data['username'],
        defaults={
            'email': emp_data['email'],
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
        print(f"✓ CREATED: {emp_data['first_name']} {emp_data['last_name']}")
    else:
        print(f"✓ EXISTS: {emp_data['first_name']} {emp_data['last_name']}")

# Show all employees in this company
emp_count = User.objects.filter(company=company, role='EMPLOYEE').count()
print(f'\nTotal Employees in Company: {emp_count}')

# Verify they appear in the dropdown query
employees = User.objects.filter(role='EMPLOYEE', company=company)
print(f'\nEmployees for dropdown: {employees.count()}')
for emp in employees:
    print(f"  - {emp.get_full_name() or emp.username} ({emp.email})")
