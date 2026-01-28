from django.urls import path
from .views import (
    LoginView, LoginCheckView, 
    StartSessionView, StopSessionView, CheckSessionActiveView,
    UploadActivityView, UploadScreenshotView,
    GetTasksView, UpdateTaskStatusView
)
from .web_views import (
    dashboard_view, admin_dashboard_view, user_dashboard_view,
    employee_list_view, employee_add_view, employee_edit_view, employee_delete_view, 
    employee_toggle_status_view, employee_reset_password_view,
    staff_list_view, staff_add_view, staff_edit_view,
    session_list_view, session_detail_view, session_end_view, session_delete_view,
    screenshot_gallery_view,
    reports_view, report_daily_view, report_monthly_view, report_top_apps_view,
    user_reports_view, user_report_daily_view, user_report_monthly_view,
    task_list_view, task_add_view, task_update_status_view, task_delete_view,
    settings_view, admin_logout_view, user_logout_view,
    admin_login_view, user_login_view,
    landing_home_view, landing_features_view, landing_benefits_view, landing_contact_view
)
from .web_views import session_active_time_api

urlpatterns = [
    # ===========================
    # API Endpoints (Desktop App)
    # ===========================
    path('login', LoginView.as_view(), name='api-login'),
    path('login-check', LoginCheckView.as_view(), name='api-login-check'),
    path('work-session/create', StartSessionView.as_view(), name='api-session-create'),
    path('work-session/stop', StopSessionView.as_view(), name='api-session-stop'),
    path('check-session-active', CheckSessionActiveView.as_view(), name='api-check-session-active'),
    path('upload/employee-activity', UploadActivityView.as_view(), name='api-upload-activity'),
    path('screenshot/upload', UploadScreenshotView.as_view(), name='api-upload-screenshot'),
    path('tasks/get', GetTasksView.as_view(), name='api-tasks-get'),
    path('tasks/update', UpdateTaskStatusView.as_view(), name='api-tasks-update'),
    path('api/session/<int:session_id>/active_time/', session_active_time_api, name='api-session-active-time'),

    # ===========================
    # Web Dashboard (Browser)
    # ===========================
    path('dashboard/', dashboard_view, name='dashboard'),
    path('dashboard/admin/', admin_dashboard_view, name='admin-dashboard'),
    path('dashboard/user/', user_dashboard_view, name='user-dashboard'),
    
    # Employees
    path('employees/', employee_list_view, name='employee-list'),
    path('employees/add/', employee_add_view, name='employee-add'),
    path('employees/<int:emp_id>/edit/', employee_edit_view, name='employee-edit'),
    path('employees/<int:emp_id>/delete/', employee_delete_view, name='employee-delete'),
    path('employees/<int:emp_id>/toggle-status/', employee_toggle_status_view, name='employee-toggle-status'),
    path('employees/<int:emp_id>/reset-password/', employee_reset_password_view, name='employee-reset-password'),
    
    # Staff Management (Admin/Manager)
    path('staff/', staff_list_view, name='staff-list'),
    path('staff/add/', staff_add_view, name='staff-add'),
    path('staff/<int:staff_id>/edit/', staff_edit_view, name='staff-edit'),
    
    # Sessions
    path('sessions/', session_list_view, name='session-list'),
    path('sessions/<int:session_id>/', session_detail_view, name='session-detail'),
    path('sessions/<int:session_id>/end/', session_end_view, name='session-end'),
    path('sessions/<int:session_id>/delete/', session_delete_view, name='session-delete'),
    
    # Screenshots
    path('screenshots/', screenshot_gallery_view, name='screenshot-gallery'),
    
    # Reports (Admin)
    path('reports/', reports_view, name='reports'),
    path('reports/daily/', report_daily_view, name='report-daily'),
    path('reports/monthly/', report_monthly_view, name='report-monthly'),
    path('reports/top-apps/', report_top_apps_view, name='report-top-apps'),
    
    # Reports (User)
    path('my-reports/', user_reports_view, name='user-reports'),
    path('my-reports/daily/', user_report_daily_view, name='user-report-daily'),
    path('my-reports/monthly/', user_report_monthly_view, name='user-report-monthly'),
    
    # Tasks
    path('tasks/', task_list_view, name='task-list'),
    path('tasks/add/', task_add_view, name='task-add'),
    path('tasks/<int:task_id>/update/', task_update_status_view, name='task-update-status'),
    path('tasks/<int:task_id>/delete/', task_delete_view, name='task-delete'),
    
    # Settings
    path('settings/', settings_view, name='settings'),
    
    # Web Auth (Separated)
    path('admin/login/', admin_login_view, name='admin-login'),
    path('user/login/', user_login_view, name='user-login'),
    path('admin/logout/', admin_logout_view, name='admin-logout'),
    path('user/logout/', user_logout_view, name='user-logout'),
    
    # Landing Page Sections
    path('', landing_home_view, name='landing-home'),
    path('home/', landing_home_view, name='home'),
    path('features/', landing_features_view, name='features'),
    path('benefits/', landing_benefits_view, name='benefits'),
    path('contact/', landing_contact_view, name='contact'),
]
