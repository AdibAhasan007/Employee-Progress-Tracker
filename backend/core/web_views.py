# --- API endpoint for dynamic session active/idle time ---
from django.http import JsonResponse

def session_active_time_api(request, session_id):
    session = get_object_or_404(WorkSession, id=session_id)
    if session.end_time is None:
        now = timezone.now()
        duration = int((now - session.start_time).total_seconds())
        active_sec = ActivityLog.objects.filter(work_session=session, minute_type='ACTIVE').aggregate(total=Sum('duration_seconds'))['total'] or 0
        idle_sec = max(0, duration - active_sec)
        active_time = active_sec
        idle_time = idle_sec
    else:
        active_time = session.active_seconds
        idle_time = session.idle_seconds

    def format_time(seconds):
        h = seconds // 3600; m = (seconds % 3600) // 60; s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    return JsonResponse({
        'active_time': active_time,
        'idle_time': idle_time,
        'active_time_fmt': format_time(active_time),
        'idle_time_fmt': format_time(idle_time)
    })
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Count, Q, Min, Max, OuterRef, Subquery
from django.contrib import messages
from django.core.paginator import Paginator
from datetime import timedelta, datetime
from .models import User, WorkSession, Screenshot, ApplicationUsage, WebsiteUsage, Task, CompanySettings, ActivityLog
from django.contrib.auth import update_session_auth_hash, logout, login, authenticate
from django.contrib.auth.forms import AuthenticationForm
import pytz
import json

# ==================== TIMEZONE UTILITY ====================
def get_user_timezone(user):
    """Get user's timezone object, default to UTC"""
    try:
        if user.timezone:
            return pytz.timezone(user.timezone)
    except:
        pass
    return pytz.UTC

def convert_to_user_tz(dt, user):
    """Convert datetime to user's timezone"""
    if not dt:
        return dt
    if dt.tzinfo is None:
        dt = timezone.make_aware(dt, pytz.UTC)
    user_tz = get_user_timezone(user)
    return dt.astimezone(user_tz)

def get_today_in_user_tz(user):
    """Get today's date in user's timezone"""
    user_tz = get_user_timezone(user)
    now = timezone.now().astimezone(user_tz)
    return now.date()

# ==================== END TIMEZONE UTILITY ====================

# ==========================
# DASHBOARD
# ==========================

@login_required
def dashboard_view(request):
    """
    Landing page that redirects to the specific dashboard based on role.
    """
    if request.user.role == 'OWNER':
        return redirect('owner-dashboard')
    elif request.user.role in ['ADMIN', 'MANAGER']:
        return redirect('admin-dashboard')
    else:
        return redirect('user-dashboard')

