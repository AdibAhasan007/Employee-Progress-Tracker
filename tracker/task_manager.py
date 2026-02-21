# ===================================================
# REALTIME TASK MANAGEMENT SYSTEM
# Desktop App Task Manager
# ===================================================
# Handles real-time task polling, caching, and management
# Similar to ConfigManager pattern

import json
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from api_helper import api_post

class TaskManager:
    """
    Manages real-time task polling and synchronization for desktop apps.
    Polls API every 5 seconds to detect new/updated tasks.
    Caches tasks locally to minimize network usage.
    Supports offline mode with fallback to cached data.
    """
    
    def __init__(self, employee_id: int, api_url: str = "http://127.0.0.1:8000/api/", token: str = None):
        """
        Initialize TaskManager
        
        Args:
            employee_id: Current employee's ID
            api_url: Base API URL for the backend
            token: Authentication token for API requests
        """
        self.employee_id = employee_id
        self.api_url = api_url
        self.token = token
        
        # Local cache file
        self.cache_file = os.path.expanduser("~/.tracker_app/task_cache.json")
        self.cache_dir = os.path.dirname(self.cache_file)
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # In-memory cache
        self.cached_tasks = {}
        self.last_fetch_time = None
        self.last_fetch_timestamp = None
        
        # Load cached tasks
        self._load_cache()
    
    def check_for_new_tasks(self) -> Dict:
        """
        Poll API for new or updated tasks
        Returns: Dict with new tasks, updated tasks, and total count
        """
        try:
            # Fetch tasks from API
            response = api_post(
                "/tasks/get",
                json_data={"id": self.employee_id, "active_token": self.token},
                timeout=5
            )
            
            if response.status_code != 200:
                return {
                    'status': False,
                    'error': f'API returned status {response.status_code}',
                    'offline': True
                }
            
            # Parse response
            data = response.json()
            
            if not data.get('status'):
                return {
                    'status': False,
                    'error': data.get('message', 'Unknown error'),
                    'offline': False
                }
            
            all_tasks = data.get('data', [])
            new_tasks = [t for t in all_tasks if t.get('status') != 'DONE']
            
            # Compare with cached tasks
            new_task_ids = {task['id'] for task in new_tasks}
            old_task_ids = set(self.cached_tasks.keys())
            
            newly_added = new_task_ids - old_task_ids
            removed_tasks = old_task_ids - new_task_ids
            
            # Update cache
            self.cached_tasks = {task['id']: task for task in new_tasks}
            self._save_cache()
            
            self.last_fetch_time = datetime.now()
            
            return {
                'status': True,
                'tasks': new_tasks,
                'newly_added_count': len(newly_added),
                'removed_count': len(removed_tasks),
                'total_count': len(new_tasks),
                'newly_added_ids': list(newly_added),
                'removed_ids': list(removed_tasks),
                'timestamp': datetime.now().isoformat()
            }
            
        except requests.exceptions.ConnectionError:
            # Network error - return cached data
            return {
                'status': True,
                'tasks': list(self.cached_tasks.values()),
                'offline': True,
                'message': 'Offline - Using cached tasks',
                'cached_task_count': len(self.cached_tasks),
                'last_sync': self.last_fetch_time.isoformat() if self.last_fetch_time else None
            }
        except Exception as e:
            return {
                'status': False,
                'error': str(e),
                'offline': True
            }
    
    def get_task_by_id(self, task_id: int) -> Optional[Dict]:
        """Get a specific task from cache"""
        return self.cached_tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Dict]:
        """Get all cached tasks"""
        return list(self.cached_tasks.values())
    
    def update_task_progress(self, task_id: int, progress_percentage: int, 
                            notes: str = "", occupancy_status: str = "ACTIVE") -> Dict:
        """
        Update task progress via API
        
        Args:
            task_id: ID of task to update
            progress_percentage: Progress value 0-100
            notes: Optional notes from employee
            occupancy_status: ACTIVE, IDLE, or OFFLINE
        """
        try:
            _ = notes
            _ = occupancy_status

            if progress_percentage < 0 or progress_percentage > 100:
                return {
                    'status': False,
                    'error': 'Progress must be between 0 and 100'
                }
            
            new_status = "IN_PROGRESS" if 0 < progress_percentage < 100 else "DONE" if progress_percentage == 100 else "OPEN"
            response = api_post(
                "/tasks/update",
                json_data={
                    "task_id": task_id,
                    "status": new_status,
                    "id": self.employee_id
                },
                timeout=5
            )
            
            if response.status_code != 200:
                return {
                    'status': False,
                    'error': f'API returned status {response.status_code}'
                }
            
            data = response.json()
            
            # Update local cache
            if task_id in self.cached_tasks:
                self.cached_tasks[task_id]['progress_percentage'] = progress_percentage
                self.cached_tasks[task_id]['last_progress_update_at'] = datetime.now().isoformat()
                self._save_cache()
            
            return {
                'status': True,
                'message': data.get('message', 'Progress updated'),
                'task_id': task_id,
                'task_status': data.get('data', {}).get('status', new_status),
                'timestamp': datetime.now().isoformat()
            }
            
        except requests.exceptions.ConnectionError:
            return {
                'status': False,
                'error': 'Network error - Cannot update progress offline',
                'offline': True
            }
        except Exception as e:
            return {
                'status': False,
                'error': str(e)
            }
    
    def complete_task(self, task_id: int, completion_notes: str = "") -> Dict:
        """
        Mark task as complete
        """
        try:
            _ = completion_notes
            response = api_post(
                "/tasks/update",
                json_data={
                    "task_id": task_id,
                    "status": "DONE",
                    "id": self.employee_id
                },
                timeout=5
            )
            
            if response.status_code != 200:
                return {
                    'status': False,
                    'error': f'API returned status {response.status_code}'
                }
            
            data = response.json()
            
            # Update local cache
            if task_id in self.cached_tasks:
                self.cached_tasks[task_id]['status'] = 'DONE'
                self.cached_tasks[task_id]['progress_percentage'] = 100
                self._save_cache()
            
            return {
                'status': True,
                'message': 'Task marked as complete',
                'task_id': task_id,
                'completed_at': data.get('data', {}).get('completed_at'),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': False,
                'error': str(e)
            }
    
    def get_status_info(self) -> Dict:
        """Get current TaskManager status"""
        return {
            'employee_id': self.employee_id,
            'cached_tasks': len(self.cached_tasks),
            'last_sync': self.last_fetch_time.isoformat() if self.last_fetch_time else None,
            'cache_file': self.cache_file,
            'cache_exists': os.path.exists(self.cache_file),
            'timestamp': datetime.now().isoformat()
        }
    
    def force_refresh(self) -> Dict:
        """Force immediate refresh of tasks"""
        # Clear cache
        self.cached_tasks.clear()
        # Fetch from API
        return self.check_for_new_tasks()
    
    def _save_cache(self) -> bool:
        """Save tasks to local cache file"""
        try:
            cache_data = {
                'employee_id': self.employee_id,
                'tasks': self.cached_tasks,
                'cached_at': datetime.now().isoformat(),
                'cache_version': 1
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving task cache: {e}")
            return False
    
    def _load_cache(self) -> bool:
        """Load tasks from local cache file"""
        try:
            if not os.path.exists(self.cache_file):
                return False
            
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            self.cached_tasks = cache_data.get('tasks', {})
            
            # Convert string keys to int
            self.cached_tasks = {
                int(k): v for k, v in self.cached_tasks.items()
            }
            
            return True
        except Exception as e:
            print(f"Error loading task cache: {e}")
            return False


class TaskProgressTracker:
    """
    Tracks task progress and occupancy status in real-time
    Integrates with the tracking system to auto-update progress
    """
    
    def __init__(self, task_manager: TaskManager):
        """Initialize progress tracker"""
        self.task_manager = task_manager
        self.current_task_id = None
        self.task_start_time = None
        self.occupancy_status = "OFFLINE"
    
    def set_current_task(self, task_id: int) -> bool:
        """Set the currently active task"""
        task = self.task_manager.get_task_by_id(task_id)
        if not task:
            return False
        
        self.current_task_id = task_id
        self.task_start_time = datetime.now()
        return True
    
    def update_occupancy(self, status: str) -> None:
        """Update occupancy status (ACTIVE, IDLE, OFFLINE)"""
        self.occupancy_status = status
    
    def track_active_seconds(self, active_seconds: int) -> Optional[Dict]:
        """
        Track active seconds and potentially auto-update progress
        """
        if not self.current_task_id:
            return None
        
        task = self.task_manager.get_task_by_id(self.current_task_id)
        if not task:
            return None
        
        # Example: Auto-increment progress by 1% for every 60 active seconds
        # Can be customized based on requirements
        current_progress = task.get('progress_percentage', 0)
        potential_progress = current_progress + (active_seconds // 60)
        
        # Cap at 99% (user must explicitly mark as complete for 100%)
        new_progress = min(potential_progress, 99)
        
        if new_progress > current_progress:
            return self.task_manager.update_task_progress(
                self.current_task_id,
                new_progress,
                notes=f"Auto-tracked {active_seconds} active seconds",
                occupancy_status=self.occupancy_status
            )
        
        return None
    
    def get_current_task_progress(self) -> Optional[Dict]:
        """Get progress of current task"""
        if not self.current_task_id:
            return None
        return self.task_manager.get_task_by_id(self.current_task_id)
