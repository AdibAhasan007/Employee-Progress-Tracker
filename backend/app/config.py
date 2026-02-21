from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent  # app/
PROJECT_ROOT = BASE_DIR.parent.parent  # workspace root
BACKEND_DIR = PROJECT_ROOT / "backend"


def _get_env_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


class Settings:
    def __init__(self) -> None:
        self.DEBUG = _get_env_bool(os.getenv("DEBUG"), False)
        self.SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
        self.DATABASE_URL = os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg2://postgres:postgres@localhost:5432/employee_tracker",
        )
        self.ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "*").split(",") if h.strip()]
        self.MEDIA_ROOT = Path(os.getenv("MEDIA_ROOT", str(BACKEND_DIR / "media")))
        self.MEDIA_URL = os.getenv("MEDIA_URL", "/media/")
        self.TEMPLATE_DIR = Path(os.getenv("TEMPLATE_DIR", str(BACKEND_DIR / "templates")))
        self.STATIC_DIR = Path(os.getenv("STATIC_DIR", str(BACKEND_DIR / "static")))
        self.SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "ept_session")


settings = Settings()
