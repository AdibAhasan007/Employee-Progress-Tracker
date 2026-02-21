from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship
from .db import Base


class Company(Base):
    __tablename__ = "core_company"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    status = Column(String(20))
    company_key = Column(String(64))


class User(Base):
    __tablename__ = "core_user"

    id = Column(Integer, primary_key=True)
    username = Column(String(150))
    email = Column(String(254))
    first_name = Column(String(150))
    last_name = Column(String(150))
    password = Column(String(256))
    role = Column(String(10))
    designation = Column(String(100))
    is_active = Column(Boolean)
    is_active_employee = Column(Boolean)
    is_staff = Column(Boolean)
    is_superuser = Column(Boolean)
    tracker_token = Column(String(100))
    timezone = Column(String(50))
    profile_picture = Column(String(100))

    department_id = Column(Integer, ForeignKey("core_department.id"))
    last_agent_sync_at = Column(DateTime)

    company_id = Column(Integer, ForeignKey("core_company.id"))
    company = relationship("Company")


class WorkSession(Base):
    __tablename__ = "core_worksession"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("core_company.id"))
    employee_id = Column(Integer, ForeignKey("core_user.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    total_seconds = Column(Integer)
    active_seconds = Column(Integer)
    idle_seconds = Column(Integer)
    created_at = Column(DateTime)


class ApplicationUsage(Base):
    __tablename__ = "core_applicationusage"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("core_company.id"))
    work_session_id = Column(Integer, ForeignKey("core_worksession.id"))
    employee_id = Column(Integer, ForeignKey("core_user.id"))
    app_name = Column(String(255))
    window_title = Column(String(500))
    active_seconds = Column(Integer)
    created_at = Column(DateTime)


class WebsiteUsage(Base):
    __tablename__ = "core_websiteusage"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("core_company.id"))
    work_session_id = Column(Integer, ForeignKey("core_worksession.id"))
    employee_id = Column(Integer, ForeignKey("core_user.id"))
    domain = Column(String(255))
    url = Column(Text)
    active_seconds = Column(Integer)
    created_at = Column(DateTime)


class ActivityLog(Base):
    __tablename__ = "core_activitylog"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("core_company.id"))
    work_session_id = Column(Integer, ForeignKey("core_worksession.id"))
    employee_id = Column(Integer, ForeignKey("core_user.id"))
    minute_type = Column(String(20))
    duration_seconds = Column(Integer)
    created_at = Column(DateTime)


class Screenshot(Base):
    __tablename__ = "core_screenshot"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("core_company.id"))
    work_session_id = Column(Integer, ForeignKey("core_worksession.id"))
    employee_id = Column(Integer, ForeignKey("core_user.id"))
    image = Column(String(100))
    capture_time = Column(DateTime)
    created_at = Column(DateTime)


class Task(Base):
    __tablename__ = "core_task"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("core_company.id"))
    project_id = Column(Integer)
    assigned_to_id = Column(Integer, ForeignKey("core_user.id"))
    assigned_by_id = Column(Integer, ForeignKey("core_user.id"))
    title = Column(String(255))
    description = Column(Text)
    status = Column(String(20))
    priority = Column(String(20))
    start_date = Column(DateTime)
    due_date = Column(DateTime)
    completed_at = Column(DateTime)
    progress_percentage = Column(Integer)
    last_progress_update_at = Column(DateTime)
    last_progress_updated_by_id = Column(Integer)
    success_note = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class TaskProgress(Base):
    __tablename__ = "core_taskprogress"

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("core_task.id"))
    updated_by_id = Column(Integer, ForeignKey("core_user.id"))
    previous_percentage = Column(Integer)
    new_percentage = Column(Integer)
    notes = Column(Text)
    occupancy_status = Column(String(20))
    created_at = Column(DateTime)


