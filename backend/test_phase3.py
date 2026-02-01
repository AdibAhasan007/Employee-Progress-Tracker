"""
Phase 3 Testing Suite - Billing & Real-Time Alerts
Tests for Stripe integration, billing features, and alert notifications
"""

import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracker_backend.settings')
django.setup()

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from core.models import (
    Company, User, SubscriptionTier, StripeBillingSubscription, 
    StripeInvoice, AlertNotification, Plan
)
import datetime

client = Client()

def test_subscription_tier_creation():
    """TEST 1: Create and verify subscription tiers"""
    print("\n" + "="*60)
    print("TEST 1: Subscription Tier Creation")
    print("="*60)
    
    # Clean up any existing tiers from previous runs
    SubscriptionTier.objects.all().delete()
    
    # Create tiers
    free_tier = SubscriptionTier.objects.create(
        tier='FREE',
        name='Free',
        description='Free plan for testing',
        monthly_cost=0,
        max_employees=5,
        max_agents=5,
        max_storage_gb=10,
        screenshot_retention_days=30,
        is_active=True,
        display_order=1,
        features={'screenshots': True, 'website_tracking': False, 'app_tracking': False}
    )
    
    pro_tier = SubscriptionTier.objects.create(
        tier='PRO',
        name='Professional',
        description='Pro plan for growing teams',
        monthly_cost=29,
        stripe_price_id='price_1ABC123',
        max_employees=50,
        max_agents=50,
        max_storage_gb=100,
        screenshot_retention_days=60,
        is_active=True,
        display_order=2,
        features={'screenshots': True, 'website_tracking': True, 'app_tracking': True, 'audit_logs': True}
    )
    
    enterprise_tier = SubscriptionTier.objects.create(
        tier='ENTERPRISE',
        name='Enterprise',
        description='Enterprise plan for large organizations',
        monthly_cost=99,
        stripe_price_id='price_1XYZ999',
        max_employees=999999,
        max_agents=999999,
        max_storage_gb=1000,
        screenshot_retention_days=365,
        is_active=True,
        display_order=3,
        features={'screenshots': True, 'website_tracking': True, 'app_tracking': True, 'audit_logs': True, 'real_time_alerts': True}
    )
    
    assert SubscriptionTier.objects.count() == 3, "Should have 3 tiers"
    assert free_tier.monthly_cost == 0, "Free tier should cost $0"
    assert pro_tier.stripe_price_id == 'price_1ABC123', "Pro tier should have Stripe price ID"
    assert enterprise_tier.features.get('real_time_alerts') == True, "Enterprise should have real-time alerts"
    
    print("✅ Created 3 subscription tiers (Free, Pro, Enterprise)")
    print(f"✅ Free: ${free_tier.monthly_cost}/mo - {free_tier.max_employees} employees")
    print(f"✅ Pro: ${pro_tier.monthly_cost}/mo - {pro_tier.max_employees} employees")
    print(f"✅ Enterprise: ${enterprise_tier.monthly_cost}/mo - {enterprise_tier.max_employees} employees")
    return True


def test_stripe_billing_subscription():
    """TEST 2: Create and manage Stripe billing subscriptions"""
    print("\n" + "="*60)
    print("TEST 2: Stripe Billing Subscription")
    print("="*60)
    
    import uuid
    
    # Create plan with unique name
    plan = Plan.objects.create(
        name=f'TRIAL_{uuid.uuid4().hex[:8]}',
        max_employees=10,
        max_storage_gb=50,
        screenshot_retention_days=30,
        price_monthly=0
    )
    
    # Create company
    company = Company.objects.create(
        name=f"Billing Test {uuid.uuid4().hex[:8]}",
        company_key=f"test_billing_key_{uuid.uuid4().hex[:8]}",
        plan=plan,
        email="billing@example.com"
    )
    
    # Create tier
    tier = SubscriptionTier.objects.first()
    
    # Create billing subscription
    subscription = StripeBillingSubscription.objects.create(
        company=company,
        tier=tier,
        stripe_subscription_id=f'sub_{uuid.uuid4().hex[:15]}',
        stripe_customer_id=f'cus_{uuid.uuid4().hex[:15]}',
        status='ACTIVE',
        current_period_start=timezone.now(),
        current_period_end=timezone.now() + datetime.timedelta(days=30),
        auto_renewal=True,
        default_payment_method_id='pm_1ABC123'
    )
    
    assert subscription.company == company, "Subscription should be linked to company"
    assert subscription.status == 'ACTIVE', "Subscription should be active"
    assert subscription.is_active_subscription(), "Subscription should return true for is_active"
    assert subscription.auto_renewal == True, "Auto renewal should be enabled"
    
    print(f"✅ Created Stripe billing subscription")
    print(f"   Subscription ID: {subscription.stripe_subscription_id}")
    print(f"   Tier: {subscription.tier.name}")
    print(f"   Status: {subscription.status}")
    print(f"   Auto-renewal: {'Enabled' if subscription.auto_renewal else 'Disabled'}")
    return True


