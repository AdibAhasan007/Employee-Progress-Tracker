"""
Django Management Command to Create Admin User
This runs during deployment (build.sh) on Render free tier
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a default admin user if it does not exist'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='admin')
        parser.add_argument('--email', type=str, default='admin@yourcompany.com')
        parser.add_argument('--password', type=str, default='Admin@123')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.SUCCESS(f'✅ Admin user "{username}" already exists!')
            )
            return

        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name='Administrator',
                last_name='User'
            )
            
            # Set ADMIN role
            user.role = 'ADMIN'
            user.is_staff = True
            user.is_superuser = True
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Admin user "{username}" created successfully!')
            )
            self.stdout.write(f'\n📋 Admin Details:')
            self.stdout.write(f'   Username: {username}')
            self.stdout.write(f'   Email: {email}')
            self.stdout.write(f'   Password: {password}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating admin user: {e}')
            )