@login_required
def admin_dashboard_view(request):
    # Security check: Owners should use the owner dashboard
    if request.user.role == 'OWNER':
        return redirect('owner-dashboard')
    
    # Security check: Only Admins/Managers can access this
    if request.user.role not in ['ADMIN', 'MANAGER']:
        return redirect('user-dashboard')

    today = timezone.now().date()  # Today in UTC/server time
    
    # 1. Global Stats
    total_employees = User.objects.filter(role='EMPLOYEE').count()
    
    todays_sessions = WorkSession.objects.filter(start_time__date=today)
    active_now_count = todays_sessions.filter(end_time__isnull=True).values('employee').distinct().count()
    
    completed_stats = todays_sessions.aggregate(total=Sum('total_seconds'), active=Sum('active_seconds'), idle=Sum('idle_seconds'))
    total_sec = completed_stats['total'] or 0
    active_sec = completed_stats['active'] or 0
    idle_sec = completed_stats['idle'] or 0
    
    # Add running sessions time
    running_sessions = todays_sessions.filter(end_time__isnull=True)
    for session in running_sessions:
        duration = (timezone.now() - session.start_time).total_seconds()
        total_sec += duration
        active_sec += duration 

    def format_hours(seconds): return round(seconds / 3600, 1)
    productivity = round((active_sec / total_sec) * 100, 1) if total_sec > 0 else 0
    
    # 2. Live Employee Status List (with timezone-aware filtering)
    employees = User.objects.filter(role='EMPLOYEE')
    employee_status_list = []
    
    for emp in employees:
        # Get employee's timezone for today's date calculation
        emp_today = get_today_in_user_tz(emp)
        
        # Check if currently active (has running session)
        current_session = WorkSession.objects.filter(employee=emp, end_time__isnull=True).first()
        is_online = current_session is not None
        
        # Get today's stats for this employee (using server timezone, then convert if needed)
        emp_sessions = WorkSession.objects.filter(employee=emp, start_time__date=today)
        emp_stats = emp_sessions.aggregate(total=Sum('total_seconds'), active=Sum('active_seconds'))
        
        # Add running time
        e_total = emp_stats['total'] or 0
        e_active = emp_stats['active'] or 0
        if is_online:
            run_dur = (timezone.now() - current_session.start_time).total_seconds()
            e_total += run_dur
            e_active += run_dur
            
        # Fetch recent data for Modal
        recent_ss = Screenshot.objects.filter(employee=emp, capture_time__date=today).order_by('-capture_time')[:10]
        
        # Convert screenshots to JSON-compatible format
        recent_ss_json = []
        for ss in recent_ss:
            recent_ss_json.append({
                'image_url': ss.image.url if ss.image else '',
                'capture_time': ss.capture_time.strftime('%H:%M')
            })
        
        recent_ss_json_str = json.dumps(recent_ss_json)
        
        top_apps = ApplicationUsage.objects.filter(employee=emp, created_at__date=today).values('app_name').annotate(total=Sum('active_seconds')).order_by('-total')[:5]
        top_sites = WebsiteUsage.objects.filter(employee=emp, created_at__date=today).values('domain').annotate(total=Sum('active_seconds')).order_by('-total')[:5]
        
        employee_status_list.append({
            'id': emp.id,
            'name': emp.get_full_name() or emp.username,
            'email': emp.email,
            'photo': emp.profile_picture.url if emp.profile_picture else None,
            'is_online': is_online,
            'total_time': format_hours(e_total),
            'productivity': round((e_active/e_total)*100) if e_total > 0 else 0,
            'recent_ss': recent_ss_json_str,
            'recent_ss_list': recent_ss_json,
            'top_apps': top_apps,
            'top_sites': top_sites
        })

    context = {
        'total_employees': total_employees, 'active_now': active_now_count,
        'total_hours': format_hours(total_sec), 'active_hours': format_hours(active_sec),
        'idle_hours': format_hours(idle_sec), 'productivity': productivity,
        'employee_status_list': employee_status_list
    }
    return render(request, 'dashboard.html', context)

@login_required
def user_dashboard_view(request):
    # Security check: Owners should use the owner dashboard
    if request.user.role == 'OWNER':
        return redirect('owner-dashboard')
    
    # Security check: Admins should use the admin dashboard (optional, but keeps it clean)
    if request.user.role in ['ADMIN', 'MANAGER']:
        return redirect('admin-dashboard')

    user = request.user
    today = timezone.now().date()
    todays_sessions = WorkSession.objects.filter(employee=user, start_time__date=today)
    stats = todays_sessions.aggregate(total=Sum('total_seconds'), active=Sum('active_seconds'))
    total_sec = stats['total'] or 0
    active_sec = stats['active'] or 0
    week_start = today - timedelta(days=today.weekday())
    weekly_sessions = WorkSession.objects.filter(employee=user, start_time__date__gte=week_start)
    weekly_total_sec = weekly_sessions.aggregate(total=Sum('total_seconds'))['total'] or 0
    def format_hours(seconds): return round(seconds / 3600, 1)
    top_apps = ApplicationUsage.objects.filter(employee=user, created_at__date=today).values('app_name').annotate(total_time=Sum('active_seconds')).order_by('-total_time')[:5]
    context = {
        'total_hours': format_hours(total_sec), 'active_hours': format_hours(active_sec),
        'idle_hours': format_hours(total_sec - active_sec),
        'productivity': round((active_sec / total_sec) * 100, 1) if total_sec > 0 else 0,
        'weekly_hours': format_hours(weekly_total_sec),
        'recent_sessions': todays_sessions.order_by('-start_time')[:5],
        'top_apps': top_apps,
    }
    return render(request, 'user_dashboard.html', context)

# ==========================
# EMPLOYEES
# ==========================

