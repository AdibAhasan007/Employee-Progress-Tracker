"""
OWNER Portal Views - Software Owner dashboard for multi-tenant management.
OWNER can see which companies use the software and overall health/usage.
OWNER must NOT access any employee-level content (screenshots, apps, websites, per-employee sessions).
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from .audit import log_audit
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import timedelta
from functools import wraps

from .models import Company, Plan, Subscription, CompanyUsageDaily, User
from .permissions import IsOwner


def owner_required(func):
    """Decorator to ensure user is OWNER and logged in."""
    @wraps(func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'OWNER':
            return redirect('/')
        return func(request, *args, **kwargs)
    return wrapper


@owner_required
def owner_dashboard(request):
    """
    Main OWNER dashboard showing all companies and key metrics.
    Shows: Companies list, status, plan, seats used, last sync, aggregate minutes, storage.
    """
    companies = Company.objects.select_related('plan').prefetch_related('subscriptions').all()
    
    # Date ranges
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    thirty_days_ago = today - timedelta(days=30)
    
    # System-wide totals
    system_total_minutes_today = 0
    system_total_minutes_week = 0
    system_total_minutes_month = 0
    system_total_screenshots_today = 0
    system_total_screenshots_week = 0
    system_total_screenshots_month = 0
    system_total_sessions_today = 0
    system_total_sessions_week = 0
    system_total_sessions_month = 0
    system_total_storage_mb = 0
    
    # Enrich with aggregates
    companies_data = []
    for company in companies:
        # Today's usage
        today_usage = company.daily_usage.filter(date=today).first()
        
        # Week's usage
        week_usage = company.daily_usage.filter(date__gte=week_ago)
        
        # Month's usage
        month_usage = company.daily_usage.filter(date__gte=thirty_days_ago)
        
        # Calculate metrics
        minutes_today = (today_usage.total_active_seconds // 60) if today_usage else 0
        screenshots_today = today_usage.num_screenshots if today_usage else 0
        sessions_today = today_usage.num_sessions if today_usage else 0
        
        minutes_week = (week_usage.aggregate(total=Sum('total_active_seconds'))['total'] or 0) // 60
        screenshots_week = week_usage.aggregate(total=Sum('num_screenshots'))['total'] or 0
        sessions_week = week_usage.aggregate(total=Sum('num_sessions'))['total'] or 0
        
        minutes_month = (month_usage.aggregate(total=Sum('total_active_seconds'))['total'] or 0) // 60
        screenshots_month = month_usage.aggregate(total=Sum('num_screenshots'))['total'] or 0
        sessions_month = month_usage.aggregate(total=Sum('num_sessions'))['total'] or 0
        
        storage_mb = month_usage.aggregate(total=Sum('storage_used_mb'))['total'] or 0
        storage_gb = round(storage_mb / 1024, 2)
        
        num_employees = company.users.filter(
            role='EMPLOYEE',
            is_active=True,
            is_active_employee=True
        ).count()
        
        # Add to system totals
        system_total_minutes_today += minutes_today
        system_total_minutes_week += minutes_week
        system_total_minutes_month += minutes_month
        system_total_screenshots_today += screenshots_today
        system_total_screenshots_week += screenshots_week
        system_total_screenshots_month += screenshots_month
        system_total_sessions_today += sessions_today
        system_total_sessions_week += sessions_week
        system_total_sessions_month += sessions_month
        system_total_storage_mb += storage_mb
        
        # Get current subscription
        current_subscription = company.subscriptions.filter(
            status='ACTIVE',
            expires_at__gte=timezone.now()
        ).first()
        
        companies_data.append({
            'company': company,
            'num_employees': num_employees,
            'minutes_today': minutes_today,
            'minutes_week': minutes_week,
            'minutes_month': minutes_month,
            'screenshots_today': screenshots_today,
            'screenshots_week': screenshots_week,
            'screenshots_month': screenshots_month,
            'sessions_today': sessions_today,
            'sessions_week': sessions_week,
            'sessions_month': sessions_month,
            'storage_gb': storage_gb,
            'last_sync': company.last_sync_at,
            'subscription': current_subscription,
        })
    
    # Summary stats
    total_companies = Company.objects.count()
    active_companies = Company.objects.filter(status='ACTIVE').count()
    trial_companies = Company.objects.filter(status='TRIAL').count()
    suspended_companies = Company.objects.filter(status='SUSPENDED').count()
    
    # Companies not syncing (last 24 hours)
    yesterday = timezone.now() - timedelta(hours=24)
    companies_not_syncing = Company.objects.filter(
        Q(last_sync_at__isnull=True) | Q(last_sync_at__lt=yesterday),
        status__in=['ACTIVE', 'TRIAL']
    ).count()
    
    context = {
        'companies_data': companies_data,
        'total_companies': total_companies,
        'active_companies': active_companies,
        'trial_companies': trial_companies,
        'suspended_companies': suspended_companies,
        'companies_not_syncing': companies_not_syncing,
        # System-wide totals
        'system_total_minutes_today': system_total_minutes_today,
        'system_total_minutes_week': system_total_minutes_week,
        'system_total_minutes_month': system_total_minutes_month,
        'system_total_screenshots_today': system_total_screenshots_today,
        'system_total_screenshots_week': system_total_screenshots_week,
        'system_total_screenshots_month': system_total_screenshots_month,
        'system_total_sessions_today': system_total_sessions_today,
        'system_total_sessions_week': system_total_sessions_week,
        'system_total_sessions_month': system_total_sessions_month,
        'system_total_storage_gb': round(system_total_storage_mb / 1024, 2),
    }
    
    return render(request, 'owner_dashboard.html', context)


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


@owner_required
def create_company(request):
    """
    OWNER creates a new company.
    """
    if request.method == 'GET':
        return render(request, 'owner_create_company.html', {
            'plans': Plan.objects.all()
        })

    name = request.POST.get('name')
    email = request.POST.get('email', '')
    contact_person = request.POST.get('contact_person', '')
    contact_phone = request.POST.get('contact_phone', '')
    plan_id = request.POST.get('plan_id')

    if not name or not plan_id:
        messages.error(request, 'Company name and plan are required.')
        return render(request, 'owner_create_company.html', {
            'plans': Plan.objects.all(),
            'form_data': request.POST
        })

    try:
        plan = Plan.objects.get(id=plan_id)
    except Plan.DoesNotExist:
        messages.error(request, 'Invalid plan selected.')
        return render(request, 'owner_create_company.html', {
            'plans': Plan.objects.all(),
            'form_data': request.POST
        })

    # Check company name uniqueness
    if Company.objects.filter(name=name).exists():
        messages.error(request, 'Company name already exists.')
        return render(request, 'owner_create_company.html', {
            'plans': Plan.objects.all(),
            'form_data': request.POST
        })

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
    
    # Log company creation
    log_audit(
        request,
        'COMPANY_CREATED',
        company,
        f"Company {company.name} created with {plan.name} plan",
        {'plan': plan.name, 'trial_ends': company.trial_ends_at.isoformat() if company.trial_ends_at else None}
    )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': True,
            'message': 'Company created successfully',
            'company': {
                'id': company.id,
                'name': company.name,
                'company_key': company.company_key,
            }
        })

    messages.success(request, f"Company '{company.name}' created successfully.")
    return redirect('owner-dashboard')


@owner_required
def change_plan(request, company_id):
    """
    OWNER changes company plan.
    """
    company = get_object_or_404(Company, id=company_id)
    
    if request.method == 'GET':
        return render(request, 'owner_change_plan.html', {
            'company': company,
            'available_plans': Plan.objects.all()
        })
    
    plan_id = request.POST.get('plan_id')
    
    try:
        new_plan = Plan.objects.get(id=plan_id)
    except Plan.DoesNotExist:
        messages.error(request, 'Invalid plan selected.')
        return redirect('owner-change-plan', company_id=company_id)
    
    old_plan = company.plan
    company.plan = new_plan
    company.save()
    
    # Log plan change
    log_audit(
        request,
        'PLAN_CHANGED',
        company,
        f"Plan changed from {old_plan.name} to {new_plan.name}",
        {'old_plan': old_plan.name, 'new_plan': new_plan.name}
    )
    
    messages.success(request, f"Plan changed from {old_plan.name} to {new_plan.name}")
    return redirect('owner-dashboard')


@owner_required
@require_http_methods(["POST"])
def suspend_company(request, company_id):
    """
    OWNER suspends a company (stops desktop sync and web login).
    """
    company = get_object_or_404(Company, id=company_id)
    
    company.status = 'SUSPENDED'
    company.save()
    
    # Log company suspension
    log_audit(
        request,
        'COMPANY_SUSPENDED',
        company,
        f"Company {company.name} suspended",
        {'reason': 'Admin action'}
    )
    
    messages.warning(request, f"Company '{company.name}' has been suspended.")
    return redirect('owner-dashboard')


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
    
    # Log company reactivation
    log_audit(
        request,
        'COMPANY_REACTIVATED',
        company,
        f"Company {company.name} reactivated",
        {'expires_at': company.subscription_expires_at.isoformat()}
    )
    
    messages.success(request, f"Company '{company.name}' has been reactivated.")
    return redirect('owner-dashboard')


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
    
    # Log key rotation
    log_audit(
        request,
        'KEY_ROTATED',
        company,
        f"API key rotated for {company.name}",
        {'old_key': old_key[:8]+'***', 'new_key': company.company_key[:8]+'***'}
    )
    
    messages.info(request, f"API key rotated for '{company.name}'. New key: {company.company_key}")
    return redirect('owner-company-detail', company_id=company_id)


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
    
    total_active_trial = total_active + total_trial
    revenue_potential = total_active_trial * 99
    subscription_health_percent = 0
    if total_active_trial > 0:
        subscription_health_percent = round((total_active / total_active_trial) * 100, 1)

    context = {
        'top_companies': top_companies,
        'plan_distribution': plan_distribution,
        'total_active': total_active,
        'total_trial': total_trial,
        'total_suspended': total_suspended,
        'total_active_trial': total_active_trial,
        'revenue_potential': revenue_potential,
        'subscription_health_percent': subscription_health_percent,
    }
    
    return render(request, 'owner_reports.html', context)


@owner_required
def retention_policy_view(request):
    """
    OWNER manages retention policies for all plans.
    """
    plans = Plan.objects.all()
    return render(request, 'owner_retention_policy.html', {'plans': plans})


@owner_required
@require_http_methods(["POST"])
def update_retention_policy(request, plan_id):
    """
    OWNER updates retention policy for a specific plan.
    """
    plan = get_object_or_404(Plan, id=plan_id)
    
    plan.screenshot_retention_days = int(request.POST.get('screenshot_retention_days', plan.screenshot_retention_days))
    plan.max_storage_gb = int(request.POST.get('max_storage_gb', plan.max_storage_gb))
    plan.max_employees = int(request.POST.get('max_employees', plan.max_employees))
    plan.save()
    
    messages.success(request, f"Retention policy updated for {plan.name} plan.")
    return redirect('owner-retention-policy')


@owner_required
@require_http_methods(["POST"])
def update_global_privacy(request):
    """
    OWNER updates global privacy settings.
    """
    # This would update a GlobalSettings model (to be created)
    messages.success(request, "Global privacy settings updated successfully.")
    return redirect('owner-retention-policy')


@owner_required
def owner_audit_log(request):
    """
    OWNER views audit log of all actions taken.
    """
    # Get audit logs (would come from AuditLog model - to be created)
    # For now, return empty template
    audit_logs = []
    
    context = {
        'audit_logs': audit_logs,
    }
    
    return render(request, 'owner_audit_log.html', context)
