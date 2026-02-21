from typing import Optional
import json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..models import (
    User,
    CompanySettings,
    CompanyPolicy,
    AuditLog,
    WorkSession,
    ApplicationUsage,
    WebsiteUsage,
    ActivityLog,
    Screenshot,
    Task,
    TaskProgress,
    Project,
    SubscriptionTier,
    StripeBillingSubscription,
    StripeInvoice,
    Department,
    Team,
    ProductivityMetric,
    CompanyBranding,
    SSOConfiguration,
    AnalyticsReport,
)
from ..auth import verify_password, hash_password

router = APIRouter()

templates = Jinja2Templates(directory=str(settings.TEMPLATE_DIR))


def _get_company_settings(db: Session) -> Optional[CompanySettings]:
    return db.query(CompanySettings).first()


def _get_session_user(db: Session, request: Request) -> Optional[User]:
    user_id = request.session.get("user_id") if hasattr(request, "session") else None
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()


def _require_login(db: Session, request: Request) -> Optional[User]:
    user = _get_session_user(db, request)
    if not user:
        return None
    return user


def _ensure_role(user: User, allowed_roles: list[str]) -> bool:
    return user.role in allowed_roles


@router.get("/")
@router.get("/home/")
def landing(request: Request, db: Session = Depends(get_db)):
    company = _get_company_settings(db)
    return templates.TemplateResponse("landing.html", {"request": request, "company": company})


@router.get("/features/")
def landing_features(request: Request, db: Session = Depends(get_db)):
    company = _get_company_settings(db)
    return templates.TemplateResponse("landing_features.html", {"request": request, "company": company})


@router.get("/benefits/")
def landing_benefits(request: Request, db: Session = Depends(get_db)):
    company = _get_company_settings(db)
    return templates.TemplateResponse("landing_benefits.html", {"request": request, "company": company})


@router.get("/contact/")
def landing_contact(request: Request, db: Session = Depends(get_db)):
    company = _get_company_settings(db)
    return templates.TemplateResponse("landing_contact.html", {"request": request, "company": company})


@router.get("/admin/login/")
def admin_login_get(request: Request, db: Session = Depends(get_db)):
    company = _get_company_settings(db)
    return templates.TemplateResponse("admin_login_new.html", {"request": request, "company": company})


@router.post("/admin/login/")
def admin_login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == username).first()
    if user and verify_password(password, user.password):
        if user.role == "OWNER":
            request.session["user_id"] = user.id
            return RedirectResponse("/owner/dashboard/", status_code=302)
        if user.role in ["ADMIN", "MANAGER"]:
            request.session["user_id"] = user.id
            return RedirectResponse("/dashboard/admin/", status_code=302)
    return templates.TemplateResponse(
        "admin_login_new.html",
        {"request": request, "company": _get_company_settings(db), "error": "Invalid username or password."},
        status_code=401,
    )


@router.get("/user/login/")
def user_login_get(request: Request, db: Session = Depends(get_db)):
    company = _get_company_settings(db)
    return templates.TemplateResponse("user_login_new.html", {"request": request, "company": company})


@router.post("/user/login/")
def user_login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == username).first()
    if user and verify_password(password, user.password):
        request.session["user_id"] = user.id
        if user.role == "EMPLOYEE":
            return RedirectResponse("/dashboard/user/", status_code=302)
        return RedirectResponse("/dashboard/admin/", status_code=302)
    return templates.TemplateResponse(
        "user_login_new.html",
        {"request": request, "company": _get_company_settings(db), "error": "Invalid email or password."},
        status_code=401,
    )


@router.get("/owner/login/")
def owner_login_get(request: Request, db: Session = Depends(get_db)):
    company = _get_company_settings(db)
    return templates.TemplateResponse("owner_login.html", {"request": request, "company": company})


@router.post("/owner/login/")
def owner_login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == username).first()
    if user and verify_password(password, user.password) and user.role == "OWNER":
        request.session["user_id"] = user.id
        return RedirectResponse("/owner/dashboard/", status_code=302)

    return templates.TemplateResponse(
        "owner_login.html",
        {"request": request, "company": _get_company_settings(db), "error": "Access denied."},
        status_code=401,
    )


@router.get("/admin/logout/")
@router.get("/user/logout/")
def logout(request: Request):
    if hasattr(request, "session"):
        request.session.clear()
    return RedirectResponse("/admin/login/", status_code=302)


# ================================
# DASHBOARDS
# ================================


