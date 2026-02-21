from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import User, WorkSession, ApplicationUsage, WebsiteUsage, ActivityLog, Screenshot, Task, CompanyPolicy
import base64
from django.core.files.base import ContentFile

# ==========================================
# Authentication
# ==========================================

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        
        # We assume username is email for simplicity, or check both
        user = User.objects.filter(email=email).first()
        if user and user.check_password(password):
            if not user.is_active or not user.is_active_employee:
                return Response({"status": False, "message": "Account is inactive"}, status=403)
            
            # Calculate today's stats
            today = timezone.now().date()
            sessions = WorkSession.objects.filter(employee=user, start_time__date=today)
            
            total_worked = sum(s.total_seconds for s in sessions)
            active_time = sum(s.active_seconds for s in sessions)
            inactive_time = sum(s.idle_seconds for s in sessions)
            
            # Format time helper
            def format_time(seconds):
                h = seconds // 3600
                m = (seconds % 3600) // 60
                s = seconds % 60
                return f"{h:02d}:{m:02d}:{s:02d}"

            # Get tasks note (simple concatenation of open tasks)
            tasks = Task.objects.filter(assigned_to=user, status__in=['OPEN', 'IN_PROGRESS'])
            task_note = "\n".join([f"- {t.title}" for t in tasks])

            data = {
                "id": user.id,
                "name": f"{user.first_name} {user.last_name}".strip() or user.username,
                "email": user.email,
                "company_id": 1, # Default for single tenant
                "active_token": user.tracker_token,
                "toddays_worked_time": format_time(total_worked),
                "toddays_active_time": format_time(active_time),
                "toddays_inactive_time": format_time(inactive_time),
                "task_note": task_note
            }
            return Response({"status": True, "data": data})
        
        return Response({"status": False, "message": "Invalid credentials"}, status=401)

class LoginCheckView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        user_id = request.data.get("id")
        token = request.data.get("token")
        
        # Also ensure the employee is marked active on our side
        user = User.objects.filter(
            id=user_id,
            tracker_token=token,
            is_active=True,
            is_active_employee=True
        ).exists()
        return Response({"status": user})

# ==========================================
# Session Management
# ==========================================

class StartSessionView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        employee_id = request.data.get("employee_id")
        token = request.data.get("active_token")
        
        user = get_object_or_404(
            User,
            id=employee_id,
            tracker_token=token,
            is_active_employee=True,
            is_active=True,
        )
        
        session = WorkSession.objects.create(
            company=user.company,
            employee=user,
            start_time=timezone.now()
        )
        
        return Response({
            "status": True, 
            "message": "Session started", 
            "data": {"id": session.id}
        })

class StopSessionView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        session_id = request.data.get("session_id")
        employee_id = request.data.get("employee_id")
        token = request.data.get("active_token")
        
        user = get_object_or_404(
            User,
            id=employee_id,
            tracker_token=token,
            is_active_employee=True,
            is_active=True,
        )
        session = get_object_or_404(WorkSession, id=session_id, employee=user)
        
        if session.end_time:
            return Response({"status": False, "message": "Session already stopped"})
            
        session.end_time = timezone.now()
        
        # Calculate duration
        duration = (session.end_time - session.start_time).total_seconds()
        session.total_seconds = int(duration)
        
        # Recalculate active/idle from logs if available
        active_logs = ActivityLog.objects.filter(work_session=session, minute_type='ACTIVE')
        active_sec = sum(log.duration_seconds for log in active_logs)
        
        session.active_seconds = active_sec
        session.idle_seconds = max(0, session.total_seconds - active_sec)
        
        session.save()
        
        return Response({"status": True, "message": "Session stopped"})

