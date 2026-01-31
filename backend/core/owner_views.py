"""
OWNER Portal Views - Software Owner dashboard for multi-tenant management.
OWNER can see which companies use the software and overall health/usage.
OWNER must NOT access any employee-level content (screenshots, apps, websites, per-employee sessions).
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import timedelta

from .models import Company, Plan, Subscription, CompanyUsageDaily, User
from .permissions import IsOwner


@login_required
def owner_required(func):
    """Decorator to ensure user is OWNER."""
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'OWNER':
            return redirect('/')
        return func(request, *args, **kwargs)
    return wrapper


@login_required
@owner_required
def owner_dashboard(request):
    """
    Main OWNER dashboard showing all companies and key metrics.
    Shows: Companies list, status, plan, seats used, last sync, aggregate minutes, storage.
    """
    companies = Company.objects.select_related('plan').prefetch_related('subscriptions').all()
    
    # Enrich with aggregates
    companies_data = []
    for company in companies:
        # Get last 30 days usage
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        daily_usage = company.daily_usage.filter(date__gte=thirty_days_ago)
        
        total_minutes = daily_usage.aggregate(
            total=Sum('total_active_seconds')
        )['total'] or 0
        total_minutes = total_minutes // 60
        
        total_screenshots = daily_usage.aggregate(
            total=Sum('num_screenshots')
        )['total'] or 0
        
        storage_mb = daily_usage.aggregate(
            total=Sum('storage_used_mb')
        )['total'] or 0
        storage_gb = round(storage_mb / 1024, 2)
        
        num_employees = company.users.filter(
            role='EMPLOYEE',
            is_active=True,
            is_active_employee=True
        ).count()
        
        companies_data.append({
            'company': company,
            'num_employees': num_employees,
            'total_minutes_30d': total_minutes,
            'num_screenshots_30d': total_screenshots,
            'storage_gb': storage_gb,
            'last_sync': company.last_sync_at,
        })
    
    # Summary stats
    total_companies = Company.objects.count()
    active_companies = Company.objects.filter(status='ACTIVE').count()
    trial_companies = Company.objects.filter(status='TRIAL').count()
    
    context = {
        'companies_data': companies_data,
        'total_companies': total_companies,
        'active_companies': active_companies,
        'trial_companies': trial_companies,
    }
    
    return render(request, 'owner_dashboard.html', context)


@login_required
@owner_required
def company_detail(request, company_id):
    """
    OWNER view for a specific company.
    Shows detailed metrics and actions (suspend, change plan, rotate key).
    """
    company = get_object_or_404(Company, id=company_id)
    
    # Get last 90 days usage
    ninety_days_ago = timezone.now().date() - timedelta(days=90)
    daily_usage = company.daily_usage.filter(
        date__gte=ninety_days_ago
    ).order_by('-date')
    
    # Aggregates
    total_active_seconds = daily_usage.aggregate(
        total=Sum('total_active_seconds')
    )['total'] or 0
    
    num_employees = company.users.filter(
        role='EMPLOYEE',
        is_active=True,
        is_active_employee=True
    ).count()
    
    num_sessions = daily_usage.aggregate(
        total=Sum('num_sessions')
    )['total'] or 0
    
    num_screenshots = daily_usage.aggregate(
        total=Sum('num_screenshots')
    )['total'] or 0
    
    storage_mb = daily_usage.aggregate(
        total=Sum('storage_used_mb')
    )['total'] or 0
    
    # Get current subscription
    current_subscription = company.subscriptions.filter(
        status='ACTIVE',
        expires_at__gte=timezone.now()
    ).first()
    
    context = {
        'company': company,
        'daily_usage': daily_usage,
        'num_employees': num_employees,
        'total_active_seconds': total_active_seconds,
        'num_sessions': num_sessions,
        'num_screenshots': num_screenshots,
        'storage_mb': storage_mb,
        'current_subscription': current_subscription,
        'available_plans': Plan.objects.all(),
    }
    
    return render(request, 'owner_company_detail.html', context)


@login_required
@owner_required
@require_http_methods(["POST"])
def create_company(request):
    """
    OWNER creates a new company.
    """
    from django import forms
    
    name = request.POST.get('name')
    email = request.POST.get('email', '')
    contact_person = request.POST.get('contact_person', '')
    contact_phone = request.POST.get('contact_phone', '')
    plan_id = request.POST.get('plan_id')
    
    try:
        plan = Plan.objects.get(id=plan_id)
    except Plan.DoesNotExist:
        return JsonResponse({'status': False, 'message': 'Invalid plan'}, status=400)
    
    # Check company name uniqueness
    if Company.objects.filter(name=name).exists():
        return JsonResponse({'status': False, 'message': 'Company name already exists'}, status=400)
    
    # Create company with TRIAL status
    company = Company.objects.create(
        name=name,
        email=email,
        contact_person=contact_person,
        contact_phone=contact_phone,
        plan=plan,
        status='TRIAL',
        trial_ends_at=timezone.now() + timedelta(days=30),
    )
    
    # Log subscription creation
    Subscription.objects.create(
        company=company,
        plan=plan,
        expires_at=company.trial_ends_at,
        status='ACTIVE',
    )
    
    return JsonResponse({
        'status': True,
        'message': 'Company created successfully',
        'company': {
            'id': company.id,
            'name': company.name,
            'company_key': company.company_key,
        }
    })


@login_required
@owner_required
@require_http_methods(["POST"])
def change_plan(request, company_id):
    """
    OWNER changes company plan.
    """
    company = get_object_or_404(Company, id=company_id)
    plan_id = request.POST.get('plan_id')
    
    try:
        new_plan = Plan.objects.get(id=plan_id)
    except Plan.DoesNotExist:
        return JsonResponse({'status': False, 'message': 'Invalid plan'}, status=400)
    
    old_plan = company.plan
    company.plan = new_plan
    company.save()
    
    return JsonResponse({
        'status': True,
        'message': f'Plan changed from {old_plan.name} to {new_plan.name}',
        'plan': new_plan.name,
    })


@login_required
@owner_required
@require_http_methods(["POST"])
def suspend_company(request, company_id):
    """
    OWNER suspends a company (stops desktop sync and web login).
    """
    company = get_object_or_404(Company, id=company_id)
    
    company.status = 'SUSPENDED'
    company.save()
    
    return JsonResponse({
        'status': True,
        'message': f'Company {company.name} suspended',
    })


@login_required
@owner_required
@require_http_methods(["POST"])
def reactivate_company(request, company_id):
    """
    OWNER reactivates a suspended company.
    """
    company = get_object_or_404(Company, id=company_id)
    
    company.status = 'ACTIVE'
    company.subscription_expires_at = timezone.now() + timedelta(days=30)
    company.save()
    
    return JsonResponse({
        'status': True,
        'message': f'Company {company.name} reactivated',
    })


@login_required
@owner_required
@require_http_methods(["POST"])
def rotate_company_key(request, company_id):
    """
    OWNER rotates the company_key (for security).
    """
    import secrets
    
    company = get_object_or_404(Company, id=company_id)
    
    old_key = company.company_key
    company.company_key = f"company_{secrets.token_hex(16)}"
    company.save()
    
    return JsonResponse({
        'status': True,
        'message': 'Company key rotated',
        'new_key': company.company_key,
        'old_key': old_key,
    })


@login_required
@owner_required
def owner_reports(request):
    """
    OWNER analytics: Top companies by usage, plan distribution, growth trends.
    """
    # Top 10 companies by usage
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    
    top_companies = []
    for company in Company.objects.all():
        total_minutes = company.daily_usage.filter(
            date__gte=thirty_days_ago
        ).aggregate(
            total=Sum('total_active_seconds')
        )['total'] or 0
        
        if total_minutes > 0:
            top_companies.append({
                'company': company,
                'minutes': total_minutes // 60,
            })
    
    top_companies.sort(key=lambda x: x['minutes'], reverse=True)
    top_companies = top_companies[:10]
    
    # Plan distribution
    plan_distribution = Plan.objects.annotate(
        num_companies=Count('company')
    ).order_by('-num_companies')
    
    # Subscription status
    total_active = Company.objects.filter(status='ACTIVE').count()
    total_trial = Company.objects.filter(status='TRIAL').count()
    total_suspended = Company.objects.filter(status='SUSPENDED').count()
    
    context = {
        'top_companies': top_companies,
        'plan_distribution': plan_distribution,
        'total_active': total_active,
        'total_trial': total_trial,
        'total_suspended': total_suspended,
    }
    
    return render(request, 'owner_reports.html', context)
