from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from .config import settings
from .routers import api, web

app = FastAPI(title="Employee Progress Tracker", debug=settings.DEBUG)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie=settings.SESSION_COOKIE_NAME,
)

app.include_router(api.router, prefix="/api")
app.include_router(web.router)

if settings.STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")

if settings.MEDIA_ROOT.exists():
    app.mount(settings.MEDIA_URL, StaticFiles(directory=str(settings.MEDIA_ROOT)), name="media")
