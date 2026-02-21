from datetime import datetime
import base64
import os
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from ..db import get_db
from ..models import (
    User,
    WorkSession,
    ApplicationUsage,
    WebsiteUsage,
    ActivityLog,
    Screenshot,
    Task,
    CompanyPolicy,
)
from ..schemas import (
    LoginRequest,
    LoginCheckRequest,
    StartSessionRequest,
    StopSessionRequest,
    CheckSessionActiveRequest,
    UploadActivityRequest,
    UploadScreenshotRequest,
    GetTasksRequest,
    UpdateTaskStatusRequest,
    UpdateCompanyPolicyRequest,
)
from ..auth import verify_password, parse_auth_token, get_user_by_tracker_token
from ..config import settings

router = APIRouter()


def _format_time(seconds: int) -> str:
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def _get_user_from_token(db: Session, request: Request) -> User:
    token = parse_auth_token(request.headers.get("Authorization"))
    if not token:
        raise HTTPException(status_code=403, detail="Missing auth token")
    user = get_user_by_tracker_token(db, token)
    if not user or not user.is_active or not user.is_active_employee:
        raise HTTPException(status_code=403, detail="Invalid token or inactive user")
    return user


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password):
        return JSONResponse({"status": False, "message": "Invalid credentials"}, status_code=401)

    if not user.is_active or not user.is_active_employee:
        return JSONResponse({"status": False, "message": "Account is inactive"}, status_code=403)

    today = datetime.utcnow().date()
    sessions = (
        db.query(WorkSession)
        .filter(WorkSession.employee_id == user.id)
        .filter(func.date(WorkSession.start_time) == today)
        .all()
    )

    total_worked = sum(s.total_seconds or 0 for s in sessions)
    active_time = sum(s.active_seconds or 0 for s in sessions)
    inactive_time = sum(s.idle_seconds or 0 for s in sessions)

    open_tasks = (
        db.query(Task)
        .filter(Task.assigned_to_id == user.id)
        .filter(Task.status.in_(["OPEN", "IN_PROGRESS"]))
        .all()
    )
    task_note = "\n".join([f"- {t.title}" for t in open_tasks])

    data = {
        "id": user.id,
        "name": f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username,
        "email": user.email,
        "company_id": user.company_id or 1,
        "active_token": user.tracker_token,
        "toddays_worked_time": _format_time(total_worked),
        "toddays_active_time": _format_time(active_time),
        "toddays_inactive_time": _format_time(inactive_time),
        "task_note": task_note,
    }
    return {"status": True, "data": data}


@router.post("/login-check")
def login_check(payload: LoginCheckRequest, db: Session = Depends(get_db)):
    exists = (
        db.query(User)
        .filter(User.id == payload.id)
        .filter(User.tracker_token == payload.token)
        .filter(User.is_active == True)
        .filter(User.is_active_employee == True)
        .count()
        > 0
    )
    return {"status": exists}