@login_required
def employee_list_view(request):
    # Show only EMPLOYEE role users
    employees = User.objects.filter(role='EMPLOYEE').order_by('-date_joined')
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        employees = employees.filter(
            Q(username__icontains=search_query) | 
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
        
    # Filter by Role
    role_filter = request.GET.get('role')
    if role_filter:
        employees = employees.filter(role=role_filter)
        
    # Filter by Status
    status_filter = request.GET.get('status')
    if status_filter == 'active':
        employees = employees.filter(is_active_employee=True)
    elif status_filter == 'inactive':
        employees = employees.filter(is_active_employee=False)
        
    return render(request, 'employee_list.html', {'employees': employees})

@login_required
def employee_add_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        designation = request.POST.get('designation')
        timezone_val = request.POST.get('timezone')
        is_active = request.POST.get('is_active_employee') == 'on'
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already exists!")
            return redirect('employee-add')
        try:
            user = User.objects.create_user(username=email, email=email, password=password)
            user.first_name = first_name; user.last_name = last_name; user.role = role
            user.designation = designation
            user.timezone = timezone_val; user.is_active_employee = is_active
            if 'profile_picture' in request.FILES: user.profile_picture = request.FILES['profile_picture']
            user.save()
            messages.success(request, f"Employee {first_name} added successfully!")
            return redirect('employee-list')
        except Exception as e: messages.error(request, f"Error creating user: {str(e)}")
    return render(request, 'employee_form.html')

@login_required
def employee_edit_view(request, emp_id):
    if request.user.role not in ['ADMIN', 'MANAGER']:
        messages.error(request, "Permission denied")
        return redirect('dashboard')
    
    emp = get_object_or_404(User, id=emp_id)
    
    if request.method == 'POST':
        new_email = request.POST.get('email')
        emp.first_name = request.POST.get('first_name')
        emp.last_name = request.POST.get('last_name')
        emp.email = new_email
        emp.username = new_email  # Update username to match email
        emp.role = request.POST.get('role')
        emp.designation = request.POST.get('designation')
        emp.timezone = request.POST.get('timezone')
        emp.is_active_employee = request.POST.get('is_active_employee') == 'on'
        
        # Update password only if provided
        new_password = request.POST.get('password')
        if new_password and new_password.strip():
            emp.set_password(new_password)
        
        if 'profile_picture' in request.FILES:
            emp.profile_picture = request.FILES['profile_picture']
        
        emp.save()
        messages.success(request, f"Employee {emp.first_name} updated successfully!")
        return redirect('employee-list')
    
    return render(request, 'employee_form.html', {'employee': emp, 'is_edit': True})

@login_required
def employee_delete_view(request, emp_id):
    if request.user.role not in ['ADMIN', 'MANAGER']:
        messages.error(request, "Permission denied")
        return redirect('dashboard')
    
    emp = get_object_or_404(User, id=emp_id)
    
    # Prevent deleting yourself
    if emp.id == request.user.id:
        messages.error(request, "You cannot delete your own account!")
        # Check if deleting from staff or employee list
        if emp.role in ['ADMIN', 'MANAGER']:
            return redirect('staff-list')
        return redirect('employee-list')
    
    # Only ADMIN can delete Admin/Manager users
    if emp.role in ['ADMIN', 'MANAGER'] and request.user.role != 'ADMIN':
        messages.error(request, "Only Admins can delete staff members!")
        return redirect('staff-list')
    
    emp_name = emp.get_full_name() or emp.username
    emp.delete()
    messages.success(request, f"User {emp_name} deleted successfully!")
    
    # Redirect based on deleted user's role
    if emp.role in ['ADMIN', 'MANAGER']:
        return redirect('staff-list')
    return redirect('employee-list')

@login_required
def employee_toggle_status_view(request, emp_id):
    if request.user.role not in ['ADMIN', 'MANAGER']:
        messages.error(request, "Permission denied")
        return redirect('dashboard')
    
    emp = get_object_or_404(User, id=emp_id)
    
    # Toggle active status
    emp.is_active_employee = not emp.is_active_employee
    emp.save()
    
    status = "activated" if emp.is_active_employee else "deactivated"
    messages.success(request, f"Employee {emp.username} {status} successfully!")
    return redirect('employee-list')

@login_required
def staff_list_view(request):
    """View for Admin and Manager users (Staff Management)"""
    if request.user.role not in ['ADMIN', 'MANAGER']:
        messages.error(request, "Permission denied")
        return redirect('dashboard')
    
    # Show ADMIN and MANAGER roles only
    staff = User.objects.filter(role__in=['ADMIN', 'MANAGER']).order_by('-date_joined')
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        staff = staff.filter(
            Q(username__icontains=search_query) | 
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(designation__icontains=search_query)
        )
        
    # Filter by Role
    role_filter = request.GET.get('role')
    if role_filter:
        staff = staff.filter(role=role_filter)
        
    return render(request, 'staff_list.html', {'staff': staff})

@login_required
def staff_add_view(request):
    """Add new Admin/Manager user"""
    if request.user.role != 'ADMIN':
        messages.error(request, "Only Admins can add staff members")
        return redirect('dashboard')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        designation = request.POST.get('designation')
        timezone_val = request.POST.get('timezone')
        is_active = request.POST.get('is_active_employee') == 'on'
        
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already exists!")
            return redirect('staff-add')
        try:
            user = User.objects.create_user(username=email, email=email, password=password)
            user.first_name = first_name
            user.last_name = last_name
            user.role = role
            user.designation = designation
            user.timezone = timezone_val
            user.is_active_employee = is_active
            user.is_staff = True  # Django staff permission
            if role == 'ADMIN':
                user.is_superuser = True
            if 'profile_picture' in request.FILES:
                user.profile_picture = request.FILES['profile_picture']
            user.save()
            messages.success(request, f"Staff member {first_name} added successfully!")
            return redirect('staff-list')
        except Exception as e:
            messages.error(request, f"Error creating user: {str(e)}")
    return render(request, 'staff_form.html')

@login_required
def staff_edit_view(request, staff_id):
    """Edit Admin/Manager user"""
    if request.user.role != 'ADMIN':
        messages.error(request, "Only Admins can edit staff members")
        return redirect('dashboard')
    
    staff = get_object_or_404(User, id=staff_id, role__in=['ADMIN', 'MANAGER'])
    
    if request.method == 'POST':
        new_email = request.POST.get('email')
        staff.first_name = request.POST.get('first_name')
        staff.last_name = request.POST.get('last_name')
        staff.email = new_email
        staff.username = new_email  # Update username to match email
        staff.role = request.POST.get('role')
        staff.designation = request.POST.get('designation')
        staff.timezone = request.POST.get('timezone')
        staff.is_active_employee = request.POST.get('is_active_employee') == 'on'
        staff.is_staff = True
        
        if request.POST.get('role') == 'ADMIN':
            staff.is_superuser = True
        else:
            staff.is_superuser = False
        
        new_password = request.POST.get('password')
        if new_password and new_password.strip():
            staff.set_password(new_password)
        
        if 'profile_picture' in request.FILES:
            staff.profile_picture = request.FILES['profile_picture']
        
        staff.save()
        messages.success(request, f"Staff member {staff.first_name} updated successfully!")
        return redirect('staff-list')
    
    return render(request, 'staff_form.html', {'staff': staff, 'is_edit': True})

@login_required
def employee_reset_password_view(request, emp_id):
    if request.user.role not in ['ADMIN', 'MANAGER']:
        messages.error(request, "Permission denied")
        return redirect('dashboard')
        
    emp = get_object_or_404(User, id=emp_id)
    emp.set_password('123456')
    emp.save()
    messages.success(request, f"Password for {emp.username} reset to '123456'")
    return redirect('employee-list')

# ==========================
# SESSIONS & SCREENSHOTS
# ==========================

@login_required
def session_list_view(request):
    sessions_qs = WorkSession.objects.select_related('employee').order_by('-start_time')
    emp_id = request.GET.get('employee')
    date_val = request.GET.get('date')
    if emp_id: sessions_qs = sessions_qs.filter(employee_id=emp_id)
    if date_val: sessions_qs = sessions_qs.filter(start_time__date=date_val)
    paginator = Paginator(sessions_qs, 20)
    sessions = paginator.get_page(request.GET.get('page'))
    employees = User.objects.filter(role='EMPLOYEE')
    return render(request, 'session_list.html', {'sessions': sessions, 'employees': employees})

@login_required
def session_detail_view(request, session_id):
    session = get_object_or_404(WorkSession, id=session_id)
    apps = ApplicationUsage.objects.filter(work_session=session).order_by('-active_seconds')
    websites = WebsiteUsage.objects.filter(work_session=session).order_by('-active_seconds')
    screenshots = Screenshot.objects.filter(work_session=session).order_by('capture_time')

    # If the session is still running, compute active/idle live from ActivityLog
    if session.end_time is None:
        now = timezone.now()
        duration = int((now - session.start_time).total_seconds())
        active_sec = ActivityLog.objects.filter(work_session=session, minute_type='ACTIVE').aggregate(total=Sum('duration_seconds'))['total'] or 0
        idle_sec = max(0, duration - active_sec)
        active_time = active_sec
        idle_time = idle_sec
    else:
        active_time = session.active_seconds
        idle_time = session.idle_seconds

    def format_time(seconds):
        h = seconds // 3600; m = (seconds % 3600) // 60; s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    return render(request, 'session_detail.html', {
        'session': session,
        'apps': apps,
        'websites': websites,
        'screenshots': screenshots,
        'active_time_fmt': format_time(active_time),
        'idle_time_fmt': format_time(idle_time)
    })

