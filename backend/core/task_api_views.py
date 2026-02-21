# ===================================================
# PHASE 4: REAL-TIME TASK MANAGEMENT SYSTEM
# ===================================================
# API endpoints for real-time task assignment,
# progress tracking, and occupancy monitoring

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from datetime import datetime
from .models import Task, TaskProgress
import json

@method_decorator(login_required, name='dispatch')
class EmployeeTasksView(APIView):
    """
    GET: Employee retrieves their assigned tasks (for polling by desktop app)
    Real-time task assignment detection
    """
    
    def get(self, request):
        """
        Get all tasks assigned to the current employee
        Returns: List of tasks with current progress and priority
        Used by: Desktop app TaskManager for polling
        """
        try:
            # Get employee
            employee = request.user
            
            if employee.role != 'EMPLOYEE':
                return Response({
                    'status': False,
                    'message': 'Only employees can view their tasks'
                }, status=403)
            
            # Get all pending and in-progress tasks
            tasks = Task.objects.filter(
                assigned_to=employee,
                status__in=['PENDING', 'OPEN', 'IN_PROGRESS']
            ).select_related('assigned_by', 'company', 'project').values(
                'id', 'title', 'description', 'status', 'priority',
                'progress_percentage', 'due_date', 'created_at',
                'company__name', 'project__name', 'assigned_by__first_name',
                'assigned_by__last_name', 'last_progress_update_at'
            )
            
            tasks_list = []
            for task in tasks:
                tasks_list.append({
                    'id': task['id'],
                    'title': task['title'],
                    'description': task['description'],
                    'status': task['status'],
                    'priority': task['priority'],
                    'progress_percentage': task['progress_percentage'],
                    'due_date': task['due_date'].isoformat() if task['due_date'] else None,
                    'created_at': task['created_at'].isoformat(),
                    'company_name': task['company__name'],
                    'project_name': task['project__name'],
                    'assigned_by': f"{task['assigned_by__first_name']} {task['assigned_by__last_name']}",
                    'last_progress_update_at': task['last_progress_update_at'].isoformat() if task['last_progress_update_at'] else None,
                })
            
            return Response({
                'status': True,
                'tasks': tasks_list,
                'count': len(tasks_list),
                'timestamp': datetime.now().isoformat()
            }, status=200)
            
        except Exception as e:
            return Response({
                'status': False,
                'message': f'Error retrieving tasks: {str(e)}'
            }, status=500)


@method_decorator(login_required, name='dispatch')
class TaskProgressUpdateView(APIView):
    """
    POST: Employee updates their task progress
    Updates progress percentage and occupancy status
    Triggers real-time notification to admin
    """
    
    def post(self, request, task_id):
        """
        Update task progress
        Request body:
        {
            'progress_percentage': 50,
            'notes': 'Working on task',
            'occupancy_status': 'ACTIVE'  # ACTIVE, IDLE, OFFLINE
        }
        """
        try:
            # Get employee
            employee = request.user
            
            if employee.role != 'EMPLOYEE':
                return Response({
                    'status': False,
                    'message': 'Only employees can update task progress'
                }, status=403)
            
            # Get task
            task = Task.objects.get(id=task_id, assigned_to=employee)
            
            # Validate request data
            progress_percentage = request.data.get('progress_percentage')
            notes = request.data.get('notes', '')
            occupancy_status = request.data.get('occupancy_status', 'ACTIVE')
            
            # Validate progress percentage
            if progress_percentage is None:
                return Response({
                    'status': False,
                    'message': 'progress_percentage is required'
                }, status=400)
            
            try:
                progress_percentage = int(progress_percentage)
                if progress_percentage < 0 or progress_percentage > 100:
                    return Response({
                        'status': False,
                        'message': 'progress_percentage must be between 0 and 100'
                    }, status=400)
            except (ValueError, TypeError):
                return Response({
                    'status': False,
                    'message': 'progress_percentage must be an integer'
                }, status=400)
            
            # Auto-update task status based on progress
            previous_percentage = task.progress_percentage
            if progress_percentage == 100 and task.status != 'DONE':
                task.status = 'DONE'
                task.completed_at = datetime.now()
            elif progress_percentage > 0 and task.status == 'PENDING':
                task.status = 'IN_PROGRESS'
            
            # Update task
            task.progress_percentage = progress_percentage
            task.last_progress_update_at = datetime.now()
            task.last_progress_updated_by = employee
            task.save()
            
            # Create TaskProgress history entry
            TaskProgress.objects.create(
                task=task,
                updated_by=employee,
                previous_percentage=previous_percentage,
                new_percentage=progress_percentage,
                notes=notes,
                occupancy_status=occupancy_status
            )
            
            return Response({
                'status': True,
                'message': 'Task progress updated successfully',
                'task_id': task.id,
                'previous_percentage': previous_percentage,
                'new_percentage': progress_percentage,
                'task_status': task.status,
                'timestamp': datetime.now().isoformat()
            }, status=200)
            
        except Task.DoesNotExist:
            return Response({
                'status': False,
                'message': 'Task not found or not assigned to you'
            }, status=404)
        except Exception as e:
            return Response({
                'status': False,
                'message': f'Error updating task progress: {str(e)}'
            }, status=500)