class CheckSessionActiveView(APIView):
    """
    Checks if a work session is still active.
    Desktop app calls this periodically to detect if admin ended the session.
    If session was ended by admin, returns status=False.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        session_id = request.data.get("session_id")
        employee_id = request.data.get("employee_id")
        token = request.data.get("active_token")
        
        try:
            user = get_object_or_404(
                User,
                id=employee_id,
                tracker_token=token,
                is_active_employee=True,
                is_active=True,
            )
            session = get_object_or_404(WorkSession, id=session_id, employee=user)
            
            # If session has end_time, it means it was ended (by user or admin)
            if session.end_time:
                return Response({
                    "status": False,
                    "message": "Session has been ended",
                    "reason": "Session ended by administrator"
                })
            
            # Session is still active
            return Response({
                "status": True,
                "message": "Session is still active"
            })
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e)
            }, status=400)

# ==========================================
# Data Upload
# ==========================================

class UploadActivityView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        data = request.data
        employee_id = data.get("employee_id")
        session_id = data.get("work_session_id")
        token = data.get("active_token")
        
        user = get_object_or_404(
            User,
            id=employee_id,
            tracker_token=token,
            is_active_employee=True,
            is_active=True,
        )
        session = get_object_or_404(WorkSession, id=session_id, employee=user)
        
        # 1. Save Applications
        apps = data.get("applications", [])
        for app in apps:
            ApplicationUsage.objects.create(
                company=user.company,
                work_session=session,
                employee=user,
                app_name=app.get("app_name"),
                window_title=app.get("window_title"),
                active_seconds=app.get("active_seconds")
            )
            
        # 2. Save Websites
        sites = data.get("websites", [])
        for site in sites:
            WebsiteUsage.objects.create(
                company=user.company,
                work_session=session,
                employee=user,
                domain=site.get("domain"),
                url=site.get("url"),  # Store full URL
                active_seconds=site.get("active_seconds")
            )
            
        # 3. Save Activity Logs
        logs = data.get("activities", [])
        for log in logs:
            ActivityLog.objects.create(
                company=user.company,
                work_session=session,
                employee=user,
                minute_type=log.get("minute_type"),
                duration_seconds=log.get("duration_seconds")
            )
            
        return Response({"status": True, "message": "Data synced"})

class UploadScreenshotView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        employee_id = request.data.get("employee_id")
        session_id = request.data.get("work_session_id")
        capture_time = request.data.get("capture_time")
        photo_data = request.data.get("photo") # Base64 string
        token = request.data.get("active_token")
        
        # Verify employee is active and has valid token
        user = get_object_or_404(
            User,
            id=employee_id,
            tracker_token=token,
            is_active_employee=True,
            is_active=True,
        )
        session = get_object_or_404(WorkSession, id=session_id, employee=user)
        
        try:
            imgstr = photo_data
            # Handle if header is present (e.g., 'data:image/png;base64,...')
            if ',' in photo_data:
                imgstr = photo_data.split(',', 1)[1]
            
            ext = "png"
            decoded_image = base64.b64decode(imgstr)
            image_data = ContentFile(decoded_image, name=f"ss_{session_id}_{timezone.now().timestamp()}.{ext}")
            
            Screenshot.objects.create(
                company=user.company,
                work_session=session,
                employee=user,
                image=image_data,
                capture_time=capture_time or timezone.now()
            )
            return Response({"status": True, "message": "Screenshot uploaded"})
        except (ValueError, TypeError) as e:
            return Response({"status": False, "message": f"Invalid image data: {str(e)}"}, status=400)
        except Exception as e:
            return Response({"status": False, "message": f"Screenshot upload failed: {str(e)}"}, status=500)

# ==========================================
# Tasks
# ==========================================

class GetTasksView(APIView):
    """API endpoint to get tasks for the logged-in employee"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        user_id = request.data.get("id")
        active_token = request.data.get("active_token")
        
        try:
            user = User.objects.get(id=user_id)
            
            # Get all tasks assigned to this user
            tasks = Task.objects.filter(assigned_to=user).order_by('-created_at')
            
            tasks_data = [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "assigned_by": task.assigned_by.get_full_name() or task.assigned_by.username,
                    "created_at": task.created_at.isoformat(),
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                }
                for task in tasks
            ]
            
            return Response({
                "status": True,
                "data": tasks_data,
                "message": f"Retrieved {tasks.count()} tasks"
            })
        except User.DoesNotExist:
            return Response({"status": False, "message": "User not found"}, status=404)
        except Exception as e:
            return Response({"status": False, "message": str(e)}, status=500)


