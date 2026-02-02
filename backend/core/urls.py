from django.urls import path
from django.views.generic import RedirectView
from .views import (
    LoginView, LoginCheckView, 
    StartSessionView, StopSessionView, CheckSessionActiveView,
    UploadActivityView, UploadScreenshotView,
    GetTasksView, UpdateTaskStatusView,
    agent_heartbeat, get_company_policy
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
    admin_login_view, user_login_view, owner_login_view,
    landing_view, landing_features_view, landing_benefits_view, landing_contact_view,
    policy_configuration_view, audit_log_viewer_view, dashboard_alerts_api, employee_sync_status_view,
    billing_dashboard_view, upgrade_subscription_view, payment_history_view, billing_settings_view, alerts_notifications_view,
    departments_view, teams_view, analytics_dashboard_view, time_utilization_view, activity_heatmap_view,
    branding_settings_view, sso_configuration_view, generate_report_view
)
from .web_views import session_active_time_api
from .stripe_webhooks import stripe_webhook_handler
from .owner_views import (
    owner_dashboard, company_detail, create_company, change_plan, edit_company, delete_company,
    suspend_company, reactivate_company, rotate_company_key, owner_reports, company_credentials,
    retention_policy_view, update_retention_policy, update_global_privacy, owner_audit_log
)

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
    
    # Agent endpoints
    path('api/agent/heartbeat/', agent_heartbeat, name='api-agent-heartbeat'),
    path('api/policy/', get_company_policy, name='api-get-policy'),

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
    
    # ===========================
    # PHASE 2: Admin Enhancements
    # ===========================
    path('policy/', policy_configuration_view, name='policy-configuration'),
    path('audit-logs/', audit_log_viewer_view, name='audit-logs'),
    path('api/dashboard-alerts/', dashboard_alerts_api, name='dashboard-alerts-api'),
    path('agent-sync-status/', employee_sync_status_view, name='employee-sync-status'),
    
    # ===========================
    # PHASE 3: Billing & Subscriptions
    # ===========================
    path('billing/', billing_dashboard_view, name='billing-dashboard'),
    path('billing/upgrade/', upgrade_subscription_view, name='upgrade-subscription'),
    path('billing/payment-history/', payment_history_view, name='payment-history'),
    path('billing/settings/', billing_settings_view, name='billing-settings'),
    path('alerts/', alerts_notifications_view, name='alerts-notifications'),
    
    # Stripe Webhook
    path('api/stripe/webhook/', stripe_webhook_handler, name='stripe-webhook'),
    
    # ===========================
    # PHASE 4: Enterprise Features
    # ===========================
    # Departments & Teams
    path('departments/', departments_view, name='departments'),
    path('teams/', teams_view, name='teams'),
    
    # Analytics & Reports
    path('analytics/', analytics_dashboard_view, name='analytics-dashboard'),
    path('analytics/time-utilization/', time_utilization_view, name='time-utilization'),
    path('analytics/activity-heatmap/', activity_heatmap_view, name='activity-heatmap'),
    path('analytics/reports/', generate_report_view, name='generate-report'),
    
    # Branding & SSO
    path('branding/', branding_settings_view, name='branding-settings'),
    path('sso/', sso_configuration_view, name='sso-configuration'),
    
    # Settings
    path('settings/', settings_view, name='settings'),
    
    # Web Auth (Separated)
    path('admin/login/', admin_login_view, name='admin-login'),
    path('user/login/', user_login_view, name='user-login'),
    path('owner/login/', owner_login_view, name='owner-login-main'),
    path('admin/logout/', admin_logout_view, name='admin-logout'),
    path('user/logout/', user_logout_view, name='user-logout'),
    
    # Landing Page Sections
    path('home/', landing_view, name='landing-home'),
    path('', RedirectView.as_view(url='/api/home/', permanent=True), name='home-redirect'),
    path('features/', landing_features_view, name='features'),
    path('benefits/', landing_benefits_view, name='benefits'),
    path('contact/', landing_contact_view, name='contact'),
    
    # ===========================
    # OWNER Portal (Multi-Tenant)
    # ===========================
    path('owner/dashboard/', owner_dashboard, name='owner-dashboard'),
    path('owner/company/<int:company_id>/', company_detail, name='owner-company-detail'),
    path('owner/company/create/', create_company, name='owner-create-company'),
    path('owner/company/credentials/', company_credentials, name='owner-company-credentials'),
    path('owner/company/<int:company_id>/edit/', edit_company, name='owner-edit-company'),
    path('owner/company/<int:company_id>/delete/', delete_company, name='owner-delete-company'),
    path('owner/company/<int:company_id>/change-plan/', change_plan, name='owner-change-plan'),
    path('owner/company/<int:company_id>/suspend/', suspend_company, name='owner-suspend-company'),
    path('owner/company/<int:company_id>/reactivate/', reactivate_company, name='owner-reactivate-company'),
    path('owner/company/<int:company_id>/rotate-key/', rotate_company_key, name='owner-rotate-key'),
    path('owner/reports/', owner_reports, name='owner-reports'),
    path('owner/retention-policy/', retention_policy_view, name='owner-retention-policy'),
    path('owner/retention-policy/<int:plan_id>/update/', update_retention_policy, name='owner-update-retention'),
    path('owner/privacy/update/', update_global_privacy, name='owner-update-global-privacy'),
    path('owner/audit-log/', owner_audit_log, name='owner-audit-log'),
]
