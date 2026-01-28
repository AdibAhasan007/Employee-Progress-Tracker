from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import User, WorkSession, ApplicationUsage, WebsiteUsage, ActivityLog, Screenshot, Task
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
        
        session = WorkSession.objects.create(employee=user, start_time=timezone.now())
        
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
                work_session=session,
                employee=user,
                domain=site.get("domain"),
                active_seconds=site.get("active_seconds")
            )
            
        # 3. Save Activity Logs
        logs = data.get("activities", [])
        for log in logs:
            ActivityLog.objects.create(
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