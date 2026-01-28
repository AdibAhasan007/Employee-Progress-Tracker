# system_tray.py
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction, QPixmap, QColor
import os
import config

class SystemTrayIcon:
    """
    Manages the system tray icon for the application.
    Allows the application to run in the background and provides a context menu.
    """
    def __init__(self, app, app_title="HRSoftBD Tracker"):
        self.app = app
        self.app_title = app_title
        
        # Create the tray icon with a safe fallback if the icon file is missing
        tray_icon = None
        try:
            icon_path = getattr(config, 'APP_TRAY_ICON', None)
            if icon_path and os.path.exists(icon_path):
                tray_icon = QIcon(icon_path)
        except Exception:
            tray_icon = None

        if tray_icon is None or tray_icon.isNull():
            # Fallback: generate a simple blue square icon
            pm = QPixmap(64, 64)
            pm.fill(QColor('#2D8CFF'))
            tray_icon = QIcon(pm)

        self.tray_icon = QSystemTrayIcon(tray_icon, self.app)
        self.tray_icon.setToolTip(self.app_title)
        
        # Create the context menu
        self.menu = QMenu()
        
        # "Open" action to restore the window
        open_action = QAction("Open", self.app)
        open_action.triggered.connect(self._on_open)
        self.menu.addAction(open_action)
        
        # "Exit" action to fully quit the application
        exit_action = QAction("Exit", self.app)
        exit_action.triggered.connect(self._on_exit)
        self.menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(self.menu)
        
        # Handle click events (e.g., double click to open)
        self.tray_icon.activated.connect(self._on_activated)

    def show_tray_icon(self):
        """Makes the tray icon visible."""
        self.tray_icon.show()

    def _on_open(self):
        """Restores the main application window."""
        if hasattr(self.app, 'window') and self.app.window:
            self.app.window.show()
            self.app.window.activateWindow()

    def _on_exit(self):
        """Quits the application and stops any running session."""
        # Stop active session if running
        if hasattr(self.app, 'window') and self.app.window:
            from dashboard_ui import DashboardUI
            if isinstance(self.app.window, DashboardUI) and self.app.window.running:
                try:
                    self.app.window.stop_session()
                except Exception as e:
                    print(f"Error stopping session on exit: {e}")
        self.app.quit()

    def _on_activated(self, reason):
        """Handles tray icon activation (e.g., double click)."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._on_open()

    def stop_tray(self):
        """Hides the tray icon."""
        self.tray_icon.hide()