@login_required
def session_end_view(request, session_id):
    """Admin view to manually end a session"""
    if request.user.role not in ['ADMIN', 'MANAGER']:
        messages.error(request, "Permission denied")
        return redirect('dashboard')
    
    session = get_object_or_404(WorkSession, id=session_id)
    
    if request.method == 'POST':
        if not session.end_time:
            session.end_time = timezone.now()
            # Calculate total, active, and idle seconds
            total_duration = (session.end_time - session.start_time).total_seconds()
            active_duration = ActivityLog.objects.filter(work_session=session, minute_type='ACTIVE').aggregate(total=Sum('duration_seconds'))['total'] or 0
            idle_duration = max(0, total_duration - active_duration)
            
            session.total_seconds = int(total_duration)
            session.active_seconds = int(active_duration)
            session.idle_seconds = int(idle_duration)
            session.save()
            messages.success(request, f"Session for {session.employee.username} ended successfully!")
        else:
            messages.warning(request, "Session is already closed!")
        return redirect('session-detail', session_id=session_id)
    
    return redirect('session-detail', session_id=session_id)

@login_required
def session_delete_view(request, session_id):
    """Admin view to delete a work session"""
    if request.user.role not in ['ADMIN', 'MANAGER']:
        messages.error(request, "Permission denied")
        return redirect('session-list')
    
    session = get_object_or_404(WorkSession, id=session_id)
    emp_name = session.employee.username
    
    if request.method == 'POST':
        session.delete()
        messages.success(request, f"Session for {emp_name} deleted successfully!")
        return redirect('session-list')
    
    return redirect('session-list')

