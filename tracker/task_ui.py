# ===================================================
# REALTIME TASK MANAGEMENT SYSTEM
# Desktop App Task UI Component
# ===================================================
# PyQt6-based task card display with progress tracking

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QProgressBar, QPushButton, QComboBox, QTextEdit,
    QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QDateTime
from PyQt6.QtGui import QFont, QColor, QPixmap
from datetime import datetime
from typing import Dict, List, Optional


class TaskCard(QFrame):
    """
    Individual task card widget with progress bar and controls
    Displays task details, progress, and allows inline updates
    """
    
    # Signals
    progress_updated = pyqtSignal(int, int, str)  # task_id, progress_percentage, notes
    task_completed = pyqtSignal(int, str)  # task_id, completion_notes
    
    def __init__(self, task_data: Dict, parent=None):
        """
        Initialize task card
        
        Args:
            task_data: Dictionary with task details
            parent: Parent widget
        """
        super().__init__(parent)
        self.task_data = task_data
        self.task_id = task_data.get('id')
        self.current_progress = task_data.get('progress_percentage', 0)
        
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setLineWidth(2)
        self.setStyleSheet(self._get_style())
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI components"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Header: Title and Priority Badge
        header_layout = QHBoxLayout()
        
        title_label = QLabel(self.task_data.get('title', 'Untitled Task'))
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        # Priority badge
        priority = self.task_data.get('priority', 'MEDIUM')
        priority_label = QLabel(priority)
        priority_label.setStyleSheet(self._get_priority_style(priority))
        priority_label.setFixedWidth(80)
        priority_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        header_layout.addStretch()
        header_layout.addWidget(priority_label)
        
        main_layout.addLayout(header_layout)
        
        # Description
        if self.task_data.get('description'):
            desc_label = QLabel(self.task_data['description'])
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #666; font-size: 10px;")
            main_layout.addWidget(desc_label)
        
        # Meta information
        meta_layout = QHBoxLayout()
        
        company = self.task_data.get('company_name', 'Unknown')
        company_label = QLabel(f"🏢 {company}")
        meta_layout.addWidget(company_label)
        
        if self.task_data.get('project_name'):
            project = self.task_data.get('project_name')
            project_label = QLabel(f"📁 {project}")
            meta_layout.addWidget(project_label)
        
        if self.task_data.get('due_date'):
            due_date_str = self.task_data['due_date'][:10]  # Extract date part
            due_label = QLabel(f"📅 Due: {due_date_str}")
            meta_layout.addWidget(due_label)
        
        main_layout.addLayout(meta_layout)
        
        # Progress bar section
        progress_label_layout = QHBoxLayout()
        progress_text = QLabel("Progress:")
        progress_text.setStyleSheet("font-weight: bold;")
        progress_label_layout.addWidget(progress_text)
        
        self.progress_percentage_label = QLabel(f"{self.current_progress}%")
        self.progress_percentage_label.setStyleSheet("font-weight: bold; color: #667eea;")
        progress_label_layout.addWidget(self.progress_percentage_label)
        progress_label_layout.addStretch()
        
        main_layout.addLayout(progress_label_layout)
        
        # Progress bar (clickable/draggable)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(self.current_progress)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                text-align: center;
                height: 30px;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #667eea;
                border-radius: 3px;
            }
        """)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setCursor(Qt.PointingHandCursor)
        self.progress_bar.mousePressEvent = self._on_progress_bar_click
        main_layout.addWidget(self.progress_bar)
        
        # Quick progress buttons
        button_layout = QHBoxLayout()
        for percent in [25, 50, 75, 100]:
            btn = QPushButton(f"{percent}%")
            btn.setMaximumWidth(60)
            btn.clicked.connect(lambda checked, p=percent: self._update_progress(p))
            button_layout.addWidget(btn)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # Status and Actions
        action_layout = QHBoxLayout()
        
        status = self.task_data.get('status', 'PENDING')
        status_label = QLabel(f"Status: {status}")
        status_label.setStyleSheet(self._get_status_style(status))
        action_layout.addWidget(status_label)
        
        # Mark as complete button
        if status != 'DONE':
            complete_btn = QPushButton("✅ Mark Complete")
            complete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4caf50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 15px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            complete_btn.clicked.connect(self._mark_complete)
            action_layout.addWidget(complete_btn)
        
        action_layout.addStretch()
        main_layout.addLayout(action_layout)
        
        # Notes section
        notes_label = QLabel("Notes:")
        notes_label.setStyleSheet("font-weight: bold;")
        main_layout.addWidget(notes_label)
        
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(60)
        self.notes_input.setPlaceholderText("Add notes about your progress...")
        main_layout.addWidget(self.notes_input)
        
        # Update button
        update_btn = QPushButton("Update Progress")
        update_btn.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5568d3;
            }
        """)
        update_btn.clicked.connect(self._send_progress_update)
        main_layout.addWidget(update_btn)
        
        self.setLayout(main_layout)
    
    def _on_progress_bar_click(self, event):
        """Handle progress bar click for quick progress update"""
        bar_width = self.progress_bar.width()
        click_x = event.x()
        percent = int((click_x / bar_width) * 100)
        self._update_progress(percent)
    
    def _update_progress(self, percentage: int):
        """Update progress display"""
        self.current_progress = min(100, max(0, percentage))
        self.progress_bar.setValue(self.current_progress)
        self.progress_percentage_label.setText(f"{self.current_progress}%")
    
    def _send_progress_update(self):
        """Send progress update to server"""
        notes = self.notes_input.toPlainText()
        self.progress_updated.emit(self.task_id, self.current_progress, notes)
        self.notes_input.clear()
    
    def _mark_complete(self):
        """Mark task as complete"""
        notes = self.notes_input.toPlainText()
        self.task_completed.emit(self.task_id, notes)
        self.notes_input.clear()
    
    def _get_style(self) -> str:
        """Get card styling based on task status"""
        status = self.task_data.get('status', 'PENDING')
        
        if status == 'DONE':
            bg_color = "#e8f5e9"
            border_color = "#4caf50"
        elif status == 'IN_PROGRESS':
            bg_color = "#e3f2fd"
            border_color = "#667eea"
        else:
            bg_color = "#fff9c4"
            border_color = "#fbc02d"
        
        return f"""
            background-color: {bg_color};
            border: 3px solid {border_color};
            border-radius: 10px;
        """
    
    def _get_status_style(self, status: str) -> str:
        """Get status label styling"""
        styles = {
            'PENDING': 'background-color: #ffc107; color: white; padding: 5px 10px; border-radius: 3px;',
            'IN_PROGRESS': 'background-color: #667eea; color: white; padding: 5px 10px; border-radius: 3px;',
            'DONE': 'background-color: #4caf50; color: white; padding: 5px 10px; border-radius: 3px;',
        }
        return styles.get(status, 'padding: 5px 10px;')
    
    def _get_priority_style(self, priority: str) -> str:
        """Get priority badge styling"""
        styles = {
            'LOW': 'background-color: #4caf50; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;',
            'MEDIUM': 'background-color: #ffc107; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;',
            'HIGH': 'background-color: #ff9800; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;',
            'URGENT': 'background-color: #f44336; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;',
        }
        return styles.get(priority, 'padding: 5px 10px;')
    
    def update_task_data(self, task_data: Dict):
        """Update task data and refresh display"""
        self.task_data = task_data
        self.current_progress = task_data.get('progress_percentage', 0)
        self.progress_bar.setValue(self.current_progress)
        self.progress_percentage_label.setText(f"{self.current_progress}%")


