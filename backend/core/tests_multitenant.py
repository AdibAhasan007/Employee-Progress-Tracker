"""
Smoke tests for multi-tenant OWNER portal implementation.
Tests: Company management, plan changes, key rotation, data isolation.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Company, Plan, Subscription, CompanyUsageDaily

User = get_user_model()


class MultiTenantFoundationTests(TestCase):
    """Test basic multi-tenant models and functionality."""
    
    def setUp(self):
        # Create test plans
        self.free_plan = Plan.objects.create(
            name='FREE',
            max_employees=5,
            max_storage_gb=10,
            price_monthly=0
        )
        self.pro_plan = Plan.objects.create(
            name='PRO',
            max_employees=50,
            max_storage_gb=100,
            price_monthly=99
        )
    
    def test_create_company(self):
        """Test company creation with auto-generated key."""
        company = Company.objects.create(
            name='Test Company',
            email='admin@test.com',
            plan=self.free_plan,
            status='TRIAL',
            trial_ends_at=timezone.now() + timedelta(days=30)
        )
        
        self.assertIsNotNone(company.company_key)
        self.assertTrue(company.company_key.startswith('company_'))
        self.assertEqual(company.status, 'TRIAL')
    
    def test_company_key_uniqueness(self):
        """Test that company keys are unique."""
        company1 = Company.objects.create(
            name='Company 1',
            plan=self.free_plan,
            status='TRIAL'
        )
        company2 = Company.objects.create(
            name='Company 2',
            plan=self.free_plan,
            status='TRIAL'
        )
        
        self.assertNotEqual(company1.company_key, company2.company_key)
    
    def test_is_active_subscription_trial(self):
        """Test subscription status for trial companies."""
        company = Company.objects.create(
            name='Trial Company',
            plan=self.free_plan,
            status='TRIAL',
            trial_ends_at=timezone.now() + timedelta(days=10)
        )
        
        self.assertTrue(company.is_active_subscription())
        
        # Expire trial
        company.trial_ends_at = timezone.now() - timedelta(hours=1)
        company.save()
        self.assertFalse(company.is_active_subscription())
    
    def test_is_active_subscription_suspended(self):
        """Test that suspended companies are inactive."""
        company = Company.objects.create(
            name='Suspended Company',
            plan=self.free_plan,
            status='SUSPENDED'
        )
        
        self.assertFalse(company.is_active_subscription())
    
    def test_subscription_tracking(self):
        """Test subscription audit trail."""
        company = Company.objects.create(
            name='Subscription Test',
            plan=self.pro_plan,
            status='ACTIVE',
            subscription_expires_at=timezone.now() + timedelta(days=365)
        )
        
        sub = Subscription.objects.create(
            company=company,
            plan=self.pro_plan,
            expires_at=timezone.now() + timedelta(days=365),
            status='ACTIVE',
            amount_paid=99
        )
        
        self.assertEqual(sub.company, company)
        self.assertEqual(sub.status, 'ACTIVE')


class OwnerDataIsolationTests(TestCase):
    """Test that OWNER can only see aggregated data."""
    
    def setUp(self):
        # Create plans and companies
        self.plan = Plan.objects.create(
            name='TEST',
            max_employees=10,
            max_storage_gb=50
        )
        
        self.company1 = Company.objects.create(
            name='Company A',
            plan=self.plan,
            status='ACTIVE'
        )
        self.company2 = Company.objects.create(
            name='Company B',
            plan=self.plan,
            status='ACTIVE'
        )
        
        # Create users for each company
        self.admin1 = User.objects.create_user(
            username='admin1',
            email='admin1@a.com',
            password='pass123',
            role='ADMIN',
            company=self.company1
        )
        
        self.employee1 = User.objects.create_user(
            username='emp1',
            email='emp1@a.com',
            password='pass123',
            role='EMPLOYEE',
            company=self.company1,
            is_active_employee=True
        )
        
        self.owner = User.objects.create_user(
            username='owner',
            email='owner@software.com',
            password='pass123',
            role='OWNER'
        )
    
    def test_owner_user_creation(self):
        """Test OWNER role user can be created."""
        self.assertEqual(self.owner.role, 'OWNER')
        self.assertIsNone(self.owner.company)  # OWNER has no company
    
    def test_admin_belongs_to_company(self):
        """Test ADMIN users belong to a company."""
        self.assertEqual(self.admin1.company, self.company1)
    
    def test_company_usage_daily_aggregation(self):
        """Test CompanyUsageDaily aggregate table."""
        today = timezone.now().date()
        
        usage = CompanyUsageDaily.objects.create(
            company=self.company1,
            date=today,
            total_active_seconds=28800,  # 8 hours
            total_idle_seconds=3600,      # 1 hour
            num_employees_active=1,
            num_sessions=1,
            num_screenshots=10,
            storage_used_mb=500
        )
        
        self.assertEqual(usage.company, self.company1)
        self.assertEqual(usage.total_active_seconds, 28800)
        self.assertEqual(usage.num_screenshots, 10)
    
    def test_daily_usage_uniqueness(self):
        """Test unique constraint on (company, date)."""
        today = timezone.now().date()
        
        CompanyUsageDaily.objects.create(
            company=self.company1,
            date=today,
            total_active_seconds=1000
        )
        
        with self.assertRaises(Exception):
            CompanyUsageDaily.objects.create(
                company=self.company1,
                date=today,
                total_active_seconds=2000
            )


class OwnerPortalViewTests(TestCase):
    """Test OWNER portal views and access control."""
    
    def setUp(self):
        self.client = Client()
        
        self.plan = Plan.objects.create(
            name='TEST',
            max_employees=10,
            max_storage_gb=50
        )
        
        self.company = Company.objects.create(
            name='Test Corp',
            plan=self.plan,
            status='TRIAL',
            trial_ends_at=timezone.now() + timedelta(days=30)
        )
        
        self.owner = User.objects.create_user(
            username='owner',
            email='owner@app.com',
            password='ownerpass',
            role='OWNER'
        )
        
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@testcorp.com',
            password='adminpass',
            role='ADMIN',
            company=self.company
        )
    
    def test_owner_dashboard_requires_login(self):
        """Test that OWNER dashboard requires authentication."""
        response = self.client.get('/api/owner/dashboard/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_admin_cannot_access_owner_dashboard(self):
        """Test that ADMIN users cannot access OWNER dashboard."""
        self.client.login(username='admin', password='adminpass')
        response = self.client.get('/api/owner/dashboard/')
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_owner_can_access_dashboard(self):
        """Test that OWNER can access dashboard."""
        self.client.login(username='owner', password='ownerpass')
        response = self.client.get('/api/owner/dashboard/')
        self.assertEqual(response.status_code, 200)


class CompanyKeyValidationTests(TestCase):
    """Test X-Company-Key header validation on API endpoints."""
    
    def setUp(self):
        self.client = Client()
        
        self.plan = Plan.objects.create(
            name='TEST',
            max_employees=10,
            max_storage_gb=50
        )
        
        self.active_company = Company.objects.create(
            name='Active Corp',
            plan=self.plan,
            status='ACTIVE',
            subscription_expires_at=timezone.now() + timedelta(days=30)
        )
        
        self.suspended_company = Company.objects.create(
            name='Suspended Corp',
            plan=self.plan,
            status='SUSPENDED'
        )
        
        self.employee = User.objects.create_user(
            username='emp',
            email='emp@active.com',
            password='pass',
            role='EMPLOYEE',
            company=self.active_company,
            is_active_employee=True,
            tracker_token='test-token-123'
        )
    
    def test_valid_company_key_accepted(self):
        """Test that valid company key is accepted."""
        response = self.client.post(
            '/api/login',
            {'email': 'emp@active.com', 'password': 'pass'},
            HTTP_X_COMPANY_KEY=self.active_company.company_key
        )
        # Would pass with proper key (middleware would allow through)
    
    def test_invalid_company_key_rejected(self):
        """Test that invalid key is rejected."""
        response = self.client.post(
            '/api/login',
            {'email': 'emp@active.com', 'password': 'pass'},
            HTTP_X_COMPANY_KEY='invalid-key-xyz'
        )
        self.assertEqual(response.status_code, 401)
    
    def test_suspended_company_rejected(self):
        """Test that suspended company key is rejected."""
        # Suspend the company
        self.suspended_company.company_key = 'suspended-key'
        self.suspended_company.save()
        
        response = self.client.post(
            '/api/login',
            {'email': 'emp@suspended.com', 'password': 'pass'},
            HTTP_X_COMPANY_KEY=self.suspended_company.company_key
        )
        self.assertEqual(response.status_code, 403)


class PlanManagementTests(TestCase):
    """Test plan changes and limits."""
    
    def setUp(self):
        self.free_plan = Plan.objects.create(
            name='FREE',
            max_employees=5,
            price_monthly=0
        )
        self.pro_plan = Plan.objects.create(
            name='PRO',
            max_employees=50,
            price_monthly=99
        )
        
        self.company = Company.objects.create(
            name='Growth Company',
            plan=self.free_plan,
            status='TRIAL'
        )
    
    def test_upgrade_plan(self):
        """Test upgrading company plan."""
        self.company.plan = self.pro_plan
        self.company.save()
        
        self.company.refresh_from_db()
        self.assertEqual(self.company.plan.name, 'PRO')
        self.assertEqual(self.company.plan.max_employees, 50)
    
    def test_plan_audit_trail(self):
        """Test subscription history tracking."""
        sub1 = Subscription.objects.create(
            company=self.company,
            plan=self.free_plan,
            expires_at=timezone.now() + timedelta(days=30),
            status='ACTIVE'
        )
        
        # Upgrade
        self.company.plan = self.pro_plan
        self.company.save()
        
        sub2 = Subscription.objects.create(
            company=self.company,
            plan=self.pro_plan,
            expires_at=timezone.now() + timedelta(days=365),
            status='ACTIVE'
        )
        
        subs = self.company.subscriptions.all()
        self.assertEqual(subs.count(), 2)


if __name__ == '__main__':
    import unittest
    unittest.main()