@login_required
def screenshot_gallery_view(request):
    screenshots_qs = Screenshot.objects.select_related('employee', 'work_session').order_by('-capture_time')
    emp_id = request.GET.get('employee')
    date_val = request.GET.get('date')
    if emp_id: screenshots_qs = screenshots_qs.filter(employee_id=emp_id)
    if date_val: screenshots_qs = screenshots_qs.filter(capture_time__date=date_val)
    paginator = Paginator(screenshots_qs, 24)
    screenshots = paginator.get_page(request.GET.get('page'))
    employees = User.objects.filter(role='EMPLOYEE')
    return render(request, 'screenshot_gallery.html', {'screenshots': screenshots, 'employees': employees})

# ==========================
# REPORTS (ADMIN)
# ==========================

@login_required
def reports_view(request):
    return render(request, 'reports.html', {
        'today_date': timezone.now().date().strftime('%Y-%m-%d'),
        'current_month': timezone.now().date().strftime('%Y-%m')
    })

@login_required
def report_daily_view(request):
    date_str = request.GET.get('date')
    if not date_str: return redirect('reports')
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    employees = User.objects.filter(role='EMPLOYEE')
    report_data = []
    total_worked_all = 0; total_active_all = 0; total_idle_all = 0
    for emp in employees:
        sessions = WorkSession.objects.filter(employee=emp, start_time__date=date_obj)
        if not sessions.exists(): continue
        stats = sessions.aggregate(first=Min('start_time'), last=Max('end_time'), total=Sum('total_seconds'), active=Sum('active_seconds'), idle=Sum('idle_seconds'))
        total = stats['total'] or 0; active = stats['active'] or 0; idle = stats['idle'] or 0
        total_worked_all += total; total_active_all += active; total_idle_all += idle
        def fmt(s): h = s // 3600; m = (s % 3600) // 60; return f"{h:02d}h {m:02d}m"
        report_data.append({
            'employee': emp, 'first_login': stats['first'], 'last_logout': stats['last'],
            'total_fmt': fmt(total), 'active_fmt': fmt(active), 'idle_fmt': fmt(idle),
            'productivity': round((active/total)*100, 1) if total > 0 else 0
        })
    def fmt_all(s): h = s // 3600; m = (s % 3600) // 60; return f"{h:02d}h {m:02d}m"
    return render(request, 'report_daily.html', {
        'date': date_obj, 'report_data': report_data,
        'total_worked_all': fmt_all(total_worked_all), 'total_active_all': fmt_all(total_active_all), 'total_idle_all': fmt_all(total_idle_all)
    })

