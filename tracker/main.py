import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
import config
from login_ui import LoginUI
from dashboard_ui import DashboardUI
from loginController import LoginController
from system_tray import SystemTrayIcon

class MainApp(QApplication):
    """
    Main application class inheriting from QApplication.
    This class manages the application lifecycle, initialization, and window switching.
    """
    def __init__(self, argv):
        super().__init__(argv)
        
        # Set application metadata
        self.setApplicationName(config.APP_TITLE)
        self.setWindowIcon(QIcon(config.APP_TRAY_ICON))
        
        # Prevent app from quitting when the last window is closed (minimized to tray)
        # This is crucial for background running capability.
        self.setQuitOnLastWindowClosed(False)
        
        # Ensure necessary folders (screenshots, db) exist
        config.setup_folders()

        # Initialize Login Controller which handles authentication logic
        self.login_ctrl = LoginController(self)

        # Always show login screen on startup (no auto-login)
        # This ensures fresh authentication every time the app is launched
        self.window = LoginUI(self.login_ctrl)
            
        self.window.show()

        # Initialize system tray icon to allow app to run in background
        self.tray_controller = SystemTrayIcon(self, config.APP_TITLE)
        self.tray_controller.show_tray_icon()

if __name__ == "__main__":
    # Entry point of the application
    app = MainApp(sys.argv)
    
    # Ensure session stops on force quit
    import atexit
    def cleanup_on_exit():
        if hasattr(app, 'window') and app.window:
            from dashboard_ui import DashboardUI
            if isinstance(app.window, DashboardUI) and app.window.running:
                try:
                    config.tracking_active = False
                    app.window.ws_controller.stop_session(
                        app.window.emp_id,
                        app.window.session_id,
                        app.window.active_token
                    )
                except Exception:
                    pass
    atexit.register(cleanup_on_exit)
    
    sys.exit(app.exec())