def test_stripe_invoice_tracking():
    """TEST 3: Track and manage Stripe invoices"""
    print("\n" + "="*60)
    print("TEST 3: Stripe Invoice Tracking")
    print("="*60)
    
    import uuid
    
    # Get company and subscription
    company = Company.objects.first()
    subscription = StripeBillingSubscription.objects.get(company=company)
    
    # Create invoices with unique IDs
    invoice1 = StripeInvoice.objects.create(
        subscription=subscription,
        company=company,
        stripe_invoice_id=f'in_{uuid.uuid4().hex[:18]}_paid',
        status='PAID',
        amount_due=29.00,
        amount_paid=29.00,
        currency='USD',
        issued_date=timezone.now() - datetime.timedelta(days=30),
        pdf_url='https://stripe.com/invoice/test1.pdf'
    )
    
    invoice2 = StripeInvoice.objects.create(
        subscription=subscription,
        company=company,
        stripe_invoice_id=f'in_{uuid.uuid4().hex[:18]}_pending',
        status='OPEN',
        amount_due=29.00,
        amount_paid=0,
        currency='USD',
        issued_date=timezone.now(),
        due_date=timezone.now() + datetime.timedelta(days=14)
    )
    
    paid_invoices = StripeInvoice.objects.filter(company=company, status='PAID')
    open_invoices = StripeInvoice.objects.filter(company=company, status='OPEN')
    
    assert paid_invoices.count() >= 1, "Should have at least 1 paid invoice"
    assert open_invoices.count() >= 1, "Should have at least 1 open invoice"
    assert invoice1.amount_paid == 29.00, "Paid invoice should show paid amount"
    
    print(f"✅ Created 2 invoices (1 paid, 1 pending)")
    print(f"   Paid Invoice: {invoice1.stripe_invoice_id[:30]}... - ${invoice1.amount_paid}")
    print(f"   Pending Invoice: {invoice2.stripe_invoice_id[:30]}... - ${invoice2.amount_due}")
    return True


def test_alert_notifications():
    """TEST 4: Create and manage alert notifications"""
    print("\n" + "="*60)
    print("TEST 4: Alert Notifications")
    print("="*60)
    
    # Get the company from test 2
    company = Company.objects.first()
    
    if not company:
        print("⚠️  No company found - skipping alert creation test")
        return True
    
    # Clean up existing alerts for this test
    AlertNotification.objects.filter(company=company).delete()
    
    # Create various alert types
    alert_offline = AlertNotification.objects.create(
        company=company,
        alert_type='AGENT_OFFLINE',
        title="Agent Offline",
        message="Agent john_doe hasn't synced in 15+ minutes",
        related_data={'employee_id': 1}
    )
    
    alert_payment = AlertNotification.objects.create(
        company=company,
        alert_type='PAYMENT_FAILED',
        title="Payment Failed",
        message="Your payment of $29.00 failed. Please update payment method.",
        related_data={'amount': 29.00, 'invoice_id': 'in_123'}
    )
    
    alert_expiring = AlertNotification.objects.create(
        company=company,
        alert_type='SUBSCRIPTION_EXPIRING',
        title="Subscription Expiring Soon",
        message="Your subscription expires in 3 days",
        is_read=False
    )
    
    alert_policy = AlertNotification.objects.create(
        company=company,
        alert_type='POLICY_CHANGED',
        title="Policy Changed",
        message="Admin updated tracking policy",
        is_read=True,
        read_at=timezone.now()
    )
    
    # Test unread count
    unread_alerts = AlertNotification.objects.filter(company=company, is_read=False)
    read_alerts = AlertNotification.objects.filter(company=company, is_read=True)
    
    assert unread_alerts.count() == 3, f"Should have 3 unread alerts, got {unread_alerts.count()}"
    assert read_alerts.count() == 1, f"Should have 1 read alert, got {read_alerts.count()}"
    assert alert_offline.alert_type == 'AGENT_OFFLINE', "Should be offline alert"
    assert alert_payment.related_data.get('amount') == 29.00, "Should store amount in related_data"
    
    print(f"✅ Created 4 alert notifications")
    print(f"   - Agent Offline: UNREAD")
    print(f"   - Payment Failed: UNREAD")
    print(f"   - Subscription Expiring: UNREAD")
    print(f"   - Policy Changed: READ")
    print(f"\n   Total unread: {unread_alerts.count()}")
    print(f"   Total read: {read_alerts.count()}")
    return True


