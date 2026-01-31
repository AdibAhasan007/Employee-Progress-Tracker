from django.core.management.base import BaseCommand
from django.db import connection
from core.models import User, Plan
import os

class Command(BaseCommand):
    help = 'Setup OWNER account and run migrations automatically'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Starting OWNER account setup...')
        
        # Check if migration 0007 exists in database
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM django_migrations 
                    WHERE app='core' AND name='0007_add_multitenant_foundation'
                )
            """)
            migration_exists = cursor.fetchone()[0]
        
        if not migration_exists:
            self.stdout.write('❌ Migration 0007 not found. Run: python manage.py migrate')
            return
        
        # Check if Ayman already exists
        if User.objects.filter(username='ayman').exists():
            self.stdout.write(self.style.SUCCESS('✅ Ayman account already exists'))
            return
        
        # Create Ayman account
        try:
            owner = User.objects.create_user(
                username='ayman',
                password='12345',
                email='ayman@gmail.com',
                role='OWNER',
                first_name='Ayman'
            )
            owner.is_staff = True
            owner.is_superuser = True
            owner.save()
            
            self.stdout.write(self.style.SUCCESS('✅ Ayman OWNER account created!'))
            self.stdout.write(f'   Username: ayman')
            self.stdout.write(f'   Email: ayman@gmail.com')
            self.stdout.write(f'   Role: OWNER')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))