@login_required
def report_monthly_view(request):
    month_str = request.GET.get('month')
    if not month_str: return redirect('reports')
    year, month = map(int, month_str.split('-'))
    employees = User.objects.filter(role='EMPLOYEE')
    report_data = []
    for emp in employees:
        sessions = WorkSession.objects.filter(employee=emp, start_time__year=year, start_time__month=month)
        if not sessions.exists(): continue
        days_worked = sessions.dates('start_time', 'day').count()
        stats = sessions.aggregate(total=Sum('total_seconds'), active=Sum('active_seconds'), idle=Sum('idle_seconds'))
        total = stats['total'] or 0; active = stats['active'] or 0; idle = stats['idle'] or 0
        report_data.append({
            'employee': emp, 'days_worked': days_worked,
            'total_hours': round(total / 3600, 1), 'active_hours': round(active / 3600, 1), 'idle_hours': round(idle / 3600, 1),
            'avg_daily': round((total / 3600) / days_worked, 1) if days_worked > 0 else 0,
            'productivity': round((active/total)*100, 1) if total > 0 else 0
        })
    return render(request, 'report_monthly.html', {'month_label': datetime(year, month, 1).strftime('%B %Y'), 'report_data': report_data})

@login_required
def report_top_apps_view(request):
    # Global Top Apps
    top_apps = ApplicationUsage.objects.values('app_name')\
        .annotate(total_time=Sum('active_seconds'))\
        .order_by('-total_time')[:10]
        
    top_sites = WebsiteUsage.objects.values('domain')\
        .annotate(total_time=Sum('active_seconds'))\
        .order_by('-total_time')[:10]
    
    # Get detailed website usage by employee (with full URL)
    detailed_sites = WebsiteUsage.objects.select_related('employee')\
        .values('domain', 'url', 'employee__first_name', 'employee__last_name')\
        .annotate(total_time=Sum('active_seconds'))\
        .order_by('-total_time')[:50]
        
    def fmt(s):
        h = s // 3600; m = (s % 3600) // 60
        return f"{h}h {m}m"
        
    # Format data for template
    apps_data = [{'app_name': x['app_name'], 'total_fmt': fmt(x['total_time'])} for x in top_apps]
    sites_data = [{'domain': x['domain'], 'total_fmt': fmt(x['total_time'])} for x in top_sites]
    detailed_sites_data = [{
        'domain': x['domain'], 
        'url': x.get('url') or f"https://{x['domain']}",  # Use stored URL or construct from domain
        'employee': f"{x['employee__first_name']} {x['employee__last_name']}",
        'total_fmt': fmt(x['total_time']),
        'total_seconds': x['total_time']
    } for x in detailed_sites]
    
    return render(request, 'report_top_apps.html', {
        'top_apps': apps_data,
        'top_sites': sites_data,
        'detailed_sites': detailed_sites_data
    })

# ==========================
# REPORTS (USER)
# ==========================

@login_required
def user_reports_view(request):
    return render(request, 'user_reports.html', {
        'today_date': timezone.now().date().strftime('%Y-%m-%d'),
        'current_month': timezone.now().date().strftime('%Y-%m')
    })

@login_required
def user_report_daily_view(request):
    date_str = request.GET.get('date')
    if not date_str: return redirect('user-reports')
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    # Only for current user
    sessions = WorkSession.objects.filter(employee=request.user, start_time__date=date_obj)
    
    report_data = []
    total_worked = 0
    
    if sessions.exists():
        stats = sessions.aggregate(
            first=Min('start_time'), last=Max('end_time'), 
            total=Sum('total_seconds'), active=Sum('active_seconds'), idle=Sum('idle_seconds')
        )
        total = stats['total'] or 0
        active = stats['active'] or 0
        idle = stats['idle'] or 0
        total_worked = total
        
        def fmt(s): h = s // 3600; m = (s % 3600) // 60; return f"{h:02d}h {m:02d}m"
        
        report_data.append({
            'employee': request.user,
            'first_login': stats['first'],
            'last_logout': stats['last'],
            'total_fmt': fmt(total),
            'active_fmt': fmt(active),
            'idle_fmt': fmt(idle),
            'productivity': round((active/total)*100, 1) if total > 0 else 0
        })
        
    return render(request, 'report_daily.html', {
        'date': date_obj,
        'report_data': report_data,
        'total_worked_all': total_worked # Reuse template logic
    })