class AuditLog(Base):
    __tablename__ = "core_auditlog"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("core_company.id"))
    user_id = Column(Integer, ForeignKey("core_user.id"))
    action_type = Column(String(50))
    description = Column(Text)
    details = Column(Text)
    ip_address = Column(String(45))
    timestamp = Column(DateTime)


class AlertNotification(Base):
    __tablename__ = "core_alertnotification"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("core_company.id"))
    user_id = Column(Integer, ForeignKey("core_user.id"))
    alert_type = Column(String(50))
    title = Column(String(255))
    message = Column(Text)
    related_employee_id = Column(Integer)
    related_data = Column(Text)
    is_read = Column(Boolean)
    is_resolved = Column(Boolean)
    created_at = Column(DateTime)
    read_at = Column(DateTime)
    resolved_at = Column(DateTime)


class Project(Base):
    __tablename__ = "core_project"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("core_company.id"))
    name = Column(String(255))
    description = Column(Text)
    status = Column(String(20))
    created_by_id = Column(Integer, ForeignKey("core_user.id"))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class CompanyBranding(Base):
    __tablename__ = "core_companybranding"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("core_company.id"))
    logo = Column(String(255))
    logo_url = Column(String(500))
    primary_color = Column(String(7))
    secondary_color = Column(String(7))
    accent_color = Column(String(7))
    font_family = Column(String(100))
    custom_domain = Column(String(255))
    email_from_name = Column(String(100))
    email_from_address = Column(String(254))
    email_footer_text = Column(Text)
    login_page_title = Column(String(100))
    login_page_subtitle = Column(String(200))
    login_background_image = Column(String(255))
    company_website = Column(String(500))
    support_email = Column(String(254))
    support_phone = Column(String(20))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class Department(Base):
    __tablename__ = "core_department"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("core_company.id"))
    name = Column(String(100))
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey("core_department.id"))
    head_id = Column(Integer, ForeignKey("core_user.id"))
    budget = Column(Integer)
    cost_center_code = Column(String(50))
    is_active = Column(Boolean)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class Team(Base):
    __tablename__ = "core_team"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("core_company.id"))
    department_id = Column(Integer, ForeignKey("core_department.id"))
    name = Column(String(100))
    description = Column(Text)
    lead_id = Column(Integer, ForeignKey("core_user.id"))
    max_members = Column(Integer)
    is_active = Column(Boolean)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class ProductivityMetric(Base):
    __tablename__ = "core_productivitymetric"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("core_company.id"))
    metric_level = Column(String(20))
    user_id = Column(Integer, ForeignKey("core_user.id"))
    team_id = Column(Integer, ForeignKey("core_team.id"))
    department_id = Column(Integer, ForeignKey("core_department.id"))
    date = Column(DateTime)
    total_work_time = Column(Integer)
    productive_time = Column(Integer)
    idle_time = Column(Integer)
    break_time = Column(Integer)
    total_activities = Column(Integer)
    app_switches = Column(Integer)
    website_visits = Column(Integer)
    productivity_score = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class SSOConfiguration(Base):
    __tablename__ = "core_ssoconfiguration"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("core_company.id"))
    provider = Column(String(20))
    is_enabled = Column(Boolean)
    enforce_sso = Column(Boolean)
    saml_entity_id = Column(String(500))
    saml_sso_url = Column(String(500))
    saml_slo_url = Column(String(500))
    saml_x509_cert = Column(Text)
    oauth_client_id = Column(String(255))
    oauth_client_secret = Column(String(255))
    oauth_authorization_url = Column(String(500))
    oauth_token_url = Column(String(500))
    oauth_user_info_url = Column(String(500))
    role_mapping = Column(Text)
    auto_provision_users = Column(Boolean)
    default_role = Column(String(20))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    last_synced_at = Column(DateTime)


