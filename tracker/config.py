import image_path
import os
from pathlib import Path

# ==========================================
# Configuration File
# Stores global constants, paths, and settings used throughout the application.
# ==========================================

# Global variable to control the tracking state (True = tracking, False = stopped)
tracking_active = False

# ==========================================
# API Configuration
# ==========================================
# ENVIRONMENT: Set to 'production' or 'local' to switch between servers
ENVIRONMENT = "production"  # Change to "local" for testing with local server

# API URLs
PRODUCTION_API_URL = "https://employee-progress-tracker.onrender.com/api"
LOCAL_API_URL = "http://127.0.0.1:8000/api"

# Auto-select API based on environment
API_URL = PRODUCTION_API_URL if ENVIRONMENT == "production" else LOCAL_API_URL

# Display current mode on startup
print(f"🌐 Running in {ENVIRONMENT.upper()} mode")
print(f"📡 API URL: {API_URL}")

# Faster sync for testing: push activity every 30 seconds
SYNC_ACTIVITY_TIMER = 30
# Capture screenshots within a 2-minute window for quicker visibility
CAPTURE_DURATION = 120

# Application Window Settings
APP_NAME = "Employee Progress Tracker"
APP_TITLE = "Employee Progress Tracker"
APP_WIDTH = 450
APP_HEIGHT = 750
RESIZEABLE = False 

# ==========================
# Logo Configuration
# ==========================
LOGO_WIDTH = 180     # Width of the logo on the login screen
LOGO_HEIGHT = 50     # Height of the logo on the login screen

# UI Text Constants
LOGIN_PAGE_TITLE = "Employee Progress Tracker"
LOGIN_PAGE_SUBTITLE = "Please sign in to continue"

# Footer Text Constants
FOOTER_COMPANY_NAME_PREFIX = "It Support by "
FOOTER_COMPANY_NAME_LINK = "IYLMA Innovation Ltd"
FOOTER_COMPANY_URL = "https://iylma.com/"
FOOTER_COMPANY_CREDENTIALS = "Accelerating your digital transformation."

# File System Paths
HOME_DIR = Path.home()  # User's home directory (cross-platform)
APP_ROOT = HOME_DIR / APP_NAME # Root folder for the app data
# Subfolders for storing specific data
SCREENSHOT_FOLDER = APP_ROOT / "screenshots"
DATABASE_FOLDER = APP_ROOT

# Project and Database Paths
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
DB_NAME = "hrsoftbdTracker.db"
DB_PATH = os.path.join(DATABASE_FOLDER, DB_NAME)

# Image Resource Paths
# Uses image_path helper to resolve paths correctly (especially for PyInstaller builds)
APP_TRAY_ICON = image_path.get_resource_path("icon64.png")
LOGO_PATH = image_path.get_resource_path("logo.png")

# UI Color Constants
BTN_BG_NORMAL = "#2D8CFF"     # Normal button background color (Blue)
BTN_BG_HOVER = "#1B6EDC"      # Button background color on hover
BTN_FG = "white"              # Button text color
BTN_ACTIVE_BG = "#155BB5"     # Button background color when pressed
BTN_ACTIVE_FG = "white"
COLOR_BLACK = "#000000"

# Function to create necessary application folders
def setup_folders():
    """
    Creates the application root, screenshot, and database folders if they don't exist.
    This ensures the app has a place to store its local data.
    """
    for folder in [APP_ROOT, SCREENSHOT_FOLDER, DATABASE_FOLDER]:
        folder.mkdir(parents=True, exist_ok=True)  # create if not exists