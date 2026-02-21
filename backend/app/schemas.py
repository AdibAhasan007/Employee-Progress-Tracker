from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginCheckRequest(BaseModel):
    id: int
    token: str


class StartSessionRequest(BaseModel):
    employee_id: int
    active_token: str


class StopSessionRequest(BaseModel):
    session_id: int
    employee_id: int
    active_token: str


class CheckSessionActiveRequest(BaseModel):
    session_id: int
    employee_id: int
    active_token: str


class ActivityApp(BaseModel):
    app_name: Optional[str]
    window_title: Optional[str]
    active_seconds: Optional[int]


class ActivityWebsite(BaseModel):
    domain: Optional[str]
    url: Optional[str]
    active_seconds: Optional[int]


class ActivityLogItem(BaseModel):
    minute_type: Optional[str]
    duration_seconds: Optional[int]


class UploadActivityRequest(BaseModel):
    employee_id: int
    work_session_id: int
    active_token: str
    applications: List[ActivityApp] = []
    websites: List[ActivityWebsite] = []
    activities: List[ActivityLogItem] = []


class UploadScreenshotRequest(BaseModel):
    employee_id: int
    work_session_id: int
    capture_time: Optional[datetime]
    photo: str
    active_token: str


class GetTasksRequest(BaseModel):
    id: int
    active_token: str


class UpdateTaskStatusRequest(BaseModel):
    task_id: int
    status: str
    id: int


class UpdateCompanyPolicyRequest(BaseModel):
    screenshots_enabled: Optional[bool] = None
    website_tracking_enabled: Optional[bool] = None
    app_tracking_enabled: Optional[bool] = None
    screenshot_interval_seconds: Optional[int] = None
    idle_threshold_seconds: Optional[int] = None
    config_sync_interval_seconds: Optional[int] = None
    max_screenshot_size_mb: Optional[int] = None
    screenshot_quality: Optional[int] = None
    enable_keyboard_tracking: Optional[bool] = None
    enable_mouse_tracking: Optional[bool] = None
    enable_idle_detection: Optional[bool] = None
    show_tracker_notification: Optional[bool] = None
    notification_interval_minutes: Optional[int] = None
    local_data_retention_days: Optional[int] = None