class AnalyticsReport(Base):
    __tablename__ = "core_analyticsreport"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("core_company.id"))
    created_by_id = Column(Integer, ForeignKey("core_user.id"))
    name = Column(String(200))
    description = Column(Text)
    report_type = Column(String(50))
    department_id = Column(Integer)
    team_id = Column(Integer)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    export_format = Column(String(20))
    frequency = Column(String(20))
    next_run_at = Column(DateTime)
    recipients = Column(Text)
    file = Column(String(255))
    file_size = Column(Integer)
    is_active = Column(Boolean)
    last_generated_at = Column(DateTime)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class SubscriptionTier(Base):
    __tablename__ = "core_subscriptiontier"

    id = Column(Integer, primary_key=True)
    tier = Column(String(20))
    name = Column(String(100))
    description = Column(Text)
    stripe_price_id = Column(String(255))
    monthly_cost = Column(Integer)
    annual_cost = Column(Integer)
    max_employees = Column(Integer)
    max_agents = Column(Integer)
    max_storage_gb = Column(Integer)
    screenshot_retention_days = Column(Integer)
    features = Column(Text)
    is_active = Column(Boolean)
    display_order = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class StripeCustomer(Base):
    __tablename__ = "core_stripecustomer"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("core_company.id"))
    stripe_customer_id = Column(String(255))
    email_synced = Column(Boolean)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class StripeBillingSubscription(Base):
    __tablename__ = "core_stripebillingsubscription"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("core_company.id"))
    tier_id = Column(Integer, ForeignKey("core_subscriptiontier.id"))
    stripe_subscription_id = Column(String(255))
    stripe_customer_id = Column(String(255))
    status = Column(String(20))
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    auto_renewal = Column(Boolean)
    default_payment_method_id = Column(String(255))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    cancelled_at = Column(DateTime)


class StripeInvoice(Base):
    __tablename__ = "core_stripeinvoice"

    id = Column(Integer, primary_key=True)
    subscription_id = Column(Integer, ForeignKey("core_stripebillingsubscription.id"))
    company_id = Column(Integer, ForeignKey("core_company.id"))
    stripe_invoice_id = Column(String(255))
    status = Column(String(20))
    amount_due = Column(Integer)
    amount_paid = Column(Integer)
    currency = Column(String(3))
    issued_date = Column(DateTime)
    due_date = Column(DateTime)
    paid_at = Column(DateTime)
    hosted_invoice_url = Column(String(500))
    pdf_url = Column(String(500))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class CompanyPolicy(Base):
    __tablename__ = "core_companypolicy"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("core_company.id"))
    screenshots_enabled = Column(Boolean)
    website_tracking_enabled = Column(Boolean)
    app_tracking_enabled = Column(Boolean)
    screenshot_interval_seconds = Column(Integer)
    idle_threshold_seconds = Column(Integer)
    config_sync_interval_seconds = Column(Integer)
    max_screenshot_size_mb = Column(Integer)
    screenshot_quality = Column(Integer)
    enable_keyboard_tracking = Column(Boolean)
    enable_mouse_tracking = Column(Boolean)
    enable_idle_detection = Column(Boolean)
    show_tracker_notification = Column(Boolean)
    notification_interval_minutes = Column(Integer)
    local_data_retention_days = Column(Integer)
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    config_version = Column(Integer)


class CompanySettings(Base):
    __tablename__ = "core_companysettings"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("core_company.id"))
    company_name = Column(String(200))
    company_tagline = Column(String(500))
    address = Column(Text)
    contact_email = Column(String(254))
    contact_phone = Column(String(30))
    map_embed_url = Column(String(500))
    terms_url = Column(String(500))
    privacy_url = Column(String(500))
    cookies_url = Column(String(500))
    logo = Column(String(100))
    favicon = Column(String(100))
    primary_color = Column(String(7))
    secondary_color = Column(String(7))
    daily_target_hours = Column(Integer)
    idle_threshold_minutes = Column(Integer)
    screenshot_retention_days = Column(Integer)
    employee_limit = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
