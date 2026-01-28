import sqlite3
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, 
                             QFrame, QHBoxLayout, QTextEdit, QSpacerItem, QSizePolicy, 
                             QSystemTrayIcon, QGraphicsDropShadowEffect, QDialog)
from PyQt6.QtGui import QFont, QCloseEvent, QIcon, QCursor, QDesktopServices, QColor
from PyQt6.QtCore import Qt, QTimer, QUrl
import config
from work_session_controller import WorkSessionController
from screenshot_controller import ScreenshotController
from activity_tracker import start_tracking
import threading
import internet_check

class DashboardUI(QWidget):
    """
    Dashboard User Interface.
    Displays employee info, timer, activity summary, and tasks.
    Allows starting/stopping work sessions and logging out.
    """
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle(config.APP_TITLE)
        self.setFixedSize(config.APP_WIDTH, config.APP_HEIGHT)
        
        # Modern Stylesheet with a light gray background for the main window
        # to make white cards pop.
        self.setStyleSheet("""
            QWidget {
                background-color: #F4F6F9;
                font-family: "Segoe UI", sans-serif;
                color: #333333;
            }
            QLabel {
                background-color: transparent;
            }
            QFrame.Card {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #ffffff;
            }
            QPushButton {
                border: none;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                color: white;
            }
            QTextEdit {
                border: none;
                background-color: #F8F9FA;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
                color: #555;
            }
        """)
        
        # Initialize database connection for reading employee data
        self.db = sqlite3.connect(config.DB_PATH)
        self.cursor = self.db.cursor()

        self.session_id = None   # Stores the current API session ID
        self.running = False     # Tracks if the timer is running
        self.seconds = 0         # Timer seconds counter
        self.task_note = ""      # Store tasks from API
        self.tasks_data = []     # Store task objects for interactive display

        # Initialize controllers for session management and screenshots
        self.ws_controller = WorkSessionController()
        self.ss_controller = ScreenshotController()
        
        # Setup timer for updating the UI clock every second
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        
        # Setup timer to check if session is still active (every 10 seconds)
        self.session_check_timer = QTimer()
        self.session_check_timer.timeout.connect(self.check_session_status)

        self.init_ui()
        
        # Check for stalled sessions from previous crashes
        self.check_and_handle_stalled_session()
        
        self.render_dashboard()

    def init_ui(self):
        """Sets up the main layout container."""
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)
        self.setLayout(self.main_layout)

    def check_and_handle_stalled_session(self):
        """
        Checks if there's a stalled session from a previous crash.
        Shows a dialog asking the user to resume or end the session.
        """
        stalled_session_id = self.controller.check_stalled_session()
        
        if stalled_session_id:
            # Create a message box with explicit buttons
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Previous Session Interrupted")
            msg_box.setText("Your previous session was not properly closed.")
            msg_box.setInformativeText(
                "What would you like to do?\n\n"
                "• Resume: Continue tracking from where you left off\n"
                "• End: Close the previous session and start fresh"
            )
            msg_box.setIcon(QMessageBox.Icon.Information)
            
            # Set minimum width and height to ensure buttons are visible
            msg_box.setMinimumWidth(500)
            msg_box.setMinimumHeight(280)
            
            # Add buttons with explicit text
            resume_btn = msg_box.addButton("Resume Session", QMessageBox.ButtonRole.AcceptRole)
            end_btn = msg_box.addButton("End Session", QMessageBox.ButtonRole.RejectRole)
            
            # Style buttons with visible colors
            button_style = """
                QPushButton {
                    background-color: #667eea;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px 20px;
                    font-size: 13px;
                    font-weight: bold;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background-color: #5568d3;
                }
                QPushButton:pressed {
                    background-color: #4a5ac0;
                }
            """
            resume_btn.setStyleSheet(button_style)
            
            # Style end button differently (red warning color)
            end_button_style = """
                QPushButton {
                    background-color: #ff6b6b;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px 20px;
                    font-size: 13px;
                    font-weight: bold;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background-color: #ff5252;
                }
                QPushButton:pressed {
                    background-color: #ff3838;
                }
            """
            end_btn.setStyleSheet(end_button_style)
            
            # Also style the message box text to be more readable
            msg_style = """
                QMessageBox {
                    background-color: #f5f5f5;
                }
                QMessageBox QLabel {
                    color: #333;
                    font-size: 13px;
                }
            """
            msg_box.setStyleSheet(msg_style)
            
            msg_box.setDefaultButton(resume_btn)
            msg_box.exec()
            
            if msg_box.clickedButton() == resume_btn:
                # Resume the session
                self.session_id = self.controller.resume_session(stalled_session_id)
                print(f"Resumed session: {self.session_id}")
            else:
                # Close the stalled session
                self.controller.close_stalled_session(stalled_session_id)
                print(f"Closed stalled session: {stalled_session_id}")
                self.session_id = None

    def fetch_tasks_from_api(self):
        """Fetch tasks from the backend API"""
        try:
            import requests
            print(f"Fetching tasks for user: {self.emp_id}, Token: {self.active_token}")
            response = requests.post(
                f"{config.API_URL}/tasks/get",
                json={"id": self.emp_id, "active_token": self.active_token},
                timeout=5
            )
            
            print(f"API Response Status: {response.status_code}")
            print(f"API Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status"):
                    self.tasks_data = data.get("data", [])
                    # Format tasks for display
                    task_texts = []
                    for task in self.tasks_data:
                        status_icon = "✓" if task["status"] == "DONE" else "•"
                        task_texts.append(f"{status_icon} {task['title']} [{task['status']}]")
                    
                    self.task_note = "\n".join(task_texts) if task_texts else "No tasks assigned"
                    print(f"Tasks loaded: {self.task_note}")
                else:
                    self.task_note = f"API Error: {data.get('message', 'Unknown error')}"
                    self.tasks_data = []
                    print(f"API returned error: {data.get('message')}")
            else:
                self.task_note = f"HTTP Error {response.status_code}"
                self.tasks_data = []
                print(f"HTTP Error: {response.status_code}")
        except Exception as e:
            print(f"Exception loading tasks: {type(e).__name__}: {e}")
            self.task_note = f"Connection error: {str(e)}"
            self.tasks_data = []
    
    def toggle_task_status(self, task_id, current_status):
        """Toggle task status between OPEN and DONE"""
        try:
            import requests
            
            # Determine new status
            new_status = "OPEN" if current_status == "DONE" else "DONE"
            
            print(f"Updating task {task_id} to {new_status}")
            
            # Call the new API endpoint with proper authentication
            response = requests.post(
                f"{config.API_URL}/tasks/update",
                json={
                    "task_id": task_id,
                    "status": new_status,
                    "id": self.emp_id,
                    "active_token": self.active_token
                },
                timeout=5
            )
            
            if response.status_code == 200:
                # Refresh tasks after update
                self.fetch_tasks_from_api()
                # Refresh UI
                self.clear_main_layout()
                self.render_dashboard()
                print(f"Task {task_id} updated successfully")
            else:
                print(f"Failed to update task: {response.status_code}")
        except Exception as e:
            print(f"Error updating task: {e}")
    
    def show_task_details(self, task):
        """Show detailed information about a task in a dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Task Details - {task['title']}")
        dialog.setMinimumWidth(500)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #F8F9FA;
            }
            QLabel {
                color: #2C3E50;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel(task['title'])
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1F2937;")
        layout.addWidget(title_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setLineWidth(1)
        layout.addWidget(separator)
        
        # Description
        desc_label = QLabel("Description:")
        desc_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #7F8C8D;")
        layout.addWidget(desc_label)
        
        desc_value = QLabel(task.get('description', 'No description provided'))
        desc_value.setWordWrap(True)
        desc_value.setStyleSheet("font-size: 13px; color: #555; padding: 8px; background-color: white; border-radius: 4px;")
        layout.addWidget(desc_value)
        
        # Status
        status_label = QLabel("Status:")
        status_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #7F8C8D;")
        layout.addWidget(status_label)
        
        status_value = QLabel(task['status'])
        status_color = "#10b981" if task['status'] == 'DONE' else "#F59E0B"
        status_value.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {status_color}; padding: 6px 12px; background-color: white; border-radius: 4px; width: fit-content;")
        layout.addWidget(status_value)
        
        # Due Date
        due_date_label = QLabel("Due Date:")
        due_date_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #7F8C8D;")
        layout.addWidget(due_date_label)
        
        due_date_value = QLabel(task.get('due_date', 'No due date') or 'No due date')
        due_date_value.setStyleSheet("font-size: 13px; color: #555; padding: 8px; background-color: white; border-radius: 4px;")
        layout.addWidget(due_date_value)
        
        # Assigned By
        assigned_label = QLabel("Assigned By:")
        assigned_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #7F8C8D;")
        layout.addWidget(assigned_label)
        
        assigned_value = QLabel(task.get('assigned_by', 'Unknown'))
        assigned_value.setStyleSheet("font-size: 13px; color: #555; padding: 8px; background-color: white; border-radius: 4px;")
        layout.addWidget(assigned_value)
        
        # Created At
        created_label = QLabel("Created At:")
        created_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #7F8C8D;")
        layout.addWidget(created_label)
        
        created_value = QLabel(task.get('created_at', 'Unknown')[:10] if task.get('created_at') else 'Unknown')
        created_value.setStyleSheet("font-size: 13px; color: #555; padding: 8px; background-color: white; border-radius: 4px;")
        layout.addWidget(created_value)
        
        # Completed At (if done)
        if task['status'] == 'DONE' and task.get('completed_at'):
            completed_label = QLabel("Completed At:")
            completed_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #7F8C8D;")
            layout.addWidget(completed_label)
            
            completed_value = QLabel(task.get('completed_at', 'Unknown')[:10])
            completed_value.setStyleSheet("font-size: 13px; color: #10b981; padding: 8px; background-color: white; border-radius: 4px;")
            layout.addWidget(completed_value)
        
        layout.addStretch()
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                color: #333;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
        """)
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def clear_main_layout(self):
        """Clear all widgets from main layout"""
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def add_shadow(self, widget):
        """Helper to add a subtle drop shadow to a widget (Card)."""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 15)) # Very subtle shadow
        widget.setGraphicsEffect(shadow)

    def render_dashboard(self):
        """
        Fetches employee data from the local database and populates the UI.
        """
        self.cursor.execute(
            "SELECT id, name, email, company_id, active_token, toddays_worked_time, toddays_active_time, toddays_inactive_time, task_note FROM employee ORDER BY id DESC LIMIT 1"
        )
        emp = self.cursor.fetchone()

        if not emp:
            QMessageBox.critical(self, "Error", "No employee found!")
            return

        # Unpack employee data
        self.emp_id = emp[0]
        self.emp_name = emp[1]
        self.emp_email = emp[2]
        self.company_id = emp[3]
        self.active_token = emp[4]
        self.toddays_worked_time = emp[5]
        self.toddays_active_time = emp[6]
        self.toddays_inactive_time = emp[7]
        self.task_note = emp[8]
        
        # Fetch tasks from API
        self.fetch_tasks_from_api()

        # =========================================
        # CARD 1: Profile & Timer (The Hero Section)
        # =========================================
        hero_card = QFrame()
        hero_card.setProperty("class", "Card")
        self.add_shadow(hero_card)
        hero_layout = QVBoxLayout(hero_card)
        hero_layout.setContentsMargins(20, 20, 20, 20)
        hero_layout.setSpacing(10)

        # Profile Info
        name_label = QLabel(f"Hi, {self.emp_name}")
        name_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2C3E50;")
        name_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        hero_layout.addWidget(name_label)
        
        email_label = QLabel(f"{self.emp_email}")
        email_label.setStyleSheet("font-size: 12px; color: #7F8C8D; margin-bottom: 10px;")
        email_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        hero_layout.addWidget(email_label)

        # Timer Display
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setStyleSheet("""
            font-size: 42px; 
            font-weight: 300; 
            color: #2D8CFF; 
            font-family: 'Segoe UI Light', sans-serif;
            margin: 10px 0;
        """)
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        hero_layout.addWidget(self.timer_label)

        # Control Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        # Only create buttons once
        if not hasattr(self, 'start_btn'):
            self.start_btn = QPushButton("Start Session")
            self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.start_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2ECC71;
                }
                QPushButton:hover {
                    background-color: #27AE60;
                }
                QPushButton:pressed {
                    background-color: #219150;
                }
            """)
            self.start_btn.clicked.connect(self.start_session)
        
        if not hasattr(self, 'stop_btn'):
            self.stop_btn = QPushButton("Stop Session")
            self.stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.stop_btn.setStyleSheet("""
                QPushButton {
                    background-color: #E74C3C;
                }
                QPushButton:hover {
                    background-color: #C0392B;
                }
                QPushButton:pressed {
                    background-color: #A93226;
                }
            """)
            self.stop_btn.clicked.connect(self.stop_session)
        
        # Show/hide buttons based on running state
        if self.running:
            self.start_btn.hide()
            self.stop_btn.show()
        else:
            self.start_btn.show()
            self.stop_btn.hide()
        
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        
        hero_layout.addLayout(btn_layout)
        self.main_layout.addWidget(hero_card)

        # =========================================
        # CARD 2: Today's Summary
        # =========================================
        summary_card = QFrame()
        summary_card.setProperty("class", "Card")
        self.add_shadow(summary_card)
        summary_layout = QVBoxLayout(summary_card)
        summary_layout.setContentsMargins(20, 15, 20, 15)
        summary_layout.setSpacing(8)

        summary_title = QLabel("Today's Activity")
        summary_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #34495E; margin-bottom: 5px;")
        summary_layout.addWidget(summary_title)

        def add_stat_row(icon, label, value, color):
            row = QHBoxLayout()
            
            lbl_text = QLabel(f"{icon}  {label}")
            lbl_text.setStyleSheet("font-size: 13px; color: #7F8C8D;")
            row.addWidget(lbl_text)
            
            lbl_val = QLabel(value)
            lbl_val.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {color};")
            row.addWidget(lbl_val, alignment=Qt.AlignmentFlag.AlignRight)
            
            summary_layout.addLayout(row)

        add_stat_row("⏱", "Total Worked", self.toddays_worked_time, "#2D8CFF")
        add_stat_row("⚡", "Active Time", self.toddays_active_time, "#2ECC71")
        add_stat_row("💤", "Inactive Time", self.toddays_inactive_time, "#E74C3C")

        self.main_layout.addWidget(summary_card)

        # =========================================
        # CARD 3: Tasks
        # =========================================
        if self.task_note and self.task_note.strip() != "":
            task_card = QFrame()
            task_card.setProperty("class", "Card")
            self.add_shadow(task_card)
            task_layout = QVBoxLayout(task_card)
            task_layout.setContentsMargins(20, 15, 20, 15)
            task_layout.setSpacing(12)

            task_title = QLabel("Assigned Tasks")
            task_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #34495E;")
            task_layout.addWidget(task_title)

            # Create a scrollable container for tasks
            task_scroll = QFrame()
            task_scroll.setStyleSheet("""
                QFrame {
                    border: 1px solid #E0E0E0;
                    border-radius: 8px;
                    background-color: #FAFAFA;
                }
            """)
            scroll_layout = QVBoxLayout(task_scroll)
            scroll_layout.setContentsMargins(10, 10, 10, 10)
            scroll_layout.setSpacing(8)
            
            # Parse and display tasks with checkboxes
            if hasattr(self, 'tasks_data') and self.tasks_data:
                for task in self.tasks_data:
                    task_item_layout = QHBoxLayout()
                    task_item_layout.setSpacing(10)
                    
                    # Checkbox button
                    check_btn = QPushButton()
                    check_btn.setFixedSize(24, 24)
                    check_btn.setToolTip(f"Mark '{task['title']}' as done")
                    
                    # Style based on status
                    if task['status'] == 'DONE':
                        check_btn.setStyleSheet("""
                            QPushButton {
                                background-color: #10b981;
                                color: white;
                                border: none;
                                border-radius: 4px;
                                font-weight: bold;
                                font-size: 14px;
                            }
                            QPushButton:hover {
                                background-color: #059669;
                            }
                        """)
                        check_btn.setText("✓")
                    else:
                        check_btn.setStyleSheet("""
                            QPushButton {
                                background-color: #E5E7EB;
                                color: #6B7280;
                                border: 1px solid #D1D5DB;
                                border-radius: 4px;
                                font-weight: bold;
                            }
                            QPushButton:hover {
                                background-color: #D1D5DB;
                            }
                        """)
                        check_btn.setText("○")
                    
                    # Lambda to capture task_id
                    check_btn.clicked.connect(
                        lambda checked, tid=task['id'], tst=task['status']: 
                        self.toggle_task_status(tid, tst)
                    )
                    
                    task_item_layout.addWidget(check_btn)
                    
                    # Task info
                    task_info_layout = QVBoxLayout()
                    task_info_layout.setSpacing(2)
                    
                    # Make task title clickable to show details
                    task_name = QPushButton(task['title'])
                    task_name.setFlat(True)
                    task_name.setCursor(Qt.CursorShape.PointingHandCursor)
                    task_name.setStyleSheet("""
                        QPushButton {
                            font-weight: bold; 
                            color: #1F2937;
                            text-align: left;
                            border: none;
                            padding: 0px;
                        }
                        QPushButton:hover {
                            color: #2D8CFF;
                            text-decoration: underline;
                        }
                    """)
                    task_name.clicked.connect(
                        lambda checked, t=task: self.show_task_details(t)
                    )
                    task_info_layout.addWidget(task_name)
                    
                    task_desc = QLabel(task['status'])
                    task_desc.setStyleSheet("font-size: 11px; color: #9CA3AF;")
                    task_info_layout.addWidget(task_desc)
                    
                    task_item_layout.addLayout(task_info_layout)
                    task_item_layout.addStretch()
                    
                    scroll_layout.addLayout(task_item_layout)
            
            scroll_layout.addStretch()
            task_layout.addWidget(task_scroll)
            task_layout.setStretch(1, 1)  # Make scroll area expandable
            task_card.setMinimumHeight(200)  # Set minimum height

            self.main_layout.addWidget(task_card)

        # Spacer
        self.main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # =========================================
        # Footer
        # =========================================
        footer_layout = QVBoxLayout()
        footer_layout.setSpacing(2)
        footer_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        # Clickable Company Name
        footer_text_layout = QHBoxLayout()
        footer_text_layout.setSpacing(0)
        footer_text_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        prefix_label = QLabel(config.FOOTER_COMPANY_NAME_PREFIX)
        prefix_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #95A5A6;")
        footer_text_layout.addWidget(prefix_label)

        company_link_label = QLabel(config.FOOTER_COMPANY_NAME_LINK)
        company_link_label.setCursor(Qt.CursorShape.PointingHandCursor)
        company_link_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #00AFF0;") 
        company_link_label.mousePressEvent = self.open_company_website
        footer_text_layout.addWidget(company_link_label)

        footer_layout.addLayout(footer_text_layout)

        footer_credentials_label = QLabel(config.FOOTER_COMPANY_CREDENTIALS)
        footer_credentials_label.setStyleSheet("font-size: 10px; color: #BDC3C7; font-style: italic;")
        footer_layout.addWidget(footer_credentials_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.main_layout.addLayout(footer_layout)

        # Logout Link
        logout_btn = QPushButton("Sign Out")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #E74C3C;
                font-size: 12px;
                font-weight: 600;
                padding: 5px;
            }
            QPushButton:hover {
                color: #C0392B;
                text-decoration: underline;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        self.main_layout.addWidget(logout_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

    def start_session(self):
        """
        Starts a new work session.
        Calls the API to create a session, starts the timer, and initiates background tracking threads.
        """
        if self.running:
            return

        session_id, msg = self.ws_controller.start_session(self.emp_id, self.company_id, self.active_token)

        if not session_id:
            QMessageBox.critical(self, "Error", msg)
            return
            
        self.start_btn.hide()
        self.stop_btn.show()
        
        config.tracking_active = True

        self.session_id = session_id
        self.running = True
        self.seconds = 0

        self.timer.start(1000)
        self.session_check_timer.start(10000)  # Check every 10 seconds if session is still active
        
        # Start activity tracking in a background thread
        threading.Thread(
            target=start_tracking,
            args=(self.company_id, self.emp_id, self.active_token, self.session_id),
            daemon=True
        ).start() 

        # Start screenshot capture loop
        self.ss_controller.start_random_capture_loop(
            self.emp_id, self.company_id, self.session_id, self.active_token, self
        )

    def stop_session(self):
        """
        Stops the current work session.
        Calls the API to end the session and stops the timer.
        """
        if not self.running:
            return

        ok, msg = self.ws_controller.stop_session(
            self.emp_id,
            self.session_id,
            self.active_token
        ) 

        if not ok:
            QMessageBox.critical(self, "Error", msg)
            return
            
        self.stop_btn.hide()
        self.start_btn.show()
        config.tracking_active = False

        self.running = False
        self.timer.stop()
        self.session_check_timer.stop()  # Stop checking session status
        QMessageBox.information(self, "Stopped", "Session stopped successfully")

    def check_session_status(self):
        """
        Periodic check to verify if the session is still active on the server.
        If admin ends the session from the web dashboard, this will detect it
        and stop the local session immediately without logging out the user.
        """
        if not self.running or not self.session_id:
            return
        
        try:
            import requests
            response = requests.post(
                f"{config.API_URL}/check-session-active",
                json={
                    "session_id": self.session_id,
                    "employee_id": self.emp_id,
                    "active_token": self.active_token
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                # If session is no longer active on server, stop it locally
                if not data.get("status"):
                    self.auto_stop_session(data.get("message", "Session ended by administrator"))
        except Exception as e:
            # Silent fail - don't disrupt user experience
            print(f"Session check error: {e}")

    def auto_stop_session(self, reason="Session ended"):
        """
        Automatically stops the session without user interaction.
        Used when admin ends the session from web dashboard.
        """
        if not self.running:
            return
        
        self.stop_btn.hide()
        self.start_btn.show()
        config.tracking_active = False
        self.running = False
        self.timer.stop()
        self.session_check_timer.stop()  # Stop checking session status
        
        # Show notification that session was ended
        QMessageBox.warning(self, "Session Ended", f"{reason}\n\nYou can start a new session when ready.")

    def update_timer(self):
        """Updates the timer label every second."""
        if self.running:
            self.seconds += 1
            hrs = self.seconds // 3600
            mins = (self.seconds % 3600) // 60
            secs = self.seconds % 60
            self.timer_label.setText(f"{hrs:02d}:{mins:02d}:{secs:02d}")

    def logout(self):
        """
        Logs out the user.
        Stops any active session and returns to the Login screen.
        """
        if self.running:
            self.stop_session()
            
        self.close()
        from login_ui import LoginUI
        self.login_window = LoginUI(self.controller)
        self.login_window.show()
        if hasattr(self.controller, 'app_context'):
             self.controller.app_context.window = self.login_window

    def open_company_website(self, event):
        """Opens the company website in the default browser."""
        QDesktopServices.openUrl(QUrl(config.FOOTER_COMPANY_URL))

    def after(self, delay_ms, callback):
        """
        Compatibility method for screenshot_controller.
        Mimics Tkinter's root.after() using QTimer.singleShot.
        """
        QTimer.singleShot(delay_ms, callback)

    def closeEvent(self, event: QCloseEvent):
        """
        Overrides close event to minimize to tray instead of quitting.
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