@method_decorator(login_required, name='dispatch')
class AdminTaskStatusView(APIView):
    """
    GET: Admin/Owner views all task progress in real-time
    Used for live task monitoring dashboard
    """
    
    def get(self, request):
        """
        Get all tasks with progress for admin company
        Returns: All tasks with live progress and occupancy status
        """
        try:
            user = request.user
            
            # Only ADMIN can view company tasks
            if user.role != 'ADMIN':
                return Response({
                    'status': False,
                    'message': 'Only ADMIN can view task status'
                }, status=403)
            
            # Get admin's company
            company = user.company
            if not company:
                return Response({
                    'status': False,
                    'message': 'No company assigned'
                }, status=400)
            
            # Get all tasks for the company with related data
            tasks = Task.objects.filter(
                company=company
            ).select_related('assigned_to', 'assigned_by', 'project').values(
                'id', 'title', 'status', 'priority', 'progress_percentage',
                'due_date', 'created_at', 'last_progress_update_at',
                'assigned_to__first_name', 'assigned_to__last_name',
                'assigned_to__id', 'project__name'
            )
            
            tasks_list = []
            for task in tasks:
                # Get latest occupancy status from TaskProgress
                latest_progress = TaskProgress.objects.filter(
                    task_id=task['id']
                ).order_by('-created_at').first()
                
                occupancy_status = latest_progress.occupancy_status if latest_progress else 'UNKNOWN'
                
                tasks_list.append({
                    'id': task['id'],
                    'title': task['title'],
                    'status': task['status'],
                    'priority': task['priority'],
                    'progress_percentage': task['progress_percentage'],
                    'due_date': task['due_date'].isoformat() if task['due_date'] else None,
                    'created_at': task['created_at'].isoformat(),
                    'last_progress_update_at': task['last_progress_update_at'].isoformat() if task['last_progress_update_at'] else None,
                    'employee_name': f"{task['assigned_to__first_name']} {task['assigned_to__last_name']}",
                    'employee_id': task['assigned_to__id'],
                    'project_name': task['project__name'],
                    'occupancy_status': occupancy_status,
                    'is_overdue': task['due_date'] < datetime.now() if task['due_date'] else False,
                })
            
            return Response({
                'status': True,
                'tasks': tasks_list,
                'count': len(tasks_list),
                'company': company.name,
                'timestamp': datetime.now().isoformat()
            }, status=200)
            
        except Exception as e:
            return Response({
                'status': False,
                'message': f'Error retrieving task status: {str(e)}'
            }, status=500)


@method_decorator(login_required, name='dispatch')
class TaskCompleteView(APIView):
    """
    POST: Employee marks task as complete
    Auto-sets progress to 100% and status to DONE
    """
    
    def post(self, request, task_id):
        """
        Mark task as complete
        Request body:
        {
            'completion_notes': 'Task completed successfully'
        }
        """
        try:
            employee = request.user
            
            if employee.role != 'EMPLOYEE':
                return Response({
                    'status': False,
                    'message': 'Only employees can mark tasks complete'
                }, status=403)
            
            task = Task.objects.get(id=task_id, assigned_to=employee)
            
            # Store previous values
            previous_percentage = task.progress_percentage
            completion_notes = request.data.get('completion_notes', '')
            
            # Update task
            task.status = 'DONE'
            task.progress_percentage = 100
            task.last_progress_update_at = datetime.now()
            task.last_progress_updated_by = employee
            task.completed_at = datetime.now()
            task.success_note = completion_notes
            task.save()
            
            # Create TaskProgress history
            TaskProgress.objects.create(
                task=task,
                updated_by=employee,
                previous_percentage=previous_percentage,
                new_percentage=100,
                notes=f"Task marked complete. {completion_notes}",
                occupancy_status='ACTIVE'
            )
            
            return Response({
                'status': True,
                'message': 'Task marked as complete',
                'task_id': task.id,
                'task_status': task.status,
                'completed_at': task.completed_at.isoformat(),
                'timestamp': datetime.now().isoformat()
            }, status=200)
            
        except Task.DoesNotExist:
            return Response({
                'status': False,
                'message': 'Task not found'
            }, status=404)
        except Exception as e:
            return Response({
                'status': False,
                'message': f'Error completing task: {str(e)}'
            }, status=500)