@login_required
def user_report_monthly_view(request):
    month_str = request.GET.get('month')
    if not month_str: return redirect('user-reports')
    year, month = map(int, month_str.split('-'))
    
    sessions = WorkSession.objects.filter(employee=request.user, start_time__year=year, start_time__month=month)
    
    report_data = []
    if sessions.exists():
        days_worked = sessions.dates('start_time', 'day').count()
        stats = sessions.aggregate(total=Sum('total_seconds'), active=Sum('active_seconds'), idle=Sum('idle_seconds'))
        total = stats['total'] or 0; active = stats['active'] or 0; idle = stats['idle'] or 0
        
        report_data.append({
            'employee': request.user,
            'days_worked': days_worked,
            'total_hours': round(total / 3600, 1),
            'active_hours': round(active / 3600, 1),
            'idle_hours': round(idle / 3600, 1),
            'avg_daily': round((total / 3600) / days_worked, 1) if days_worked > 0 else 0,
            'productivity': round((active/total)*100, 1) if total > 0 else 0
        })
        
    return render(request, 'report_monthly.html', {
        'month_label': datetime(year, month, 1).strftime('%B %Y'),
        'report_data': report_data
    })

# ==========================
# TASKS
# ==========================

@login_required
def task_list_view(request):
    if request.user.role == 'EMPLOYEE':
        tasks = Task.objects.filter(assigned_to=request.user).order_by('-created_at')
    else:
        tasks = Task.objects.all().order_by('-created_at')
        
    return render(request, 'task_list.html', {'tasks': tasks})

@login_required
def task_add_view(request):
    if request.user.role == 'EMPLOYEE':
        return redirect('task-list')
        
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        assigned_to_id = request.POST.get('assigned_to')
        due_date = request.POST.get('due_date')
        
        assigned_to = get_object_or_404(User, id=assigned_to_id)
        
        Task.objects.create(
            title=title,
            description=description,
            assigned_to=assigned_to,
            assigned_by=request.user,
            due_date=due_date if due_date else None
        )
        messages.success(request, "Task assigned successfully!")
        return redirect('task-list')
        
    employees = User.objects.filter(role='EMPLOYEE')
    return render(request, 'task_form.html', {'employees': employees})