@router.post("/work-session/create")
def start_session(payload: StartSessionRequest, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(User.id == payload.employee_id)
        .filter(User.tracker_token == payload.active_token)
        .filter(User.is_active_employee == True)
        .filter(User.is_active == True)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session = WorkSession(
        company_id=user.company_id,
        employee_id=user.id,
        start_time=datetime.utcnow(),
        total_seconds=0,
        active_seconds=0,
        idle_seconds=0,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"status": True, "message": "Session started", "data": {"id": session.id}}


@router.post("/work-session/stop")
def stop_session(payload: StopSessionRequest, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(User.id == payload.employee_id)
        .filter(User.tracker_token == payload.active_token)
        .filter(User.is_active_employee == True)
        .filter(User.is_active == True)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session = (
        db.query(WorkSession)
        .filter(WorkSession.id == payload.session_id)
        .filter(WorkSession.employee_id == user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.end_time:
        return JSONResponse({"status": False, "message": "Session already stopped"}, status_code=400)

    session.end_time = datetime.utcnow()
    duration = (session.end_time - session.start_time).total_seconds()
    session.total_seconds = int(duration)

    active_logs = (
        db.query(ActivityLog)
        .filter(ActivityLog.work_session_id == session.id)
        .filter(ActivityLog.minute_type == "ACTIVE")
        .all()
    )
    active_sec = sum(log.duration_seconds or 0 for log in active_logs)
    session.active_seconds = int(active_sec)
    session.idle_seconds = max(0, session.total_seconds - session.active_seconds)

    db.commit()
    return {"status": True, "message": "Session stopped"}


@router.post("/check-session-active")
def check_session_active(payload: CheckSessionActiveRequest, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(User.id == payload.employee_id)
        .filter(User.tracker_token == payload.active_token)
        .filter(User.is_active_employee == True)
        .filter(User.is_active == True)
        .first()
    )
    if not user:
        return JSONResponse({"status": False, "message": "Invalid user"}, status_code=400)

    session = (
        db.query(WorkSession)
        .filter(WorkSession.id == payload.session_id)
        .filter(WorkSession.employee_id == user.id)
        .first()
    )
    if not session:
        return JSONResponse({"status": False, "message": "Session not found"}, status_code=400)

    if session.end_time:
        return {
            "status": False,
            "message": "Session has been ended",
            "reason": "Session ended by administrator",
        }

    return {"status": True, "message": "Session is still active"}


@router.post("/upload/employee-activity")
def upload_activity(payload: UploadActivityRequest, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(User.id == payload.employee_id)
        .filter(User.tracker_token == payload.active_token)
        .filter(User.is_active_employee == True)
        .filter(User.is_active == True)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session = (
        db.query(WorkSession)
        .filter(WorkSession.id == payload.work_session_id)
        .filter(WorkSession.employee_id == user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    for app in payload.applications:
        db.add(
            ApplicationUsage(
                company_id=user.company_id,
                work_session_id=session.id,
                employee_id=user.id,
                app_name=app.app_name,
                window_title=app.window_title,
                active_seconds=app.active_seconds or 0,
                created_at=datetime.utcnow(),
            )
        )

    for site in payload.websites:
        db.add(
            WebsiteUsage(
                company_id=user.company_id,
                work_session_id=session.id,
                employee_id=user.id,
                domain=site.domain,
                url=site.url,
                active_seconds=site.active_seconds or 0,
                created_at=datetime.utcnow(),
            )
        )

    for log in payload.activities:
        db.add(
            ActivityLog(
                company_id=user.company_id,
                work_session_id=session.id,
                employee_id=user.id,
                minute_type=log.minute_type,
                duration_seconds=log.duration_seconds or 0,
                created_at=datetime.utcnow(),
            )
        )

    db.commit()
    return {"status": True, "message": "Data synced"}


@router.post("/screenshot/upload")
def upload_screenshot(payload: UploadScreenshotRequest, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(User.id == payload.employee_id)
        .filter(User.tracker_token == payload.active_token)
        .filter(User.is_active_employee == True)
        .filter(User.is_active == True)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session = (
        db.query(WorkSession)
        .filter(WorkSession.id == payload.work_session_id)
        .filter(WorkSession.employee_id == user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    photo_data = payload.photo
    imgstr = photo_data.split(",", 1)[1] if "," in photo_data else photo_data

    try:
        decoded_image = base64.b64decode(imgstr)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid image data: {exc}")

    capture_time = payload.capture_time or datetime.utcnow()
    filename = f"ss_{session.id}_{datetime.utcnow().timestamp()}.png"
    rel_path = os.path.join("screenshots", capture_time.strftime("%Y/%m/%d"), filename)
    abs_path = settings.MEDIA_ROOT / rel_path
    os.makedirs(abs_path.parent, exist_ok=True)

    with open(abs_path, "wb") as f:
        f.write(decoded_image)

    screenshot = Screenshot(
        company_id=user.company_id,
        work_session_id=session.id,
        employee_id=user.id,
        image=rel_path.replace("\\", "/"),
        capture_time=capture_time,
        created_at=datetime.utcnow(),
    )
    db.add(screenshot)
    db.commit()

    return {"status": True, "message": "Screenshot uploaded"}


@router.post("/tasks/get")
def get_tasks(payload: GetTasksRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    tasks = db.query(Task).filter(Task.assigned_to_id == user.id).order_by(Task.created_at.desc()).all()
    tasks_data = []
    for task in tasks:
        tasks_data.append(
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "assigned_by": str(task.assigned_by_id) if task.assigned_by_id else None,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            }
        )

    return {
        "status": True,
        "data": tasks_data,
        "message": f"Retrieved {len(tasks_data)} tasks",
    }


@router.post("/tasks/update")
def update_task_status(payload: UpdateTaskStatusRequest, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == payload.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.assigned_to_id != payload.id:
        raise HTTPException(status_code=403, detail="Not assigned to this task")

    if payload.status not in ["OPEN", "IN_PROGRESS", "DONE"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    task.status = payload.status
    if payload.status == "DONE":
        task.completed_at = datetime.utcnow()
    db.commit()

    return {
        "status": True,
        "message": f"Task updated to {payload.status}",
        "data": {
            "id": task.id,
            "status": task.status,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        },
    }


@router.get("/session/{session_id}/active_time/")
def session_active_time(session_id: int, db: Session = Depends(get_db)):
    session = db.query(WorkSession).filter(WorkSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.end_time is None:
        duration = int((datetime.utcnow() - session.start_time).total_seconds())
        active_sec = (
            db.query(ActivityLog)
            .filter(ActivityLog.work_session_id == session.id)
            .filter(ActivityLog.minute_type == "ACTIVE")
            .with_entities(ActivityLog.duration_seconds)
            .all()
        )
        active_time = sum(a[0] or 0 for a in active_sec)
        idle_time = max(0, duration - active_time)
    else:
        active_time = session.active_seconds or 0
        idle_time = session.idle_seconds or 0

    return {
        "active_time": active_time,
        "idle_time": idle_time,
        "active_time_fmt": _format_time(active_time),
        "idle_time_fmt": _format_time(idle_time),
    }


@router.get("/employee-config/")
def employee_config(request: Request, db: Session = Depends(get_db)):
    user = _get_user_from_token(db, request)

    policy = db.query(CompanyPolicy).filter(CompanyPolicy.company_id == user.company_id).first()
    if not policy:
        policy = CompanyPolicy(company_id=user.company_id, config_version=1)
        db.add(policy)
        db.commit()
        db.refresh(policy)

    config = {
        "screenshots_enabled": bool(policy.screenshots_enabled),
        "website_tracking_enabled": bool(policy.website_tracking_enabled),
        "app_tracking_enabled": bool(policy.app_tracking_enabled),
        "screenshot_interval_seconds": policy.screenshot_interval_seconds,
        "idle_threshold_seconds": policy.idle_threshold_seconds,
        "config_sync_interval_seconds": policy.config_sync_interval_seconds,
        "max_screenshot_size_mb": policy.max_screenshot_size_mb,
        "screenshot_quality": policy.screenshot_quality,
        "enable_keyboard_tracking": bool(policy.enable_keyboard_tracking),
        "enable_mouse_tracking": bool(policy.enable_mouse_tracking),
        "enable_idle_detection": bool(policy.enable_idle_detection),
        "show_tracker_notification": bool(policy.show_tracker_notification),
        "notification_interval_minutes": policy.notification_interval_minutes,
        "local_data_retention_days": policy.local_data_retention_days,
        "config_version": policy.config_version,
        "updated_at": policy.updated_at.isoformat() if policy.updated_at else None,
    }

    return {
        "status": True,
        "config": config,
        "company": {
            "name": user.company.name if user.company else None,
            "status": user.company.status if user.company else None,
            "is_active": True,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/update-company-policy/")
def update_company_policy(
    payload: UpdateCompanyPolicyRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    user = _get_user_from_token(db, request)
    if user.role != "OWNER":
        raise HTTPException(status_code=403, detail="Only OWNER can update company policy")

    policy = db.query(CompanyPolicy).filter(CompanyPolicy.company_id == user.company_id).first()
    if not policy:
        policy = CompanyPolicy(company_id=user.company_id, config_version=1)
        db.add(policy)
        db.commit()
        db.refresh(policy)

    for field, value in payload.dict(exclude_unset=True).items():
        if value is None:
            continue
        if field.endswith("_enabled"):
            setattr(policy, field, bool(value))
        else:
            setattr(policy, field, int(value))

    policy.config_version = (policy.config_version or 0) + 1
    db.commit()

    return {
        "status": True,
        "message": "Policy updated successfully",
        "config": {
            "config_version": policy.config_version,
        },
    }


@router.post("/stripe/webhook/")
def stripe_webhook_handler():
    return {"status": "ok"}