class TaskCardContainer(QWidget):
    """
    Container widget for displaying multiple task cards with scrolling
    """
    
    # Signals for parent to handle
    progress_updated = pyqtSignal(int, int, str)  # task_id, progress, notes
    task_completed = pyqtSignal(int, str)  # task_id, notes
    
    def __init__(self, parent=None):
        """Initialize container"""
        super().__init__(parent)
        self._setup_ui()
        self.task_cards = {}
        self.setVisible(False)
    
    def _setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("📋 Assigned Tasks")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Scroll area for tasks
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(15)
        self.content_widget.setLayout(self.content_layout)
        scroll.setWidget(self.content_widget)
        layout.addWidget(scroll)
        
        # Empty state
        self.empty_state = QLabel("✅ No pending tasks")
        self.empty_state.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.empty_state.setStyleSheet("color: #999; font-size: 14px;")
        self.empty_state.hide()
        layout.addWidget(self.empty_state)
        
        self.setLayout(layout)
    
    def add_task(self, task_data: Dict):
        """Add a task card"""
        task_id = task_data.get('id')
        
        if task_id not in self.task_cards:
            card = TaskCard(task_data)
            card.progress_updated.connect(self.progress_updated.emit)
            card.task_completed.connect(self.task_completed.emit)
            
            self.task_cards[task_id] = card
            self.content_layout.addWidget(card)
            self.empty_state.hide()
            self.setVisible(True)
    
    def update_task(self, task_data: Dict):
        """Update existing task card"""
        task_id = task_data.get('id')
        
        if task_id in self.task_cards:
            self.task_cards[task_id].update_task_data(task_data)
    
    def remove_task(self, task_id: int):
        """Remove a task card"""
        if task_id in self.task_cards:
            card = self.task_cards[task_id]
            card.deleteLater()
            del self.task_cards[task_id]
            
            if not self.task_cards:
                self.empty_state.show()
                self.setVisible(False)
    
    def clear_all(self):
        """Clear all task cards"""
        for card in self.task_cards.values():
            card.deleteLater()
        self.task_cards.clear()
        self.empty_state.show()
        self.setVisible(False)
    
    def update_all_tasks(self, tasks: List[Dict]):
        """Update all tasks at once"""
        # Get current IDs
        current_ids = set(self.task_cards.keys())
        new_ids = {task.get('id') for task in tasks}
        
        # Remove tasks that no longer exist
        for task_id in current_ids - new_ids:
            self.remove_task(task_id)
        
        # Add or update tasks
        for task in tasks:
            task_id = task.get('id')
            if task_id in self.task_cards:
                self.update_task(task)
            else:
                self.add_task(task)
        
        # Show empty state if no tasks
        if not self.task_cards:
            self.empty_state.show()
            self.setVisible(False)
        else:
            self.empty_state.hide()
            self.setVisible(True)
