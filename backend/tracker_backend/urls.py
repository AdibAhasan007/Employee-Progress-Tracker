from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.web_views import (landing_view, admin_login_view, user_login_view, 
                            landing_features_view, landing_benefits_view, landing_contact_view,
                            admin_task_monitor_view, admin_task_assign_view, admin_task_statistics_view)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')), # Prefix all core URLs with /api/

    # Friendly web entry points
    path('', landing_view, name='landing'),
    path('home/', landing_view, name='landing-home'),
    path('features/', landing_features_view, name='landing-features'),
    path('benefits/', landing_benefits_view, name='landing-benefits'),
    path('contact/', landing_contact_view, name='landing-contact'),
    path('login/', admin_login_view, name='admin-login-main'),
    path('signin/', user_login_view, name='user-login-main'),
    
    # Task Management Routes
    path('dashboard/tasks/monitor/', admin_task_monitor_view, name='admin-task-monitor'),
    path('dashboard/tasks/assign/', admin_task_assign_view, name='admin-task-assign'),
    path('dashboard/tasks/statistics/', admin_task_statistics_view, name='admin-task-statistics'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
