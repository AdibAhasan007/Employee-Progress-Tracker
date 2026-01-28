# Employee Progress Tracker

A desktop application designed to track employee work sessions, monitor activity (applications and websites), and capture periodic screenshots for productivity analysis. Built with Python and PyQt6, it features a modern, clean interface and robust offline synchronization capabilities.

## Overview

The **Employee Progress Tracker** allows employees to log in, start a work timer, and track their productivity. The application runs in the background, minimizing to the system tray, and automatically logs:
*   **Work Duration**: Start and stop times for work sessions.
*   **Activity**: Currently active window titles and website domains.
*   **Screenshots**: Randomly captured screenshots within defined intervals (default: every 5 minutes).

Data is stored locally in an SQLite database and synchronized with a central API server when an internet connection is available.

## Features

*   **User Authentication**: Secure login system validating credentials against a remote API.
*   **Time Tracking**: Simple Start/Stop timer to record work hours.
*   **Activity Monitoring**:
    *   Logs active application window titles.
    *   Detects and logs website domains from browser titles (Chrome, Firefox, Edge).
    *   Distinguishes between Active and Inactive time.
*   **Automated Screenshots**: Captures screenshots at random intervals to verify work progress.
*   **Offline Resilience**: All data is saved locally to SQLite first; background threads handle uploading when online.
*   **System Tray Integration**: Minimizes to the system tray to reduce clutter while running.
*   **Modern UI**: Clean, white-themed interface built with PyQt6, featuring a card-based dashboard layout.

## Tech Stack

*   **Language**: Python 3.x
*   **GUI Framework**: PyQt6
*   **Database**: SQLite (Local storage)
*   **Networking**: `requests` (API communication)
*   **Image Processing**: Pillow (PIL)
*   **System Integration**: `pygetwindow` (Windows active window detection), `subprocess` (Linux fallback).


## Project Structure

```
tracker/
├── main.py                   # Application entry point
├── config.py                 # Global configuration and constants
├── requirements.txt          # Python dependencies
├── db_init.py                # Database initialization script
├── login_ui.py               # Login screen UI
├── dashboard_ui.py           # Main dashboard UI
├── system_tray.py            # System tray icon logic
├── loginController.py        # Authentication logic
├── work_session_controller.py# Session management logic
├── screenshot_controller.py  # Screenshot capture and upload logic
├── activity_tracker.py       # Background activity monitoring
├── internet_check.py         # Connectivity utility
├── image_path.py             # Resource path helper (PyInstaller support)
├── activity_log.py           # Activity data model
├── application_usage.py      # App usage data model
├── website_usage.py          # Website usage data model
└── screenshots/              # Local storage for captured images
```

## Requirements

*   **Python**: 3.8 or higher
*   **Operating System**: Windows (recommended) or Linux.
*   **System Libraries**:
    *   On Linux, `xdotool` is required for active window detection.

## Installation

1.  **Clone the repository**:
    ```sh
    git clone <repository-url>
    cd tracker
    ```

2.  **Create a virtual environment**:
    ```sh
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Linux/Mac
    source .venv/bin/activate
    ```

3.  **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

## Configuration

The application uses `config.py` for global settings. No `.env` file is currently used, but key constants can be modified directly in `config.py` if necessary.

**Key Settings in `config.py`:**
*   `API_URL`: The endpoint for the backend server (Default: `https://tracker.hrsoftbd-omr.com/api`).
*   `SYNC_ACTIVITY_TIMER`: Interval for syncing logs (Default: 300 seconds).
*   `CAPTURE_DURATION`: Interval window for random screenshots (Default: 300 seconds).
*   `FOOTER_COMPANY_URL`: The URL opened when clicking the company name in the footer (Default: `https://iylma.com/`).

## Running the Project

To start the application locally:

1.  Ensure your virtual environment is activated.
2.  Run the entry point script:

```sh
python main.py
```

The application will launch the Login window. If a valid session exists in the local database, it will auto-redirect to the Dashboard.

## Usage

### 1. Login
*   Launch the app.
*   Enter your registered **Email** and **Password**.
*   Click **Sign In**.

### 2. Start Working
*   On the Dashboard, click the green **Start Session** button.
*   The timer will begin counting up.
*   The app will minimize to the system tray if you close the window, continuing to track in the background.

### 3. During the Session
*   **Activity**: The app automatically logs which window is in focus.
*   **Screenshots**: The app silently captures the screen periodically.
*   **Sync**: Data is uploaded to the server every 5 minutes (if online).

### 4. Stop Working
*   Open the app from the system tray or taskbar.
*   Click the red **Stop Session** button.
*   The session end time is logged locally and synced to the server.

### 5. Logout
*   Click **Sign Out** at the bottom of the dashboard to clear your local session and return to the login screen.

## Testing

Currently, there are no automated tests included in the repository. To add tests:

1.  Install `pytest`:
    ```sh
    pip install pytest
    ```
2.  Create a `tests/` directory.
3.  Run tests:
    ```sh
    pytest
    ```

## Troubleshooting

### 1. `ModuleNotFoundError: No module named 'PyQt6'`
*   **Cause**: Dependencies are not installed.
*   **Fix**: Run `pip install -r requirements.txt`.

### 2. Application crashes immediately on start
*   **Cause**: Missing resource files (e.g., `icon64.png`, `logo.png`) or database corruption.
*   **Fix**: Ensure image files exist in the root directory. If the database is corrupt, delete `hrsoftbdTracker.db` (it will be recreated).

### 3. Screenshots are not uploading
*   **Cause**: No internet connection or API server is down.
*   **Fix**: Check your internet connection. The app will retry uploading pending screenshots automatically when connectivity is restored.

### 4. "No Internet Connection Found" in logs
*   **Cause**: The app cannot ping `google.com`.
*   **Fix**: Verify your network adapter settings. The app continues to track locally even without internet.

### 5. Window title detection fails (Linux)
*   **Cause**: Missing `xdotool`.
*   **Fix**: Install it via your package manager (e.g., `sudo apt-get install xdotool`).

## Roadmap

1.  **Encryption**: Encrypt local SQLite database and cached screenshots for enhanced security.
2.  **Settings UI**: Allow users to configure sync intervals or toggle dark mode via the GUI.
3.  **Mac OS Support**: Add specific window detection logic for macOS (Quartz/AppKit).
4.  **Auto-Update**: Implement a mechanism to check for and download app updates.
5.  **Unit Tests**: Add comprehensive test coverage for controllers and database logic.

## License

**Proprietary / All Rights Reserved**
Copyright © IYLMA Innovation Ltd.

## Contact

**Maintainer**: IT Support
**Company**: IYLMA Innovation Ltd
**Website**: https://iylma.com/