"""
Stripe Webhook Handlers for payment events.
Handles subscription updates, payment successes/failures, invoices, etc.
"""

import stripe
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings
from .models import (
    StripeBillingSubscription, StripeInvoice, Company, 
    SubscriptionTier, AlertNotification
)

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(['POST'])
def stripe_webhook_handler(request):
    """
    Handle incoming Stripe webhook events.
    
    Handles:
    - payment_intent.succeeded
    - payment_intent.payment_failed
    - invoice.payment_succeeded
    - invoice.payment_failed
    - customer.subscription.updated
    - customer.subscription.deleted
    """
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        logger.warning(f"Invalid payload: {e}")
        return JsonResponse({'status': 'invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.warning(f"Invalid signature: {e}")
        return JsonResponse({'status': 'invalid signature'}, status=400)
    
    # Route event to appropriate handler
    event_type = event['type']
    event_data = event['data']['object']
    
    try:
        if event_type == 'payment_intent.succeeded':
            handle_payment_intent_succeeded(event_data)
        
        elif event_type == 'payment_intent.payment_failed':
            handle_payment_intent_failed(event_data)
        
        elif event_type == 'invoice.payment_succeeded':
            handle_invoice_payment_succeeded(event_data)
        
        elif event_type == 'invoice.payment_failed':
            handle_invoice_payment_failed(event_data)
        
        elif event_type == 'customer.subscription.updated':
            handle_subscription_updated(event_data)
        
        elif event_type == 'customer.subscription.deleted':
            handle_subscription_deleted(event_data)
        
        logger.info(f"Handled event: {event_type}")
        
    except Exception as e:
        logger.error(f"Error handling webhook {event_type}: {str(e)}")
        return JsonResponse({'status': 'error'}, status=500)
    
    return JsonResponse({'status': 'received'}, status=200)


def handle_payment_intent_succeeded(event_data):
    """Handle successful payment intent."""
    customer_id = event_data.get('customer')
    amount = event_data.get('amount') / 100  # Convert cents to dollars
    
    try:
        subscription = StripeBillingSubscription.objects.get(
            stripe_customer_id=customer_id
        )
        company = subscription.company
        
        # Create success alert
        AlertNotification.objects.create(
            company=company,
            alert_type='PAYMENT_SUCCEEDED',
            title="Payment Successful",
            message=f"Payment of ${amount:.2f} processed successfully",
            related_data={'amount': amount}
        )
        
        logger.info(f"Payment succeeded for {company.name}: ${amount:.2f}")
    
    except StripeBillingSubscription.DoesNotExist:
        logger.warning(f"Subscription not found for customer {customer_id}")


def handle_payment_intent_failed(event_data):
    """Handle failed payment intent."""
    customer_id = event_data.get('customer')
    
    try:
        subscription = StripeBillingSubscription.objects.get(
            stripe_customer_id=customer_id
        )
        company = subscription.company
        
        # Create failure alert - CRITICAL
        AlertNotification.objects.create(
            company=company,
            alert_type='PAYMENT_FAILED',
            title="Payment Failed - Action Required",
            message="Your payment failed. Please update your payment method.",
            related_data={'stripe_customer_id': customer_id}
        )
        
        # Update subscription status
        subscription.status = 'PAST_DUE'
        subscription.save()
        
        logger.warning(f"Payment failed for {company.name}")
    
    except StripeBillingSubscription.DoesNotExist:
        logger.warning(f"Subscription not found for customer {customer_id}")


def handle_invoice_payment_succeeded(event_data):
    """Handle successful invoice payment."""
    stripe_invoice_id = event_data.get('id')
    stripe_customer_id = event_data.get('customer')
    amount_paid = event_data.get('amount_paid') / 100
    paid_at = event_data.get('status_transitions', {}).get('paid_at')
    
    try:
        invoice = StripeInvoice.objects.get(stripe_invoice_id=stripe_invoice_id)
        invoice.status = 'PAID'
        invoice.amount_paid = amount_paid
        if paid_at:
            invoice.paid_at = timezone.datetime.fromtimestamp(paid_at, tz=timezone.utc)
        invoice.save()
        
        logger.info(f"Invoice {stripe_invoice_id} marked as paid: ${amount_paid:.2f}")
    
    except StripeInvoice.DoesNotExist:
        logger.warning(f"Invoice {stripe_invoice_id} not found in database")


def handle_invoice_payment_failed(event_data):
    """Handle failed invoice payment."""
    stripe_invoice_id = event_data.get('id')
    stripe_customer_id = event_data.get('customer')
    
    try:
        subscription = StripeBillingSubscription.objects.get(
            stripe_customer_id=stripe_customer_id
        )
        company = subscription.company
        
        # Create critical alert
        AlertNotification.objects.create(
            company=company,
            alert_type='PAYMENT_FAILED',
            title="Invoice Payment Failed",
            message=f"Invoice {stripe_invoice_id} payment failed. Please update payment method.",
            related_data={'stripe_invoice_id': stripe_invoice_id}
        )
        
        logger.warning(f"Invoice payment failed: {stripe_invoice_id}")
    
    except StripeBillingSubscription.DoesNotExist:
        logger.warning(f"Subscription not found for invoice {stripe_invoice_id}")


def handle_subscription_updated(event_data):
    """Handle subscription update (tier change, date change, etc.)."""
    stripe_subscription_id = event_data.get('id')
    stripe_customer_id = event_data.get('customer')
    current_period_start = event_data.get('current_period_start')
    current_period_end = event_data.get('current_period_end')
    
    try:
        subscription = StripeBillingSubscription.objects.get(
            stripe_subscription_id=stripe_subscription_id
        )
        
        # Update period dates
        if current_period_start:
            subscription.current_period_start = timezone.datetime.fromtimestamp(
                current_period_start, tz=timezone.utc
            )
        if current_period_end:
            subscription.current_period_end = timezone.datetime.fromtimestamp(
                current_period_end, tz=timezone.utc
            )
        
        subscription.save()
        logger.info(f"Subscription {stripe_subscription_id} updated")
    
    except StripeBillingSubscription.DoesNotExist:
        logger.warning(f"Subscription {stripe_subscription_id} not found")


def handle_subscription_deleted(event_data):
    """Handle subscription cancellation."""
    stripe_subscription_id = event_data.get('id')
    stripe_customer_id = event_data.get('customer')
    
    try:
        subscription = StripeBillingSubscription.objects.get(
            stripe_subscription_id=stripe_subscription_id
        )
        company = subscription.company
        
        # Mark as cancelled
        subscription.status = 'CANCELLED'
        subscription.cancelled_at = timezone.now()
        subscription.save()
        
        # Create alert
        AlertNotification.objects.create(
            company=company,
            alert_type='SUBSCRIPTION_CANCELLED',
            title="Subscription Cancelled",
            message="Your subscription has been cancelled. Service access may be limited.",
            related_data={'stripe_subscription_id': stripe_subscription_id}
        )
        
        logger.info(f"Subscription {stripe_subscription_id} cancelled for {company.name}")
    
    except StripeBillingSubscription.DoesNotExist:
        logger.warning(f"Subscription {stripe_subscription_id} not found")


def create_stripe_customer(company, email=None):
    """
    Create a new Stripe customer for a company.
    
    Args:
        company: Company instance
        email: Billing email (optional)
    
    Returns:
        stripe_customer_id or None if error
    """
    try:
        from .models import StripeCustomer
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        customer = stripe.Customer.create(
            name=company.name,
            email=email or company.email,
            metadata={'company_id': company.id}
        )
        
        # Store in database
        StripeCustomer.objects.create(
            company=company,
            stripe_customer_id=customer.id,
            email_synced=True
        )
        
        logger.info(f"Created Stripe customer {customer.id} for {company.name}")
        return customer.id
    
    except stripe.error.StripeError as e:
        logger.error(f"Error creating Stripe customer: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error creating Stripe customer: {str(e)}")
        return None


def create_subscription(company, tier):
    """
    Create a Stripe subscription for a company.
    
    Args:
        company: Company instance
        tier: SubscriptionTier instance
    
    Returns:
        StripeBillingSubscription instance or None
    """
    try:
        from .models import StripeCustomer
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # Get or create Stripe customer
        try:
            stripe_customer = StripeCustomer.objects.get(company=company)
            stripe_customer_id = stripe_customer.stripe_customer_id
        except StripeCustomer.DoesNotExist:
            stripe_customer_id = create_stripe_customer(company)
            if not stripe_customer_id:
                return None
        
        if not tier.stripe_price_id:
            logger.error(f"Tier {tier.name} has no Stripe price ID")
            return None
        
        # Create subscription
        stripe_subscription = stripe.Subscription.create(
            customer=stripe_customer_id,
            items=[{'price': tier.stripe_price_id}],
            metadata={'company_id': company.id, 'tier': tier.tier}
        )
        
        # Store in database
        subscription = StripeBillingSubscription.objects.create(
            company=company,
            tier=tier,
            stripe_subscription_id=stripe_subscription.id,
            stripe_customer_id=stripe_customer_id,
            status='ACTIVE',
            current_period_start=timezone.datetime.fromtimestamp(
                stripe_subscription.current_period_start, tz=timezone.utc
            ),
            current_period_end=timezone.datetime.fromtimestamp(
                stripe_subscription.current_period_end, tz=timezone.utc
            ),
        )
        
        logger.info(f"Created subscription for {company.name}: {tier.name}")
        return subscription
    
    except stripe.error.StripeError as e:
        logger.error(f"Error creating Stripe subscription: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error creating subscription: {str(e)}")
        return None
