from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import User, Plan, Company, Subscription

class Command(BaseCommand):
    help = 'Initialize OWNER account and test company on first run'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n🚀 Running OWNER initialization...\n'))
        
        # 1. Create or verify OWNER user
        owner, created = User.objects.get_or_create(
            username='ayman',
            defaults={
                'email': 'ayman@gmail.com',
                'first_name': 'Ayman',
                'role': 'OWNER',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )
        
        # Always set password to ensure it's correct
        owner.set_password('12345')
        owner.save()
        
        if created:
            self.stdout.write(self.style.SUCCESS('✅ Created OWNER user: ayman'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ OWNER user already exists: ayman'))
        
        # 2. Create default plans if they don't exist
        plans = ['FREE', 'PRO', 'ENTERPRISE']
        for plan_name in plans:
            plan, created = Plan.objects.get_or_create(
                name=plan_name,
                defaults={
                    'max_employees': 5 if plan_name == 'FREE' else 50 if plan_name == 'PRO' else 999,
                    'max_storage_gb': 10 if plan_name == 'FREE' else 100 if plan_name == 'PRO' else 1000,
                }
            )
            if created:
                self.stdout.write(f'  ✅ Created plan: {plan_name}')
        
        # 3. Create test company if none exist
        if not Company.objects.exists():
            free_plan = Plan.objects.get(name='FREE')
            test_company = Company.objects.create(
                name='Test Company',
                plan=free_plan,
                status='TRIAL',
            )
            
            Subscription.objects.create(
                company=test_company,
                plan=free_plan,
                starts_at=timezone.now(),
                expires_at=timezone.now() + timedelta(days=30),
            )
            
            self.stdout.write(self.style.SUCCESS(f'✅ Created test company: Test Company'))
            self.stdout.write(f'  Company Key: {test_company.company_key}')
        else:
            self.stdout.write(f'✅ Companies already exist ({Company.objects.count()} total)')
        
        self.stdout.write(self.style.SUCCESS('\n✅ OWNER initialization complete!\n'))
        self.stdout.write('Login at: /admin/login/')
        self.stdout.write('Username: ayman')
        self.stdout.write('Password: 12345\n')
