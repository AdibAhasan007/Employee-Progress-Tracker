import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QCheckBox, QMessageBox, QFrame, QHBoxLayout, QSpacerItem, QSizePolicy, QSystemTrayIcon)
from PyQt6.QtGui import QPixmap, QFont, QCursor, QCloseEvent, QDesktopServices
from PyQt6.QtCore import Qt, QUrl
import config

class LoginUI(QWidget):
    """
    Login User Interface.
    Provides fields for email and password, and a login button.
    Handles user input and delegates authentication to the LoginController.
    """
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle(config.APP_TITLE)
        self.setFixedSize(config.APP_WIDTH, config.APP_HEIGHT)
        
        # Modern Stylesheet for a clean, professional look
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                font-family: "Segoe UI", sans-serif;
                color: #333333;
            }
            QLabel {
                font-size: 14px;
            }
            QLineEdit {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 14px;
                background-color: #f8f9fa;
                color: #333;
            }
            QLineEdit:focus {
                border: 1px solid #2D8CFF;
                background-color: #ffffff;
            }
            QPushButton {
                background-color: #2D8CFF;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1B6EDC;
            }
            QPushButton:pressed {
                background-color: #155BB5;
            }
            QCheckBox {
                font-size: 13px;
                color: #666666;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background: white;
            }
            QCheckBox::indicator:checked {
                background-color: #2D8CFF;
                border-color: #2D8CFF;
            }
        """)
        
        self.init_ui()

    def init_ui(self):
        """Initializes the layout and widgets of the login screen."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 50, 40, 30)
        main_layout.setSpacing(20)
        self.setLayout(main_layout)

        # ===== Header Section (Logo & Titles) =====
        header_layout = QVBoxLayout()
        header_layout.setSpacing(15)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        # Display Logo prominently at the top
        logo_path = config.LOGO_PATH
        print(f"[DEBUG] Looking for logo at: {logo_path}")
        print(f"[DEBUG] Logo exists: {os.path.exists(logo_path)}")
        
        if os.path.exists(logo_path):
            try:
                logo_label = QLabel()
                pixmap = QPixmap(logo_path)
                
                # Check if pixmap loaded successfully
                if not pixmap.isNull():
                    # Scale logo for maximum visibility
                    pixmap = pixmap.scaled(350, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    logo_label.setPixmap(pixmap)
                    logo_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                    header_layout.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignHCenter)
                    print(f"[DEBUG] Logo loaded successfully: {pixmap.width()}x{pixmap.height()}")
                else:
                    print(f"[DEBUG] Failed to load pixmap from {logo_path}")
            except Exception as e:
                print(f"[DEBUG] Error loading logo: {e}")
        else:
            print(f"[DEBUG] Logo file not found at {logo_path}")
        
        # App Title
        title_label = QLabel(config.LOGIN_PAGE_TITLE)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #222; margin-top: 15px;")
        header_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Subtitle
        subtitle_label = QLabel(config.LOGIN_PAGE_SUBTITLE)
        subtitle_label.setStyleSheet("font-size: 14px; color: #666;")
        header_layout.addWidget(subtitle_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        main_layout.addLayout(header_layout)
        
        # Spacing
        main_layout.addSpacing(10)

        # ===== Form Section (Inputs) =====
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        # Email Input
        email_layout = QVBoxLayout()
        email_layout.setSpacing(6)
        email_label = QLabel("Email Address")
        email_label.setStyleSheet("font-weight: 600; color: #444; font-size: 13px;")
        self.email_entry = QLineEdit()
        self.email_entry.setPlaceholderText("Enter your email")
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_entry)
        form_layout.addLayout(email_layout)

        # Password Input
        pass_layout = QVBoxLayout()
        pass_layout.setSpacing(6)
        pass_label = QLabel("Password")
        pass_label.setStyleSheet("font-weight: 600; color: #444; font-size: 13px;")
        self.password_entry = QLineEdit()
        self.password_entry.setPlaceholderText("Enter your password")
        self.password_entry.setEchoMode(QLineEdit.EchoMode.Password)
        pass_layout.addWidget(pass_label)
        pass_layout.addWidget(self.password_entry)
        form_layout.addLayout(pass_layout)

        # Show Password Checkbox
        self.show_password_cb = QCheckBox("Show password")
        self.show_password_cb.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.show_password_cb.stateChanged.connect(self.toggle_password_visibility)
        form_layout.addWidget(self.show_password_cb)

        main_layout.addLayout(form_layout)
        
        main_layout.addSpacing(10)

        # Login Button
        self.login_button = QPushButton("Sign In")
        self.login_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.login_button.clicked.connect(self.login)
        main_layout.addWidget(self.login_button)
        
        # Spacer to push footer to bottom
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # ===== Footer Section (Credits) =====
        footer_layout = QVBoxLayout()
        footer_layout.setSpacing(4)
        footer_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        # Footer Text with Clickable Company Name
        footer_text_layout = QHBoxLayout()
        footer_text_layout.setSpacing(0)
        footer_text_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        prefix_label = QLabel(config.FOOTER_COMPANY_NAME_PREFIX)
        prefix_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #555;")
        footer_text_layout.addWidget(prefix_label)

        company_link_label = QLabel(config.FOOTER_COMPANY_NAME_LINK)
        company_link_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        # Skype blue color for the link
        company_link_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #00AFF0;") 
        company_link_label.mousePressEvent = self.open_company_website
        footer_text_layout.addWidget(company_link_label)

        footer_layout.addLayout(footer_text_layout)

        footer_credentials_label = QLabel(config.FOOTER_COMPANY_CREDENTIALS)
        footer_credentials_label.setStyleSheet("font-size: 11px; color: #888; font-style: italic;")
        footer_layout.addWidget(footer_credentials_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        main_layout.addLayout(footer_layout)

    def toggle_password_visibility(self):
        """Toggles the password field between hidden (dots) and visible text."""
        if self.show_password_cb.isChecked():
            self.password_entry.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_entry.setEchoMode(QLineEdit.EchoMode.Password)

    def login(self):
        """
        Validates input and initiates the login process via the controller.
        """
        email = self.email_entry.text().strip()
        password = self.password_entry.text().strip()

        if not email or not password:
            QMessageBox.critical(self, "Error", "Enter email and password")
            return

        self.controller.api_login(email, password)

    def open_company_website(self, event):
        """Opens the company website in the default browser."""
        QDesktopServices.openUrl(QUrl(config.FOOTER_COMPANY_URL))

    def closeEvent(self, event: QCloseEvent):
        """
        Overrides the default close event to minimize to system tray instead of quitting.
        """
        event.ignore()
        self.hide()
        if hasattr(self.controller, 'app_context') and hasattr(self.controller.app_context, 'tray_controller'):
             self.controller.app_context.tray_controller.tray_icon.showMessage(
                config.APP_TITLE,
                f"{config.APP_TITLE} Moved to System Tray",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