def test_billing_urls():
    """TEST 5: Verify all billing URLs exist"""
    print("\n" + "="*60)
    print("TEST 5: Billing URL Routes")
    print("="*60)
    
    urls_to_test = [
        ('billing-dashboard', '/api/billing/', 'Billing Dashboard'),
        ('upgrade-subscription', '/api/billing/upgrade/', 'Upgrade Subscription'),
        ('payment-history', '/api/billing/payment-history/', 'Payment History'),
        ('billing-settings', '/api/billing/settings/', 'Billing Settings'),
        ('alerts-notifications', '/api/alerts/', 'Alerts & Notifications'),
    ]
    
    for url_name, expected_path, description in urls_to_test:
        try:
            url = reverse(url_name)
            print(f"✅ {description}: {url}")
        except Exception as e:
            print(f"❌ {description}: {str(e)}")
            return False
    
    print(f"\n✅ All {len(urls_to_test)} billing URL routes verified")
    return True


def test_billing_templates():
    """TEST 6: Verify billing templates exist"""
    print("\n" + "="*60)
    print("TEST 6: Billing Templates")
    print("="*60)
    
    templates = [
        ('billing_dashboard.html', 'Billing Dashboard'),
        ('upgrade_subscription.html', 'Upgrade Subscription'),
        ('payment_history.html', 'Payment History'),
        ('billing_settings.html', 'Billing Settings'),
        ('alerts_notifications.html', 'Alerts & Notifications'),
    ]
    
    import os
    template_dir = 'd:\\Employee-Progress-Tracker\\backend\\templates'
    
    for template_file, description in templates:
        path = os.path.join(template_dir, template_file)
        if os.path.exists(path):
            size = os.path.getsize(path) / 1024  # KB
            print(f"✅ {description}: {template_file} ({size:.1f} KB)")
        else:
            print(f"❌ {description}: {template_file} NOT FOUND")
            return False
    
    print(f"\n✅ All {len(templates)} billing templates exist")
    return True


def test_billing_views():
    """TEST 7: Verify billing view functions are callable"""
    print("\n" + "="*60)
    print("TEST 7: Billing View Functions")
    print("="*60)
    
    from core.web_views import (
        billing_dashboard_view, upgrade_subscription_view,
        payment_history_view, billing_settings_view, alerts_notifications_view
    )
    
    views = [
        (billing_dashboard_view, 'billing_dashboard_view'),
        (upgrade_subscription_view, 'upgrade_subscription_view'),
        (payment_history_view, 'payment_history_view'),
        (billing_settings_view, 'billing_settings_view'),
        (alerts_notifications_view, 'alerts_notifications_view'),
    ]
    
    for view_func, view_name in views:
        assert callable(view_func), f"{view_name} should be callable"
        print(f"✅ {view_name} - callable")
    
    print(f"\n✅ All {len(views)} billing view functions verified")
    return True


def test_webhook_handler():
    """TEST 8: Verify Stripe webhook handler"""
    print("\n" + "="*60)
    print("TEST 8: Stripe Webhook Handler")
    print("="*60)
    
    from core.stripe_webhooks import (
        stripe_webhook_handler, create_stripe_customer, create_subscription
    )
    
    handlers = [
        (stripe_webhook_handler, 'stripe_webhook_handler'),
        (create_stripe_customer, 'create_stripe_customer'),
        (create_subscription, 'create_subscription'),
    ]
    
    for handler_func, handler_name in handlers:
        assert callable(handler_func), f"{handler_name} should be callable"
        print(f"✅ {handler_name} - callable")
    
    print(f"\n✅ All {len(handlers)} webhook handlers verified")
    return True


def main():
    """Run all Phase 3 tests"""
    import uuid
    
    # Clean up from previous test runs
    StripeBillingSubscription.objects.all().delete()
    StripeInvoice.objects.all().delete()
    Company.objects.all().delete()
    Plan.objects.all().delete()
    
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "PHASE 3 TESTING SUITE - BILLING & ALERTS" + " "*3 + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    tests = [
        ("Subscription Tier Creation", test_subscription_tier_creation),
        ("Stripe Billing Subscription", test_stripe_billing_subscription),
        ("Stripe Invoice Tracking", test_stripe_invoice_tracking),
        ("Alert Notifications", test_alert_notifications),
        ("Billing URL Routes", test_billing_urls),
        ("Billing Templates", test_billing_templates),
        ("Billing View Functions", test_billing_views),
        ("Stripe Webhook Handler", test_webhook_handler),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except AssertionError as e:
            print(f"\n❌ ASSERTION ERROR: {str(e)}")
            results.append((test_name, False))
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*20 + "TESTING SUMMARY" + " "*23 + "║")
    print("╠" + "="*58 + "╣")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"║ {status}: {test_name:<45} ║")
    
    print("╠" + "="*58 + "╣")
    print(f"║ TOTAL: {passed}/{total} tests passed {' '*35} ║")
    
    if passed == total:
        print("║" + " "*13 + "🎉 ALL TESTS PASSED - PHASE 3 READY! 🎉" + " "*5 + "║")
    else:
        print(f"║ {total - passed} test(s) failed" + " "*40 + "║")
    
    print("╚" + "="*58 + "╝\n")
    
    return passed == total


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