@login_required
def task_update_status_view(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    # Only assigned user can update status
    if request.user != task.assigned_to:
        messages.error(request, "Permission denied")
        return redirect('task-list')
        
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in ['OPEN', 'IN_PROGRESS', 'DONE']:
            task.status = status
            if status == 'DONE':
                task.completed_at = timezone.now()
            task.save()
            messages.success(request, "Task updated!")
            
    return redirect('task-list')

@login_required
def task_delete_view(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    # Only admin/manager can delete tasks
    if request.user.role not in ['ADMIN', 'MANAGER']:
        messages.error(request, "Permission denied")
        return redirect('task-list')
    
    if request.method == 'POST':
        task.delete()
        messages.success(request, "Task deleted successfully!")
        return redirect('task-list')
    
    return redirect('task-list')

# ==========================
# SETTINGS & PROFILE
# ==========================

@login_required
def settings_view(request):
    import logging
    from django.http import HttpResponse
    company_settings, created = CompanySettings.objects.get_or_create(pk=1, defaults={'company_name': 'My Company'})

    if request.method == 'POST':
        try:
            form_type = request.POST.get('form_type')

            if form_type == 'profile':
                request.user.first_name = request.POST.get('first_name')
                request.user.last_name = request.POST.get('last_name')
                request.user.timezone = request.POST.get('timezone')
                if 'profile_picture' in request.FILES:
                    request.user.profile_picture = request.FILES['profile_picture']
                request.user.save()
                messages.success(request, "Profile updated successfully!")

            elif form_type == 'company' and request.user.role == 'OWNER':
                company_settings.company_name = request.POST.get('company_name')
                company_settings.company_tagline = request.POST.get('company_tagline')
                company_settings.address = request.POST.get('address')
                company_settings.contact_email = request.POST.get('contact_email')
                company_settings.contact_phone = request.POST.get('contact_phone')
                company_settings.map_embed_url = request.POST.get('map_embed_url')
                company_settings.terms_url = request.POST.get('terms_url')
                company_settings.privacy_url = request.POST.get('privacy_url')
                company_settings.cookies_url = request.POST.get('cookies_url')
                company_settings.primary_color = request.POST.get('primary_color', '#667eea')
                company_settings.secondary_color = request.POST.get('secondary_color', '#764ba2')

                # Convert string to float/int for numeric fields
                try:
                    company_settings.daily_target_hours = float(request.POST.get('daily_target_hours', 8.0))
                except (ValueError, TypeError):
                    company_settings.daily_target_hours = 8.0

                try:
                    company_settings.idle_threshold_minutes = int(request.POST.get('idle_threshold_minutes', 5))
                except (ValueError, TypeError):
                    company_settings.idle_threshold_minutes = 5

                try:
                    company_settings.screenshot_retention_days = int(request.POST.get('screenshot_retention_days', 30))
                except (ValueError, TypeError):
                    company_settings.screenshot_retention_days = 30

                # Handle logo upload
                if 'logo' in request.FILES:
                    company_settings.logo = request.FILES['logo']

                # Handle favicon upload
                if 'favicon' in request.FILES:
                    company_settings.favicon = request.FILES['favicon']

                company_settings.save()
                messages.success(request, "Company branding updated successfully!")

            elif form_type == 'password':
                new_password = request.POST.get('new_password')
                confirm_password = request.POST.get('confirm_password')

                if new_password == confirm_password:
                    request.user.set_password(new_password)
                    request.user.save()
                    update_session_auth_hash(request, request.user) # Keep user logged in
                    messages.success(request, "Password changed successfully!")
                else:
                    messages.error(request, "Passwords do not match!")

            return redirect('settings')
        except Exception as e:
            import traceback
            logging.error(traceback.format_exc())
            return HttpResponse("Internal Server Error: " + str(e), status=500)

    return render(request, 'settings.html', {'company_settings': company_settings})

# ==========================
def landing_view(request):
    # If already authenticated, go to respective dashboard
    if request.user.is_authenticated:
        if request.user.role in ['ADMIN', 'MANAGER']:
            return redirect('admin-dashboard')
        return redirect('user-dashboard')

    return render(request, 'landing.html')

# ==========================
# AUTH
# ==========================

def admin_logout_view(request):
    logout(request)
    return redirect('admin-login')

def user_logout_view(request):
    logout(request)
    return redirect('user-login')

def admin_login_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'OWNER':
            return redirect('owner-dashboard')
        elif request.user.role in ['ADMIN', 'MANAGER']:
            return redirect('admin-dashboard')
        else:
            return redirect('user-dashboard')
    
    # Get company branding
    try:
        company = CompanySettings.objects.first()
    except:
        company = None
            
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.role == 'OWNER':
                login(request, user)
                return redirect('owner-dashboard')
            elif user.role in ['ADMIN', 'MANAGER']:
                login(request, user)
                return redirect('admin-dashboard')
            else:
                messages.error(request, "Access Denied: You are not an Admin.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'admin_login_new.html', {'form': form, 'company': company})

def user_login_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'EMPLOYEE':
            return redirect('user-dashboard')
        else:
            return redirect('admin-dashboard')
    
    # Get company branding
    try:
        company = CompanySettings.objects.first()
    except:
        company = None
            
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.role == 'EMPLOYEE':
                login(request, user)
                return redirect('user-dashboard')
            else:
                # Admins trying to login here will be redirected to admin dashboard
                login(request, user)
                return redirect('admin-dashboard')
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'user_login_new.html', {'form': form, 'company': company})

def owner_login_view(request):
    """Owner-only login view"""
    if request.user.is_authenticated:
        if request.user.role == 'OWNER':
            return redirect('owner-dashboard')
        elif request.user.role in ['ADMIN', 'MANAGER']:
            return redirect('admin-dashboard')
        else:
            return redirect('user-dashboard')
    
    # Get company branding
    try:
        company = CompanySettings.objects.first()
    except:
        company = None
            
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.role == 'OWNER':
                login(request, user)
                return redirect('owner-dashboard')
            else:
                messages.error(request, "Access Denied: You are not an Owner. Please use the appropriate login page.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'owner_login.html', {'form': form, 'company': company})

# ==================== LANDING PAGE SECTIONS ====================

def landing_view(request):
    """Home/Hero section of landing page"""
    try:
        company = CompanySettings.objects.first()
    except:
        company = None
    return render(request, 'landing.html', {'company': company})

def landing_features_view(request):
    """Features section page"""
    try:
        company = CompanySettings.objects.first()
    except:
        company = None
    return render(request, 'landing_features.html', {'company': company})

def landing_benefits_view(request):
    """Benefits section page"""
    try:
        company = CompanySettings.objects.first()
    except:
        company = None
    return render(request, 'landing_benefits.html', {'company': company})

def landing_contact_view(request):
    """Contact section page"""
    try:
        company = CompanySettings.objects.first()
    except:
        company = None
    return render(request, 'landing_contact.html', {'company': company})

def company_context(request):
    """
    Context processor to add company settings to all templates
    """
    try:
        company = CompanySettings.objects.first()
    except:
        company = None
    
    return {'company': company}