@router.get("/dashboard/")
def dashboard_view(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user:
        return RedirectResponse("/admin/login/", status_code=302)

    if user.role == "OWNER":
        return RedirectResponse("/owner/dashboard/", status_code=302)
    if user.role in ["ADMIN", "MANAGER"]:
        return RedirectResponse("/dashboard/admin/", status_code=302)
    return RedirectResponse("/dashboard/user/", status_code=302)


@router.get("/dashboard/admin/")
def admin_dashboard_view(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or user.role == "OWNER":
        return RedirectResponse("/owner/dashboard/", status_code=302)
    if user.role not in ["ADMIN", "MANAGER"]:
        return RedirectResponse("/dashboard/user/", status_code=302)

    today = datetime.utcnow().date()

    total_employees = (
        db.query(User)
        .filter(User.company_id == user.company_id)
        .filter(User.role == "EMPLOYEE")
        .count()
    )

    todays_sessions = (
        db.query(WorkSession)
        .filter(WorkSession.company_id == user.company_id)
        .filter(func.date(WorkSession.start_time) == today)
        .all()
    )

    active_now_count = len({s.employee_id for s in todays_sessions if s.end_time is None})
    total_sec = sum(s.total_seconds or 0 for s in todays_sessions)
    active_sec = sum(s.active_seconds or 0 for s in todays_sessions)
    idle_sec = sum(s.idle_seconds or 0 for s in todays_sessions)

    def format_hours(seconds: int) -> float:
        return round(seconds / 3600, 1) if seconds else 0

    productivity = round((active_sec / total_sec) * 100, 1) if total_sec > 0 else 0

    employees = (
        db.query(User)
        .filter(User.company_id == user.company_id)
        .filter(User.role == "EMPLOYEE")
        .all()
    )

    employee_status_list = []
    for emp in employees:
        current_session = (
            db.query(WorkSession)
            .filter(WorkSession.employee_id == emp.id)
            .filter(WorkSession.end_time.is_(None))
            .first()
        )
        is_online = current_session is not None

        emp_sessions = (
            db.query(WorkSession)
            .filter(WorkSession.employee_id == emp.id)
            .filter(func.date(WorkSession.start_time) == today)
            .all()
        )
        e_total = sum(s.total_seconds or 0 for s in emp_sessions)
        e_active = sum(s.active_seconds or 0 for s in emp_sessions)

        recent_ss = (
            db.query(Screenshot)
            .filter(Screenshot.employee_id == emp.id)
            .filter(func.date(Screenshot.capture_time) == today)
            .order_by(Screenshot.capture_time.desc())
            .limit(10)
            .all()
        )

        recent_ss_json = [
            {
                "image_url": f"{settings.MEDIA_URL}{ss.image}" if ss.image else "",
                "capture_time": ss.capture_time.strftime("%H:%M") if ss.capture_time else "",
            }
            for ss in recent_ss
        ]

        top_apps = (
            db.query(ApplicationUsage.app_name, func.sum(ApplicationUsage.active_seconds).label("total"))
            .filter(ApplicationUsage.employee_id == emp.id)
            .filter(func.date(ApplicationUsage.created_at) == today)
            .group_by(ApplicationUsage.app_name)
            .order_by(func.sum(ApplicationUsage.active_seconds).desc())
            .limit(5)
            .all()
        )

        top_sites = (
            db.query(WebsiteUsage.domain, func.sum(WebsiteUsage.active_seconds).label("total"))
            .filter(WebsiteUsage.employee_id == emp.id)
            .filter(func.date(WebsiteUsage.created_at) == today)
            .group_by(WebsiteUsage.domain)
            .order_by(func.sum(WebsiteUsage.active_seconds).desc())
            .limit(5)
            .all()
        )

        employee_status_list.append(
            {
                "id": emp.id,
                "name": f"{emp.first_name or ''} {emp.last_name or ''}".strip() or emp.username,
                "email": emp.email,
                "photo": emp.profile_picture,
                "is_online": is_online,
                "total_time": format_hours(e_total),
                "productivity": round((e_active / e_total) * 100) if e_total > 0 else 0,
                "recent_ss": json.dumps(recent_ss_json),
                "recent_ss_list": recent_ss_json,
                "top_apps": [{"app_name": a[0], "total": a[1]} for a in top_apps],
                "top_sites": [{"domain": s[0], "total": s[1]} for s in top_sites],
            }
        )

    context = {
        "request": request,
        "total_employees": total_employees,
        "active_now": active_now_count,
        "total_hours": format_hours(total_sec),
        "active_hours": format_hours(active_sec),
        "idle_hours": format_hours(idle_sec),
        "productivity": productivity,
        "employee_status_list": employee_status_list,
    }
    return templates.TemplateResponse("dashboard.html", context)


@router.get("/dashboard/user/")
def user_dashboard_view(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user:
        return RedirectResponse("/user/login/", status_code=302)
    if user.role == "OWNER":
        return RedirectResponse("/owner/dashboard/", status_code=302)
    if user.role in ["ADMIN", "MANAGER"]:
        return RedirectResponse("/dashboard/admin/", status_code=302)

    today = datetime.utcnow().date()
    sessions = (
        db.query(WorkSession)
        .filter(WorkSession.employee_id == user.id)
        .filter(func.date(WorkSession.start_time) == today)
        .all()
    )
    total_sec = sum(s.total_seconds or 0 for s in sessions)
    active_sec = sum(s.active_seconds or 0 for s in sessions)
    weekly_start = today - timedelta(days=today.weekday())
    weekly_sessions = (
        db.query(WorkSession)
        .filter(WorkSession.employee_id == user.id)
        .filter(func.date(WorkSession.start_time) >= weekly_start)
        .all()
    )
    weekly_total_sec = sum(s.total_seconds or 0 for s in weekly_sessions)

    top_apps = (
        db.query(ApplicationUsage.app_name, func.sum(ApplicationUsage.active_seconds).label("total"))
        .filter(ApplicationUsage.employee_id == user.id)
        .filter(func.date(ApplicationUsage.created_at) == today)
        .group_by(ApplicationUsage.app_name)
        .order_by(func.sum(ApplicationUsage.active_seconds).desc())
        .limit(5)
        .all()
    )

    context = {
        "request": request,
        "total_hours": round(total_sec / 3600, 1) if total_sec else 0,
        "active_hours": round(active_sec / 3600, 1) if active_sec else 0,
        "idle_hours": round((total_sec - active_sec) / 3600, 1) if total_sec else 0,
        "productivity": round((active_sec / total_sec) * 100, 1) if total_sec else 0,
        "weekly_hours": round(weekly_total_sec / 3600, 1) if weekly_total_sec else 0,
        "recent_sessions": sessions[-5:],
        "top_apps": [{"app_name": a[0], "total_time": a[1]} for a in top_apps],
    }
    return templates.TemplateResponse("user_dashboard.html", context)


# ================================
# EMPLOYEES & STAFF
# ================================


@router.get("/employees/")
def employee_list_view(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user:
        return RedirectResponse("/admin/login/", status_code=302)

    employees = (
        db.query(User)
        .filter(User.company_id == user.company_id)
        .filter(User.role == "EMPLOYEE")
        .order_by(User.id.desc())
        .all()
    )
    return templates.TemplateResponse("employee_list.html", {"request": request, "employees": employees})


@router.get("/employees/add/")
def employee_add_view(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user:
        return RedirectResponse("/admin/login/", status_code=302)
    return templates.TemplateResponse("employee_form.html", {"request": request})


@router.post("/employees/add/")
async def employee_add_post(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user:
        return RedirectResponse("/admin/login/", status_code=302)

    form = await request.form()
    email = form.get("email")
    password = form.get("password")
    if not email or not password:
        return RedirectResponse("/employees/add/", status_code=302)

    if db.query(User).filter(User.username == email).first():
        return RedirectResponse("/employees/add/", status_code=302)

    new_user = User(
        username=email,
        email=email,
        first_name=form.get("first_name"),
        last_name=form.get("last_name"),
        role=form.get("role") or "EMPLOYEE",
        designation=form.get("designation"),
        timezone=form.get("timezone") or "UTC",
        is_active_employee=form.get("is_active_employee") == "on",
        is_active=True,
        password=hash_password(password),
        company_id=user.company_id,
    )
    db.add(new_user)
    db.commit()
    return RedirectResponse("/employees/", status_code=302)


@router.get("/employees/{emp_id}/edit/")
def employee_edit_view(request: Request, emp_id: int, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or user.role not in ["ADMIN", "MANAGER"]:
        return RedirectResponse("/dashboard/", status_code=302)

    emp = db.query(User).filter(User.id == emp_id).first()
    return templates.TemplateResponse("employee_form.html", {"request": request, "employee": emp, "is_edit": True})


@router.post("/employees/{emp_id}/edit/")
async def employee_edit_post(request: Request, emp_id: int, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or user.role not in ["ADMIN", "MANAGER"]:
        return RedirectResponse("/dashboard/", status_code=302)

    emp = db.query(User).filter(User.id == emp_id).first()
    if not emp:
        return RedirectResponse("/employees/", status_code=302)

    form = await request.form()
    emp.first_name = form.get("first_name")
    emp.last_name = form.get("last_name")
    new_email = form.get("email")
    if new_email:
        emp.email = new_email
        emp.username = new_email
    emp.role = form.get("role") or emp.role
    emp.designation = form.get("designation")
    emp.timezone = form.get("timezone") or emp.timezone
    emp.is_active_employee = form.get("is_active_employee") == "on"
    new_password = form.get("password")
    if new_password:
        emp.password = hash_password(new_password)
    db.commit()
    return RedirectResponse("/employees/", status_code=302)


@router.post("/employees/{emp_id}/delete/")
def employee_delete_view(request: Request, emp_id: int, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or user.role not in ["ADMIN", "MANAGER"]:
        return RedirectResponse("/dashboard/", status_code=302)

    emp = db.query(User).filter(User.id == emp_id).first()
    if emp and emp.id != user.id:
        db.delete(emp)
        db.commit()
    return RedirectResponse("/employees/", status_code=302)


@router.post("/employees/{emp_id}/toggle-status/")
def employee_toggle_status_view(request: Request, emp_id: int, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or user.role not in ["ADMIN", "MANAGER"]:
        return RedirectResponse("/dashboard/", status_code=302)

    emp = db.query(User).filter(User.id == emp_id).first()
    if emp:
        emp.is_active_employee = not bool(emp.is_active_employee)
        db.commit()
    return RedirectResponse("/employees/", status_code=302)


@router.post("/employees/{emp_id}/reset-password/")
def employee_reset_password_view(request: Request, emp_id: int, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or user.role not in ["ADMIN", "MANAGER"]:
        return RedirectResponse("/dashboard/", status_code=302)

    emp = db.query(User).filter(User.id == emp_id).first()
    if emp:
        emp.password = hash_password("123456")
        db.commit()
    return RedirectResponse("/employees/", status_code=302)


@router.get("/staff/")
def staff_list_view(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or user.role not in ["ADMIN", "MANAGER"]:
        return RedirectResponse("/dashboard/", status_code=302)

    staff = (
        db.query(User)
        .filter(User.company_id == user.company_id)
        .filter(User.role.in_(["ADMIN", "MANAGER"]))
        .order_by(User.id.desc())
        .all()
    )
    return templates.TemplateResponse("staff_list.html", {"request": request, "staff": staff})


@router.get("/staff/add/")
def staff_add_view(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or user.role != "ADMIN":
        return RedirectResponse("/dashboard/", status_code=302)
    return templates.TemplateResponse("staff_form.html", {"request": request})


@router.post("/staff/add/")
async def staff_add_post(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or user.role != "ADMIN":
        return RedirectResponse("/dashboard/", status_code=302)

    form = await request.form()
    email = form.get("email")
    password = form.get("password")
    if not email or not password:
        return RedirectResponse("/staff/add/", status_code=302)

    if db.query(User).filter(User.username == email).first():
        return RedirectResponse("/staff/add/", status_code=302)

    role = form.get("role") or "MANAGER"
    new_user = User(
        username=email,
        email=email,
        first_name=form.get("first_name"),
        last_name=form.get("last_name"),
        role=role,
        designation=form.get("designation"),
        timezone=form.get("timezone") or "UTC",
        is_active_employee=form.get("is_active_employee") == "on",
        is_active=True,
        is_staff=True,
        is_superuser=role == "ADMIN",
        password=hash_password(password),
        company_id=user.company_id,
    )
    db.add(new_user)
    db.commit()
    return RedirectResponse("/staff/", status_code=302)


@router.get("/staff/{staff_id}/edit/")
def staff_edit_view(request: Request, staff_id: int, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or user.role != "ADMIN":
        return RedirectResponse("/dashboard/", status_code=302)

    staff = db.query(User).filter(User.id == staff_id).first()
    return templates.TemplateResponse("staff_form.html", {"request": request, "staff": staff, "is_edit": True})


@router.post("/staff/{staff_id}/edit/")
async def staff_edit_post(request: Request, staff_id: int, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or user.role != "ADMIN":
        return RedirectResponse("/dashboard/", status_code=302)

    staff = db.query(User).filter(User.id == staff_id).first()
    if not staff:
        return RedirectResponse("/staff/", status_code=302)

    form = await request.form()
    new_email = form.get("email")
    if new_email:
        staff.email = new_email
        staff.username = new_email
    staff.first_name = form.get("first_name")
    staff.last_name = form.get("last_name")
    staff.role = form.get("role") or staff.role
    staff.designation = form.get("designation")
    staff.timezone = form.get("timezone") or staff.timezone
    staff.is_active_employee = form.get("is_active_employee") == "on"
    staff.is_staff = True
    staff.is_superuser = staff.role == "ADMIN"
    new_password = form.get("password")
    if new_password:
        staff.password = hash_password(new_password)
    db.commit()
    return RedirectResponse("/staff/", status_code=302)


# ================================
# SESSIONS & SCREENSHOTS & REPORTS
# ================================


@router.get("/sessions/")
def session_list_view(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user:
        return RedirectResponse("/dashboard/", status_code=302)

    sessions = (
        db.query(WorkSession)
        .filter(WorkSession.company_id == user.company_id)
        .order_by(WorkSession.start_time.desc())
        .all()
    )
    employees = db.query(User).filter(User.company_id == user.company_id, User.role == "EMPLOYEE").all()
    return templates.TemplateResponse("session_list.html", {"request": request, "sessions": sessions, "employees": employees})


@router.get("/sessions/{session_id}/")
def session_detail_view(request: Request, session_id: int, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user:
        return RedirectResponse("/dashboard/", status_code=302)

    session = db.query(WorkSession).filter(WorkSession.id == session_id).first()
    apps = db.query(ApplicationUsage).filter(ApplicationUsage.work_session_id == session_id).order_by(ApplicationUsage.active_seconds.desc()).all()
    websites = db.query(WebsiteUsage).filter(WebsiteUsage.work_session_id == session_id).order_by(WebsiteUsage.active_seconds.desc()).all()
    screenshots = db.query(Screenshot).filter(Screenshot.work_session_id == session_id).order_by(Screenshot.capture_time.asc()).all()

    active_time = session.active_seconds if session else 0
    idle_time = session.idle_seconds if session else 0

    def format_time(seconds: int) -> str:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    return templates.TemplateResponse(
        "session_detail.html",
        {
            "request": request,
            "session": session,
            "apps": apps,
            "websites": websites,
            "screenshots": screenshots,
            "active_time_fmt": format_time(active_time),
            "idle_time_fmt": format_time(idle_time),
        },
    )


@router.post("/sessions/{session_id}/end/")
def session_end_view(request: Request, session_id: int, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or user.role not in ["ADMIN", "MANAGER"]:
        return RedirectResponse("/dashboard/", status_code=302)

    session = db.query(WorkSession).filter(WorkSession.id == session_id).first()
    if session and session.end_time is None:
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
    return RedirectResponse(f"/sessions/{session_id}/", status_code=302)


@router.post("/sessions/{session_id}/delete/")
def session_delete_view(request: Request, session_id: int, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or user.role not in ["ADMIN", "MANAGER"]:
        return RedirectResponse("/sessions/", status_code=302)

    session = db.query(WorkSession).filter(WorkSession.id == session_id).first()
    if session:
        db.delete(session)
        db.commit()
    return RedirectResponse("/sessions/", status_code=302)


@router.get("/screenshots/")
def screenshot_gallery_view(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user:
        return RedirectResponse("/dashboard/", status_code=302)

    screenshots = (
        db.query(Screenshot)
        .filter(Screenshot.company_id == user.company_id)
        .order_by(Screenshot.capture_time.desc())
        .all()
    )
    employees = db.query(User).filter(User.company_id == user.company_id, User.role == "EMPLOYEE").all()
    return templates.TemplateResponse("screenshot_gallery.html", {"request": request, "screenshots": screenshots, "employees": employees})


@router.get("/reports/")
def reports_view(request: Request):
    return templates.TemplateResponse("reports.html", {"request": request, "today_date": datetime.utcnow().date(), "current_month": datetime.utcnow().date()})


@router.get("/reports/daily/")
def report_daily_view(request: Request, db: Session = Depends(get_db)):
    date_str = request.query_params.get("date")
    if not date_str:
        return RedirectResponse("/reports/", status_code=302)
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

    employees = db.query(User).filter(User.role == "EMPLOYEE").all()
    report_data = []
    total_worked_all = 0
    total_active_all = 0
    total_idle_all = 0

    for emp in employees:
        sessions = (
            db.query(WorkSession)
            .filter(WorkSession.employee_id == emp.id)
            .filter(func.date(WorkSession.start_time) == date_obj)
            .all()
        )
        if not sessions:
            continue
        total = sum(s.total_seconds or 0 for s in sessions)
        active = sum(s.active_seconds or 0 for s in sessions)
        idle = sum(s.idle_seconds or 0 for s in sessions)
        total_worked_all += total
        total_active_all += active
        total_idle_all += idle

        def fmt(s: int) -> str:
            h = s // 3600
            m = (s % 3600) // 60
            return f"{h:02d}h {m:02d}m"

        report_data.append(
            {
                "employee": emp,
                "first_login": sessions[0].start_time,
                "last_logout": sessions[-1].end_time,
                "total_fmt": fmt(total),
                "active_fmt": fmt(active),
                "idle_fmt": fmt(idle),
                "productivity": round((active / total) * 100, 1) if total > 0 else 0,
            }
        )

    return templates.TemplateResponse(
        "report_daily.html",
        {
            "request": request,
            "date": date_obj,
            "report_data": report_data,
            "total_worked_all": total_worked_all,
            "total_active_all": total_active_all,
            "total_idle_all": total_idle_all,
        },
    )


@router.get("/reports/monthly/")
def report_monthly_view(request: Request, db: Session = Depends(get_db)):
    month_str = request.query_params.get("month")
    if not month_str:
        return RedirectResponse("/reports/", status_code=302)
    year, month = map(int, month_str.split("-"))

    employees = db.query(User).filter(User.role == "EMPLOYEE").all()
    report_data = []
    for emp in employees:
        sessions = (
            db.query(WorkSession)
            .filter(WorkSession.employee_id == emp.id)
            .filter(func.extract("year", WorkSession.start_time) == year)
            .filter(func.extract("month", WorkSession.start_time) == month)
            .all()
        )
        if not sessions:
            continue
        total = sum(s.total_seconds or 0 for s in sessions)
        active = sum(s.active_seconds or 0 for s in sessions)
        idle = sum(s.idle_seconds or 0 for s in sessions)
        days_worked = len({s.start_time.date() for s in sessions})

        report_data.append(
            {
                "employee": emp,
                "days_worked": days_worked,
                "total_hours": round(total / 3600, 1),
                "active_hours": round(active / 3600, 1),
                "idle_hours": round(idle / 3600, 1),
                "avg_daily": round((total / 3600) / days_worked, 1) if days_worked > 0 else 0,
                "productivity": round((active / total) * 100, 1) if total > 0 else 0,
            }
        )

    return templates.TemplateResponse(
        "report_monthly.html",
        {"request": request, "month_label": datetime(year, month, 1).strftime("%B %Y"), "report_data": report_data},
    )


@router.get("/reports/top-apps/")
def report_top_apps_view(request: Request, db: Session = Depends(get_db)):
    top_apps = (
        db.query(ApplicationUsage.app_name, func.sum(ApplicationUsage.active_seconds).label("total_time"))
        .group_by(ApplicationUsage.app_name)
        .order_by(func.sum(ApplicationUsage.active_seconds).desc())
        .limit(10)
        .all()
    )
    top_sites = (
        db.query(WebsiteUsage.domain, func.sum(WebsiteUsage.active_seconds).label("total_time"))
        .group_by(WebsiteUsage.domain)
        .order_by(func.sum(WebsiteUsage.active_seconds).desc())
        .limit(10)
        .all()
    )

    def fmt(s: int) -> str:
        h = s // 3600
        m = (s % 3600) // 60
        return f"{h}h {m}m"

    apps_data = [{"app_name": x[0], "total_fmt": fmt(x[1])} for x in top_apps]
    sites_data = [{"domain": x[0], "total_fmt": fmt(x[1])} for x in top_sites]
    return templates.TemplateResponse(
        "report_top_apps.html",
        {"request": request, "top_apps": apps_data, "top_sites": sites_data, "detailed_sites": []},
    )


@router.get("/my-reports/")
def user_reports_view(request: Request):
    return templates.TemplateResponse("user_reports.html", {"request": request, "today_date": datetime.utcnow().date(), "current_month": datetime.utcnow().date()})


@router.get("/my-reports/daily/")
def user_report_daily_view(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user:
        return RedirectResponse("/user/login/", status_code=302)
    date_str = request.query_params.get("date")
    if not date_str:
        return RedirectResponse("/my-reports/", status_code=302)
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

    sessions = (
        db.query(WorkSession)
        .filter(WorkSession.employee_id == user.id)
        .filter(func.date(WorkSession.start_time) == date_obj)
        .all()
    )
    total = sum(s.total_seconds or 0 for s in sessions)
    active = sum(s.active_seconds or 0 for s in sessions)
    idle = sum(s.idle_seconds or 0 for s in sessions)

    def fmt(s: int) -> str:
        h = s // 3600
        m = (s % 3600) // 60
        return f"{h:02d}h {m:02d}m"

    report_data = [
        {
            "employee": user,
            "first_login": sessions[0].start_time if sessions else None,
            "last_logout": sessions[-1].end_time if sessions else None,
            "total_fmt": fmt(total),
            "active_fmt": fmt(active),
            "idle_fmt": fmt(idle),
            "productivity": round((active / total) * 100, 1) if total > 0 else 0,
        }
    ]

    return templates.TemplateResponse(
        "report_daily.html",
        {"request": request, "date": date_obj, "report_data": report_data, "total_worked_all": total},
    )


@router.get("/my-reports/monthly/")
def user_report_monthly_view(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user:
        return RedirectResponse("/user/login/", status_code=302)
    month_str = request.query_params.get("month")
    if not month_str:
        return RedirectResponse("/my-reports/", status_code=302)
    year, month = map(int, month_str.split("-"))

    sessions = (
        db.query(WorkSession)
        .filter(WorkSession.employee_id == user.id)
        .filter(func.extract("year", WorkSession.start_time) == year)
        .filter(func.extract("month", WorkSession.start_time) == month)
        .all()
    )
    total = sum(s.total_seconds or 0 for s in sessions)
    active = sum(s.active_seconds or 0 for s in sessions)
    idle = sum(s.idle_seconds or 0 for s in sessions)
    days_worked = len({s.start_time.date() for s in sessions})

    report_data = [
        {
            "employee": user,
            "days_worked": days_worked,
            "total_hours": round(total / 3600, 1),
            "active_hours": round(active / 3600, 1),
            "idle_hours": round(idle / 3600, 1),
            "avg_daily": round((total / 3600) / days_worked, 1) if days_worked > 0 else 0,
            "productivity": round((active / total) * 100, 1) if total > 0 else 0,
        }
    ]

    return templates.TemplateResponse(
        "report_monthly.html",
        {"request": request, "month_label": datetime(year, month, 1).strftime("%B %Y"), "report_data": report_data},
    )


# ================================
# TASKS & PROJECTS & SETTINGS
# ================================


@router.get("/tasks/")
def task_list_view(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user:
        return RedirectResponse("/user/login/", status_code=302)

    if user.role == "EMPLOYEE":
        tasks = (
            db.query(Task)
            .filter(Task.assigned_to_id == user.id)
            .filter(Task.company_id == user.company_id)
            .order_by(Task.created_at.desc())
            .all()
        )
    else:
        tasks = (
            db.query(Task)
            .filter(Task.company_id == user.company_id)
            .order_by(Task.created_at.desc())
            .all()
        )
    return templates.TemplateResponse("task_list.html", {"request": request, "tasks": tasks})


@router.get("/tasks/add/")
def task_add_view(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or user.role == "EMPLOYEE":
        return RedirectResponse("/tasks/", status_code=302)

    employees = db.query(User).filter(User.company_id == user.company_id, User.role == "EMPLOYEE").order_by(User.first_name).all()
    return templates.TemplateResponse("task_form.html", {"request": request, "employees": employees, "page": "task-add"})


@router.post("/tasks/add/")
async def task_add_post(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or user.role == "EMPLOYEE":
        return RedirectResponse("/tasks/", status_code=302)

    form = await request.form()
    title = (form.get("title") or "").strip()
    description = (form.get("description") or "").strip()
    assigned_to_id = form.get("assigned_to")
    due_date_raw = form.get("due_date")
    project_id = form.get("project")

    if not title or not assigned_to_id:
        return RedirectResponse("/tasks/add/", status_code=302)

    due_date = None
    if due_date_raw:
        try:
            due_date = datetime.fromisoformat(due_date_raw)
        except ValueError:
            due_date = None

    task = Task(
        company_id=user.company_id,
        project_id=int(project_id) if project_id else None,
        title=title,
        description=description,
        assigned_to_id=int(assigned_to_id),
        assigned_by_id=user.id,
        due_date=due_date,
        status="PENDING",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(task)
    db.commit()
    return RedirectResponse("/tasks/", status_code=302)


@router.post("/tasks/{task_id}/update/")
async def task_update_status_view(request: Request, task_id: int, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user:
        return RedirectResponse("/tasks/", status_code=302)

    form = await request.form()
    status = form.get("status")
    task = db.query(Task).filter(Task.id == task_id, Task.company_id == user.company_id).first()
    if task and user.id == task.assigned_to_id and status in ["OPEN", "IN_PROGRESS", "DONE"]:
        task.status = status
        if status == "DONE":
            task.completed_at = datetime.utcnow()
        db.commit()
    return RedirectResponse("/tasks/", status_code=302)


@router.post("/tasks/{task_id}/delete/")
def task_delete_view(request: Request, task_id: int, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or user.role not in ["ADMIN", "MANAGER"]:
        return RedirectResponse("/tasks/", status_code=302)

    task = db.query(Task).filter(Task.id == task_id, Task.company_id == user.company_id).first()
    if task:
        db.delete(task)
        db.commit()
    return RedirectResponse("/tasks/", status_code=302)


@router.get("/projects/")
def project_list_view(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or user.role not in ["ADMIN", "OWNER"]:
        return RedirectResponse("/dashboard/", status_code=302)

    projects = db.query(Project).filter(Project.company_id == user.company_id).order_by(Project.created_at.desc()).all()
    return templates.TemplateResponse("project_list.html", {"request": request, "projects": projects, "page": "project-list"})


@router.get("/projects/add/")
def project_add_view(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or user.role not in ["ADMIN", "OWNER"]:
        return RedirectResponse("/dashboard/", status_code=302)
    return templates.TemplateResponse("project_add.html", {"request": request, "page": "project-add"})


@router.post("/projects/add/")
async def project_add_post(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or user.role not in ["ADMIN", "OWNER"]:
        return RedirectResponse("/dashboard/", status_code=302)

    form = await request.form()
    name = (form.get("name") or "").strip()
    description = (form.get("description") or "").strip()
    status = form.get("status") or "ACTIVE"
    start_date = form.get("start_date")
    end_date = form.get("end_date")

    if not name:
        return RedirectResponse("/projects/add/", status_code=302)

    project = Project(
        company_id=user.company_id,
        name=name,
        description=description,
        status=status,
        created_by_id=user.id,
        start_date=start_date,
        end_date=end_date,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(project)
    db.commit()
    return RedirectResponse("/projects/", status_code=302)


@router.get("/projects/{project_id}/")
def project_detail_view(request: Request, project_id: int, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or user.role not in ["ADMIN", "OWNER"]:
        return RedirectResponse("/dashboard/", status_code=302)

    project = db.query(Project).filter(Project.id == project_id, Project.company_id == user.company_id).first()
    tasks = db.query(Task).filter(Task.company_id == user.company_id, Task.project_id == project_id).order_by(Task.created_at.desc()).all()
    total_tasks = len(tasks)
    open_tasks = len([t for t in tasks if t.status == "OPEN"])
    in_progress_tasks = len([t for t in tasks if t.status == "IN_PROGRESS"])
    completed_tasks = len([t for t in tasks if t.status == "DONE"])
    progress_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    context = {
        "request": request,
        "project": project,
        "tasks": tasks,
        "total_tasks": total_tasks,
        "open_tasks": open_tasks,
        "in_progress_tasks": in_progress_tasks,
        "completed_tasks": completed_tasks,
        "progress_percentage": round(progress_percentage, 1),
        "page": "project-detail",
        "employees": [],
        "employee_occupancy": [],
    }
    return templates.TemplateResponse("project_detail.html", context)


@router.get("/projects/{project_id}/edit/")
def project_edit_view(request: Request, project_id: int, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or user.role not in ["ADMIN", "OWNER"]:
        return RedirectResponse("/dashboard/", status_code=302)
    project = db.query(Project).filter(Project.id == project_id, Project.company_id == user.company_id).first()
    return templates.TemplateResponse("project_edit.html", {"request": request, "project": project, "page": "project-edit"})


@router.post("/projects/{project_id}/edit/")
async def project_edit_post(request: Request, project_id: int, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or user.role not in ["ADMIN", "OWNER"]:
        return RedirectResponse("/dashboard/", status_code=302)

    project = db.query(Project).filter(Project.id == project_id, Project.company_id == user.company_id).first()
    if not project:
        return RedirectResponse("/projects/", status_code=302)

    form = await request.form()
    project.name = form.get("name") or project.name
    project.description = form.get("description") or project.description
    project.status = form.get("status") or project.status
    project.start_date = form.get("start_date") or project.start_date
    project.end_date = form.get("end_date") or project.end_date
    project.updated_at = datetime.utcnow()
    db.commit()
    return RedirectResponse("/projects/", status_code=302)


@router.post("/projects/{project_id}/delete/")
def project_delete_view(request: Request, project_id: int, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or user.role not in ["ADMIN", "OWNER"]:
        return RedirectResponse("/dashboard/", status_code=302)
    project = db.query(Project).filter(Project.id == project_id, Project.company_id == user.company_id).first()
    if project:
        db.delete(project)
        db.commit()
    return RedirectResponse("/projects/", status_code=302)


@router.get("/settings/")
def settings_view(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user:
        return RedirectResponse("/admin/login/", status_code=302)
    company_settings = db.query(CompanySettings).first()
    return templates.TemplateResponse("settings.html", {"request": request, "company_settings": company_settings})


@router.post("/settings/")
async def settings_post(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user:
        return RedirectResponse("/admin/login/", status_code=302)

    form = await request.form()
    form_type = form.get("form_type")
    company_settings = db.query(CompanySettings).first()
    if not company_settings:
        company_settings = CompanySettings(company_name="My Company")
        db.add(company_settings)
        db.commit()
        db.refresh(company_settings)

    if form_type == "profile":
        user.first_name = form.get("first_name")
        user.last_name = form.get("last_name")
        user.timezone = form.get("timezone") or user.timezone
        db.commit()
    elif form_type == "company" and user.role == "OWNER":
        company_settings.company_name = form.get("company_name") or company_settings.company_name
        company_settings.company_tagline = form.get("company_tagline") or company_settings.company_tagline
        company_settings.address = form.get("address") or company_settings.address
        company_settings.contact_email = form.get("contact_email") or company_settings.contact_email
        company_settings.contact_phone = form.get("contact_phone") or company_settings.contact_phone
        company_settings.primary_color = form.get("primary_color") or company_settings.primary_color
        company_settings.secondary_color = form.get("secondary_color") or company_settings.secondary_color
        db.commit()
    elif form_type == "password":
        new_password = form.get("new_password")
        confirm_password = form.get("confirm_password")
        if new_password and new_password == confirm_password:
            user.password = hash_password(new_password)
            db.commit()

    return RedirectResponse("/settings/", status_code=302)


@router.get("/account/settings/admin/")
def admin_account_settings(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user:
        return RedirectResponse("/admin/login/", status_code=302)
    return templates.TemplateResponse("admin_account_settings.html", {"request": request, "user": user})


@router.get("/account/settings/employee/")
def employee_account_settings(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user:
        return RedirectResponse("/user/login/", status_code=302)
    return templates.TemplateResponse("employee_account_settings.html", {"request": request, "user": user})


@router.get("/account/change-password/")
def change_password_view(request: Request):
    return templates.TemplateResponse("change_password.html", {"request": request})


@router.get("/account/change-username/")
def change_username_view(request: Request):
    return templates.TemplateResponse("change_username.html", {"request": request})


# ================================
# PHASE 2: Admin Enhancements
# ================================


@router.get("/policy/")
@router.get("/owner/company/{company_id}/policy/")
def policy_configuration_view(request: Request, company_id: int | None = None, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or user.role != "OWNER":
        return RedirectResponse("/admin/login/", status_code=302)

    target_company_id = company_id or user.company_id
    policy = db.query(CompanyPolicy).filter(CompanyPolicy.company_id == target_company_id).first()
    if not policy:
        policy = CompanyPolicy(company_id=target_company_id, config_version=1)
        db.add(policy)
        db.commit()
        db.refresh(policy)

    context = {
        "request": request,
        "policy": policy,
        "page": "policy_configuration",
        "config_version": policy.config_version,
        "last_updated": policy.updated_at,
        "company_id": target_company_id,
    }
    return templates.TemplateResponse("policy_configuration.html", context)


@router.post("/policy/")
@router.post("/owner/company/{company_id}/policy/")
async def policy_configuration_post(
    request: Request,
    company_id: int | None = None,
    db: Session = Depends(get_db),
):
    user = _require_login(db, request)
    if not user or user.role != "OWNER":
        return RedirectResponse("/admin/login/", status_code=302)

    target_company_id = company_id or user.company_id
    policy = db.query(CompanyPolicy).filter(CompanyPolicy.company_id == target_company_id).first()
    if not policy:
        policy = CompanyPolicy(company_id=target_company_id, config_version=1)
        db.add(policy)
        db.commit()
        db.refresh(policy)

    form = await request.form()

    policy.screenshots_enabled = form.get("screenshots_enabled") == "on"
    policy.website_tracking_enabled = form.get("website_tracking_enabled") == "on"
    policy.app_tracking_enabled = form.get("app_tracking_enabled") == "on"
    policy.enable_keyboard_tracking = form.get("enable_keyboard_tracking") == "on"
    policy.enable_mouse_tracking = form.get("enable_mouse_tracking") == "on"
    policy.enable_idle_detection = form.get("enable_idle_detection") == "on"
    policy.show_tracker_notification = form.get("show_tracker_notification") == "on"

    def _safe_int(value: str | None, default: int) -> int:
        try:
            return int(value) if value is not None else default
        except ValueError:
            return default

    policy.screenshot_interval_seconds = max(30, min(3600, _safe_int(form.get("screenshot_interval_seconds"), policy.screenshot_interval_seconds or 600)))
    policy.idle_threshold_seconds = max(60, min(1800, _safe_int(form.get("idle_threshold_seconds"), policy.idle_threshold_seconds or 300)))
    policy.config_sync_interval_seconds = max(5, min(60, _safe_int(form.get("config_sync_interval_seconds"), policy.config_sync_interval_seconds or 10)))
    policy.max_screenshot_size_mb = max(1, min(50, _safe_int(form.get("max_screenshot_size_mb"), policy.max_screenshot_size_mb or 5)))
    policy.screenshot_quality = max(50, min(95, _safe_int(form.get("screenshot_quality"), policy.screenshot_quality or 85)))
    policy.notification_interval_minutes = max(0, min(120, _safe_int(form.get("notification_interval_minutes"), policy.notification_interval_minutes or 30)))
    policy.local_data_retention_days = max(7, min(365, _safe_int(form.get("local_data_retention_days"), policy.local_data_retention_days or 30)))

    policy.config_version = (policy.config_version or 0) + 1
    db.commit()

    return RedirectResponse(f"/owner/company/{target_company_id}/policy/", status_code=302)


@router.get("/audit-logs/")
def audit_log_viewer_view(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or not _ensure_role(user, ["ADMIN", "OWNER"]):
        return RedirectResponse("/admin/login/", status_code=302)

    logs = (
        db.query(AuditLog)
        .filter(AuditLog.company_id == user.company_id)
        .order_by(AuditLog.timestamp.desc())
        .limit(200)
        .all()
    )

    context = {
        "request": request,
        "logs": logs,
        "page": "audit_logs",
        "action_types": [],
        "users": [],
        "selected_action": None,
        "selected_user": None,
        "date_from": None,
        "date_to": None,
        "search_query": None,
    }
    return templates.TemplateResponse("audit_log_viewer.html", context)


@router.get("/api/dashboard-alerts/")
def dashboard_alerts_api(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or not _ensure_role(user, ["ADMIN", "OWNER"]):
        return JSONResponse({"error": "Permission denied"}, status_code=403)

    offline_agents = (
        db.query(User)
        .filter(User.company_id == user.company_id)
        .filter(User.role == "EMPLOYEE")
        .filter(User.is_active_employee == True)
        .all()
    )

    offline_agents_data = [
        {
            "id": emp.id,
            "username": emp.username,
            "email": emp.email,
            "last_agent_sync_at": emp.last_agent_sync_at,
        }
        for emp in offline_agents
        if emp.last_agent_sync_at is not None
    ]

    never_synced_data = [
        {
            "id": emp.id,
            "username": emp.username,
            "email": emp.email,
        }
        for emp in offline_agents
        if emp.last_agent_sync_at is None
    ]

    recent_logs = (
        db.query(AuditLog)
        .filter(AuditLog.company_id == user.company_id)
        .order_by(AuditLog.timestamp.desc())
        .limit(10)
        .all()
    )
    recent_logs_data = [
        {
            "id": log.id,
            "action_type": log.action_type,
            "description": log.description,
            "timestamp": log.timestamp,
            "user__username": None,
        }
        for log in recent_logs
    ]

    return {
        "status": "success",
        "offline_agents_count": len(offline_agents_data),
        "offline_agents": offline_agents_data,
        "never_synced_count": len(never_synced_data),
        "never_synced_agents": never_synced_data,
        "recent_audit_logs": recent_logs_data,
    }


@router.get("/agent-sync-status/")
def employee_sync_status_view(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or not _ensure_role(user, ["ADMIN", "OWNER", "MANAGER"]):
        return RedirectResponse("/admin/login/", status_code=302)

    employees = (
        db.query(User)
        .filter(User.company_id == user.company_id)
        .filter(User.role == "EMPLOYEE")
        .filter(User.is_active_employee == True)
        .all()
    )

    synced_agents = []
    offline_agents = []
    never_synced_agents = []
    offline_threshold = datetime.utcnow() - timedelta(minutes=15)

    for emp in employees:
        status_data = {
            "id": emp.id,
            "username": emp.username,
            "full_name": f"{emp.first_name or ''} {emp.last_name or ''}".strip(),
            "email": emp.email,
            "last_sync": emp.last_agent_sync_at,
            "is_online": False,
            "minutes_since_sync": 0,
        }
        if emp.last_agent_sync_at is None:
            status_data["status"] = "Never Synced"
            status_data["status_badge"] = "danger"
            never_synced_agents.append(status_data)
        else:
            if emp.last_agent_sync_at > offline_threshold:
                status_data["status"] = "Online"
                status_data["status_badge"] = "success"
                status_data["is_online"] = True
                synced_agents.append(status_data)
            else:
                status_data["status"] = "Offline"
                status_data["status_badge"] = "warning"
                offline_agents.append(status_data)

    context = {
        "request": request,
        "synced_agents": synced_agents,
        "offline_agents": offline_agents,
        "never_synced_agents": never_synced_agents,
        "total_employees": len(employees),
        "online_count": len(synced_agents),
        "offline_count": len(offline_agents),
        "never_synced_count": len(never_synced_agents),
        "page": "sync_status",
    }
    return templates.TemplateResponse("employee_sync_status.html", context)


@router.get("/dashboard/tasks/monitor/")
def admin_task_monitor_view(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or not _ensure_role(user, ["ADMIN", "OWNER"]):
        return RedirectResponse("/admin/login/", status_code=302)

    tasks = (
        db.query(Task)
        .filter(Task.company_id == user.company_id)
        .order_by(Task.created_at.desc())
        .all()
    )

    tasks_data = []
    for task in tasks:
        latest_progress = (
            db.query(TaskProgress)
            .filter(TaskProgress.task_id == task.id)
            .order_by(TaskProgress.created_at.desc())
            .first()
        )
        tasks_data.append(
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "priority": task.priority,
                "progress_percentage": task.progress_percentage,
                "due_date": task.due_date,
                "created_at": task.created_at,
                "last_progress_update_at": task.last_progress_update_at,
                "employee_name": str(task.assigned_to_id),
                "employee_id": task.assigned_to_id,
                "assigned_by": str(task.assigned_by_id) if task.assigned_by_id else "",
                "project_name": "No Project",
                "occupancy_status": latest_progress.occupancy_status if latest_progress else "UNKNOWN",
                "is_overdue": False,
                "progress_history": [],
            }
        )

    context = {
        "request": request,
        "company": user.company_id,
        "tasks": tasks_data,
        "total_tasks": len(tasks_data),
        "pending_count": sum(1 for t in tasks_data if t["status"] in ["PENDING", "OPEN"]),
        "in_progress_count": sum(1 for t in tasks_data if t["status"] == "IN_PROGRESS"),
        "completed_count": sum(1 for t in tasks_data if t["status"] == "DONE"),
        "page": "admin_task_monitor",
    }
    return templates.TemplateResponse("admin_task_monitor.html", context)


@router.get("/dashboard/tasks/assign/")
def admin_task_assign_get(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or not _ensure_role(user, ["ADMIN", "OWNER"]):
        return RedirectResponse("/admin/login/", status_code=302)

    employees = (
        db.query(User)
        .filter(User.company_id == user.company_id)
        .filter(User.role == "EMPLOYEE")
        .all()
    )

    context = {
        "request": request,
        "company": user.company_id,
        "employees": employees,
        "projects": [],
        "page": "admin_task_assign",
    }
    return templates.TemplateResponse("admin_task_assign.html", context)


@router.post("/dashboard/tasks/assign/")
async def admin_task_assign_post(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or not _ensure_role(user, ["ADMIN", "OWNER"]):
        return RedirectResponse("/admin/login/", status_code=302)

    form = await request.form()
    title = (form.get("title") or "").strip()
    description = (form.get("description") or "").strip()
    employee_id = form.get("employee_id")
    project_id = form.get("project_id")
    due_date_raw = form.get("due_date")
    priority = form.get("priority") or "MEDIUM"

    if not title or not employee_id:
        return JSONResponse({"status": False, "message": "Title and employee are required"}, status_code=400)

    employee = (
        db.query(User)
        .filter(User.id == int(employee_id))
        .filter(User.company_id == user.company_id)
        .filter(User.role == "EMPLOYEE")
        .first()
    )
    if not employee:
        return JSONResponse({"status": False, "message": "Employee not found"}, status_code=404)

    project = None
    if project_id:
        project = db.query(Project).filter(Project.id == int(project_id)).first()

    due_date = None
    if due_date_raw:
        try:
            due_date = datetime.fromisoformat(due_date_raw)
        except ValueError:
            due_date = None

    task = Task(
        company_id=user.company_id,
        project_id=project.id if project else None,
        title=title,
        description=description,
        assigned_to_id=employee.id,
        assigned_by_id=user.id,
        priority=priority,
        due_date=due_date,
        status="PENDING",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return JSONResponse({"status": True, "message": "Task assigned successfully", "task_id": task.id}, status_code=201)


@router.get("/dashboard/tasks/statistics/")
def admin_task_statistics_view(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or not _ensure_role(user, ["ADMIN", "OWNER"]):
        return RedirectResponse("/admin/login/", status_code=302)

    total_tasks = db.query(Task).filter(Task.company_id == user.company_id).count()
    completed_tasks = (
        db.query(Task)
        .filter(Task.company_id == user.company_id, Task.status == "DONE")
        .count()
    )
    in_progress_tasks = (
        db.query(Task)
        .filter(Task.company_id == user.company_id, Task.status == "IN_PROGRESS")
        .count()
    )
    pending_tasks = (
        db.query(Task)
        .filter(Task.company_id == user.company_id, Task.status.in_(["PENDING", "OPEN"]))
        .count()
    )
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    last_24h = datetime.utcnow() - timedelta(hours=24)
    active_updates = (
        db.query(TaskProgress)
        .filter(TaskProgress.created_at >= last_24h)
        .filter(TaskProgress.occupancy_status == "ACTIVE")
        .count()
    )
    idle_updates = (
        db.query(TaskProgress)
        .filter(TaskProgress.created_at >= last_24h)
        .filter(TaskProgress.occupancy_status == "IDLE")
        .count()
    )
    total_updates = active_updates + idle_updates
    active_ratio = (active_updates / total_updates * 100) if total_updates > 0 else 0

    employee_stats = []
    employees = (
        db.query(User)
        .filter(User.company_id == user.company_id)
        .filter(User.role == "EMPLOYEE")
        .all()
    )
    for emp in employees:
        emp_tasks = db.query(Task).filter(Task.assigned_to_id == emp.id)
        pending_count = emp_tasks.filter(Task.status.in_(["PENDING", "OPEN"]))
        pending_count = pending_count.count()
        employee_stats.append(
            {
                "name": f"{emp.first_name or ''} {emp.last_name or ''}".strip() or emp.username,
                "total_assigned": emp_tasks.count(),
                "completed": emp_tasks.filter(Task.status == "DONE").count(),
                "in_progress": emp_tasks.filter(Task.status == "IN_PROGRESS").count(),
                "pending": pending_count,
            }
        )

    context = {
        "request": request,
        "company": user.company_id,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "in_progress_tasks": in_progress_tasks,
        "pending_tasks": pending_tasks,
        "completion_rate": round(completion_rate, 1),
        "active_ratio": round(active_ratio, 1),
        "idle_ratio": round(100 - active_ratio, 1),
        "progress_ranges": {},
        "employee_stats": employee_stats,
        "page": "admin_task_statistics",
    }
    return templates.TemplateResponse("admin_task_statistics.html", context)


# ================================
# PHASE 3: Billing & Subscriptions
# ================================


@router.get("/billing/")
def billing_dashboard_view(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or not _ensure_role(user, ["ADMIN", "OWNER"]):
        return RedirectResponse("/admin/login/", status_code=302)

    subscription = (
        db.query(StripeBillingSubscription)
        .filter(StripeBillingSubscription.company_id == user.company_id)
        .first()
    )
    tiers = db.query(SubscriptionTier).filter(SubscriptionTier.is_active == True).order_by(SubscriptionTier.display_order).all()
    recent_invoices = (
        db.query(StripeInvoice)
        .filter(StripeInvoice.company_id == user.company_id)
        .order_by(StripeInvoice.issued_date.desc())
        .limit(5)
        .all()
    )

    days_until_renewal = None
    if subscription and subscription.current_period_end:
        days_until_renewal = max(0, (subscription.current_period_end - datetime.utcnow()).days)

    context = {
        "request": request,
        "subscription": subscription,
        "tiers": tiers,
        "recent_invoices": recent_invoices,
        "total_employees": 0,
        "active_sessions": 0,
        "days_until_renewal": days_until_renewal,
        "page": "billing",
    }
    return templates.TemplateResponse("billing_dashboard.html", context)


@router.get("/billing/upgrade/")
def upgrade_subscription_view(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or not _ensure_role(user, ["ADMIN", "OWNER"]):
        return RedirectResponse("/admin/login/", status_code=302)

    tiers = db.query(SubscriptionTier).filter(SubscriptionTier.is_active == True).order_by(SubscriptionTier.display_order).all()
    return templates.TemplateResponse("upgrade_subscription.html", {"request": request, "tiers": tiers, "page": "upgrade"})


@router.post("/billing/upgrade/")
async def upgrade_subscription_post(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or not _ensure_role(user, ["ADMIN", "OWNER"]):
        return RedirectResponse("/admin/login/", status_code=302)

    form = await request.form()
    tier_id = form.get("tier_id")
    if tier_id:
        subscription = (
            db.query(StripeBillingSubscription)
            .filter(StripeBillingSubscription.company_id == user.company_id)
            .first()
        )
        if subscription:
            subscription.tier_id = int(tier_id)
            db.commit()
    return RedirectResponse("/billing/", status_code=302)


@router.get("/billing/payment-history/")
def payment_history_view(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or not _ensure_role(user, ["ADMIN", "OWNER"]):
        return RedirectResponse("/admin/login/", status_code=302)

    invoices = (
        db.query(StripeInvoice)
        .filter(StripeInvoice.company_id == user.company_id)
        .order_by(StripeInvoice.issued_date.desc())
        .all()
    )
    return templates.TemplateResponse("payment_history.html", {"request": request, "invoices": invoices, "page": "payment_history"})


@router.get("/billing/settings/")
def billing_settings_view(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or not _ensure_role(user, ["ADMIN", "OWNER"]):
        return RedirectResponse("/admin/login/", status_code=302)

    subscription = (
        db.query(StripeBillingSubscription)
        .filter(StripeBillingSubscription.company_id == user.company_id)
        .first()
    )
    context = {
        "request": request,
        "subscription": subscription,
        "billing_email": user.email,
        "page": "billing_settings",
    }
    return templates.TemplateResponse("billing_settings.html", context)


@router.post("/billing/settings/")
async def billing_settings_post(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or not _ensure_role(user, ["ADMIN", "OWNER"]):
        return RedirectResponse("/admin/login/", status_code=302)

    form = await request.form()
    action = form.get("action")
    subscription = (
        db.query(StripeBillingSubscription)
        .filter(StripeBillingSubscription.company_id == user.company_id)
        .first()
    )
    if action == "toggle_auto_renewal" and subscription:
        subscription.auto_renewal = not bool(subscription.auto_renewal)
        db.commit()
    return RedirectResponse("/billing/settings/", status_code=302)


# ================================
# PHASE 4: Enterprise Features
# ================================


@router.get("/departments/")
def departments_view(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or not _ensure_role(user, ["ADMIN", "OWNER"]):
        return RedirectResponse("/admin/login/", status_code=302)

    departments = (
        db.query(Department)
        .filter(Department.company_id == user.company_id)
        .all()
    )

    dept_stats = []
    for dept in departments:
        employee_count = (
            db.query(User)
            .filter(User.company_id == user.company_id)
            .filter(User.department_id == dept.id)
            .count()
        )
        team_count = db.query(Team).filter(Team.department_id == dept.id).count()
        dept_stats.append({"department": dept, "employee_count": employee_count, "team_count": team_count})

    context = {
        "request": request,
        "departments": departments,
        "dept_stats": dept_stats,
        "all_users": db.query(User).filter(User.company_id == user.company_id).all(),
        "page": "departments",
    }
    return templates.TemplateResponse("departments.html", context)


@router.post("/departments/")
async def departments_post(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or not _ensure_role(user, ["ADMIN", "OWNER"]):
        return RedirectResponse("/admin/login/", status_code=302)

    form = await request.form()
    action = form.get("action")

    if action == "create":
        name = form.get("name")
        description = form.get("description", "")
        parent_id = form.get("parent_id")
        budget = form.get("budget")
        dept = Department(
            company_id=user.company_id,
            name=name,
            description=description,
            parent_id=int(parent_id) if parent_id else None,
            budget=int(budget) if budget else 0,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(dept)
        db.commit()
    elif action == "update":
        dept_id = form.get("dept_id")
        dept = db.query(Department).filter(Department.id == int(dept_id)).first()
        if dept:
            dept.name = form.get("name", dept.name)
            dept.description = form.get("description", dept.description)
            dept.budget = int(form.get("budget", dept.budget or 0))
            dept.updated_at = datetime.utcnow()
            db.commit()
    elif action == "delete":
        dept_id = form.get("dept_id")
        dept = db.query(Department).filter(Department.id == int(dept_id)).first()
        if dept:
            db.delete(dept)
            db.commit()

    return RedirectResponse("/departments/", status_code=302)


@router.get("/teams/")
def teams_view(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or not _ensure_role(user, ["ADMIN", "OWNER", "MANAGER"]):
        return RedirectResponse("/admin/login/", status_code=302)

    teams = (
        db.query(Team)
        .filter(Team.company_id == user.company_id)
        .all()
    )
    departments = db.query(Department).filter(Department.company_id == user.company_id).all()
    employees = db.query(User).filter(User.company_id == user.company_id, User.role == "EMPLOYEE").all()

    context = {
        "request": request,
        "teams": teams,
        "departments": departments,
        "all_users": employees,
        "page": "teams",
    }
    return templates.TemplateResponse("teams.html", context)


@router.post("/teams/")
async def teams_post(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or not _ensure_role(user, ["ADMIN", "OWNER", "MANAGER"]):
        return RedirectResponse("/admin/login/", status_code=302)

    form = await request.form()
    action = form.get("action")

    if action == "create":
        team = Team(
            company_id=user.company_id,
            department_id=int(form.get("department_id")),
            name=form.get("name"),
            description=form.get("description", ""),
            max_members=int(form.get("max_members", 10)),
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(team)
        db.commit()
    elif action == "delete":
        team_id = form.get("team_id")
        team = db.query(Team).filter(Team.id == int(team_id)).first()
        if team:
            db.delete(team)
            db.commit()

    return RedirectResponse("/teams/", status_code=302)


@router.get("/analytics/")
def analytics_dashboard_view(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or not _ensure_role(user, ["ADMIN", "OWNER"]):
        return RedirectResponse("/admin/login/", status_code=302)

    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=30)
    metrics = (
        db.query(ProductivityMetric)
        .filter(ProductivityMetric.company_id == user.company_id)
        .filter(ProductivityMetric.metric_level == "COMPANY")
        .all()
    )

    context = {
        "request": request,
        "company_metrics": metrics,
        "dept_metrics": [],
        "top_users": [],
        "overall_stats": {"avg_productivity": 0, "total_work_hours": 0, "total_employees": 0},
        "start_date": start_date,
        "end_date": end_date,
        "page": "analytics",
    }
    return templates.TemplateResponse("analytics_dashboard.html", context)


@router.get("/analytics/time-utilization/")
def time_utilization_view(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or not _ensure_role(user, ["ADMIN", "OWNER", "MANAGER"]):
        return RedirectResponse("/admin/login/", status_code=302)

    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=7)
    metrics = (
        db.query(ProductivityMetric)
        .filter(ProductivityMetric.company_id == user.company_id)
        .filter(ProductivityMetric.metric_level == "COMPANY")
        .all()
    )

    context = {
        "request": request,
        "metrics": metrics,
        "totals": {},
        "start_date": start_date,
        "end_date": end_date,
        "page": "time-utilization",
    }
    return templates.TemplateResponse("time_utilization.html", context)


@router.get("/analytics/activity-heatmap/")
def activity_heatmap_view(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or not _ensure_role(user, ["ADMIN", "OWNER"]):
        return RedirectResponse("/admin/login/", status_code=302)

    context = {
        "request": request,
        "activities": [],
        "start_date": datetime.utcnow().date(),
        "end_date": datetime.utcnow().date(),
        "page": "activity-heatmap",
    }
    return templates.TemplateResponse("activity_heatmap.html", context)


@router.get("/branding/")
def branding_settings_view(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or not _ensure_role(user, ["ADMIN", "OWNER"]):
        return RedirectResponse("/admin/login/", status_code=302)

    branding = db.query(CompanyBranding).filter(CompanyBranding.company_id == user.company_id).first()
    context = {"request": request, "branding": branding, "page": "branding"}
    return templates.TemplateResponse("branding_settings.html", context)


@router.post("/branding/")
async def branding_settings_post(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or not _ensure_role(user, ["ADMIN", "OWNER"]):
        return RedirectResponse("/admin/login/", status_code=302)

    form = await request.form()
    branding = db.query(CompanyBranding).filter(CompanyBranding.company_id == user.company_id).first()
    if not branding:
        branding = CompanyBranding(company_id=user.company_id)
        db.add(branding)
        db.commit()
        db.refresh(branding)

    action = form.get("action")
    if action == "update_colors":
        branding.primary_color = form.get("primary_color", branding.primary_color)
        branding.secondary_color = form.get("secondary_color", branding.secondary_color)
        branding.accent_color = form.get("accent_color", branding.accent_color)
        branding.updated_at = datetime.utcnow()
        db.commit()

    return RedirectResponse("/branding/", status_code=302)


@router.get("/sso/")
def sso_configuration_view(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or user.role != "OWNER":
        return RedirectResponse("/admin/login/", status_code=302)

    sso_config = db.query(SSOConfiguration).filter(SSOConfiguration.company_id == user.company_id).first()
    context = {"request": request, "sso_config": sso_config, "page": "sso"}
    return templates.TemplateResponse("sso_configuration.html", context)


@router.post("/sso/")
async def sso_configuration_post(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or user.role != "OWNER":
        return RedirectResponse("/admin/login/", status_code=302)

    form = await request.form()
    sso_config = db.query(SSOConfiguration).filter(SSOConfiguration.company_id == user.company_id).first()
    if not sso_config:
        sso_config = SSOConfiguration(company_id=user.company_id, provider=form.get("provider"))
        db.add(sso_config)
        db.commit()
        db.refresh(sso_config)

    action = form.get("action")
    if action == "update_provider":
        sso_config.provider = form.get("provider", sso_config.provider)
        sso_config.is_enabled = form.get("is_enabled") == "true"
        sso_config.enforce_sso = form.get("enforce_sso") == "true"
        sso_config.updated_at = datetime.utcnow()
        db.commit()

    return RedirectResponse("/sso/", status_code=302)


@router.get("/analytics/reports/")
def generate_report_view(request: Request, db: Session = Depends(get_db)):
    user = _require_login(db, request)
    if not user or not _ensure_role(user, ["ADMIN", "OWNER"]):
        return RedirectResponse("/admin/login/", status_code=302)

    reports = (
        db.query(AnalyticsReport)
        .filter(AnalyticsReport.company_id == user.company_id)
        .order_by(AnalyticsReport.created_at.desc())
        .limit(20)
        .all()
    )
    context = {
        "request": request,
        "reports": reports,
        "departments": db.query(Department).filter(Department.company_id == user.company_id).all(),
        "teams": db.query(Team).filter(Team.company_id == user.company_id).all(),
        "page": "reports",
    }
    return templates.TemplateResponse("generate_report.html", context)