class UpdateTaskStatusView(APIView):
    """API endpoint to update task status"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        task_id = request.data.get("task_id")
        new_status = request.data.get("status")
        user_id = request.data.get("id")
        
        try:
            task = Task.objects.get(id=task_id)
            user = User.objects.get(id=user_id)
            
            # Check if user is assigned to this task
            if task.assigned_to != user:
                return Response({"status": False, "message": "Not assigned to this task"}, status=403)
            
            # Update task status
            if new_status in ['OPEN', 'IN_PROGRESS', 'DONE']:
                task.status = new_status
                if new_status == 'DONE':
                    task.completed_at = timezone.now()
                task.save()
                return Response({
                    "status": True,
                    "message": f"Task updated to {new_status}",
                    "data": {
                        "id": task.id,
                        "status": task.status,
                        "completed_at": task.completed_at.isoformat() if task.completed_at else None
                    }
                })
            else:
                return Response({"status": False, "message": "Invalid status"}, status=400)
        except Task.DoesNotExist:
            return Response({"status": False, "message": "Task not found"}, status=404)
        except User.DoesNotExist:
            return Response({"status": False, "message": "User not found"}, status=404)
        except Exception as e:
            return Response({"status": False, "message": str(e)}, status=500)

# ==========================================
# AGENT HEARTBEAT & POLICY
# ==========================================

@require_http_methods(["POST"])
@login_required
def agent_heartbeat(request):
    """
    Desktop agent reports it's alive.
    Call every 5 minutes to track online status.
    """
    try:
        request.user.last_agent_sync_at = timezone.now()
        request.user.save(update_fields=['last_agent_sync_at'])
        
        return JsonResponse({
            'status': 'ok',
            'server_time': timezone.now().isoformat(),
            'company_status': request.user.company.status,
            'message': 'Heartbeat received'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@require_http_methods(["GET"])
@login_required
def get_company_policy(request):
    """
    Desktop agent fetches policy to configure tracking behavior.
    Call on startup and every 60 minutes.
    """
    try:
        # Get or create policy
        try:
            policy = request.user.company.policy
        except CompanyPolicy.DoesNotExist:
            policy = CompanyPolicy.objects.create(company=request.user.company)
        
        return JsonResponse({
            'success': True,
            'policy': {
                'company_key': request.user.company.company_key,
                'company_status': request.user.company.status,
                'is_active_subscription': request.user.company.is_active_subscription(),
                'screenshots': {
                    'enabled': policy.screenshots_enabled,
                    'interval_seconds': policy.screenshot_interval_seconds,
                },
                'website_tracking': {
                    'enabled': policy.website_tracking_enabled,
                },
                'app_tracking': {
                    'enabled': policy.app_tracking_enabled,
                },
                'idle_threshold_seconds': policy.idle_threshold_seconds,
            },
            'policy_updated_at': policy.updated_at.isoformat(),
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


# ==========================================
# REALTIME CONFIG SYNC API
# ==========================================

class EmployeeConfigView(APIView):
    """
    Realtime configuration endpoint for desktop agent.
    Desktop app polls this endpoint to get updated policy settings.
    Includes version hash for cache busting.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        GET /api/employee-config/
        Returns the current company policy configuration.
        """
        try:
            if not request.user.is_active or not request.user.is_active_employee:
                return Response({
                    'status': False,
                    'message': 'User account is inactive'
                }, status=403)
            
            # Get or create company policy
            try:
                policy = request.user.company.policy
            except CompanyPolicy.DoesNotExist:
                policy = CompanyPolicy.objects.create(company=request.user.company)
            
            # Return full configuration
            config_data = {
                'status': True,
                'config': policy.to_dict(),
                'company': {
                    'name': request.user.company.name,
                    'status': request.user.company.status,
                    'is_active': request.user.company.is_active_subscription(),
                },
                'timestamp': timezone.now().isoformat(),
            }
            
            return Response(config_data)
        
        except Exception as e:
            return Response({
                'status': False,
                'message': str(e)
            }, status=500)


class UpdateCompanyPolicyView(APIView):
    """
    Update company policy settings (OWNER only).
    Triggers realtime sync to all desktop agents.
    Creates audit log entry.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        POST /api/update-company-policy/
        Update policy settings. Only OWNER can update.
        """
        try:
            # Check permission
            if request.user.role != 'OWNER':
                return Response({
                    'status': False,
                    'message': 'Only OWNER can update company policy'
                }, status=403)
            
            # Get company policy
            try:
                policy = request.user.company.policy
            except CompanyPolicy.DoesNotExist:
                policy = CompanyPolicy.objects.create(company=request.user.company)
            
            # Get request data
            data = request.data
            
            # Store old values for audit log
            old_values = {}
            new_values = {}
            
            # Update allowed fields
            allowed_fields = [
                'screenshots_enabled',
                'website_tracking_enabled',
                'app_tracking_enabled',
                'screenshot_interval_seconds',
                'idle_threshold_seconds',
                'config_sync_interval_seconds',
                'max_screenshot_size_mb',
                'screenshot_quality',
                'enable_keyboard_tracking',
                'enable_mouse_tracking',
                'enable_idle_detection',
                'show_tracker_notification',
                'notification_interval_minutes',
                'local_data_retention_days',
            ]
            
            for field in allowed_fields:
                if field in data:
                    old_values[field] = getattr(policy, field)
                    
                    # Type conversion
                    value = data[field]
                    if isinstance(value, bool) or field.endswith('_enabled'):
                        value = bool(value)
                    else:
                        value = int(value)
                    
                    # Validation
                    if field == 'screenshot_interval_seconds':
                        value = max(30, min(3600, value))  # 30 sec to 1 hour
                    elif field == 'idle_threshold_seconds':
                        value = max(60, min(1800, value))  # 1 min to 30 min
                    elif field == 'config_sync_interval_seconds':
                        value = max(5, min(60, value))  # 5 to 60 seconds
                    elif field == 'max_screenshot_size_mb':
                        value = max(1, min(50, value))  # 1 to 50 MB
                    elif field == 'screenshot_quality':
                        value = max(50, min(95, value))  # 50 to 95
                    elif field == 'notification_interval_minutes':
                        value = max(0, min(120, value))  # 0 to 120 minutes
                    elif field == 'local_data_retention_days':
                        value = max(7, min(365, value))  # 7 to 365 days
                    
                    setattr(policy, field, value)
                    new_values[field] = value
            
            # Increment version for cache busting
            policy.increment_version()
            
            # Create audit log
            if old_values:  # Only log if something changed
                from .models import AuditLog
                AuditLog.objects.create(
                    company=request.user.company,
                    user=request.user,
                    action_type='POLICY_CHANGED',
                    description=f'Updated company policy settings',
                    details={
                        'old_values': old_values,
                        'new_values': new_values,
                        'config_version': policy.config_version,
                    },
                    ip_address=self.get_client_ip(request),
                )
            
            return Response({
                'status': True,
                'message': 'Policy updated successfully',
                'config': policy.to_dict(),
            })
        
        except Exception as e:
            return Response({
                'status': False,
                'message': str(e)
            }, status=500)
    
    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip