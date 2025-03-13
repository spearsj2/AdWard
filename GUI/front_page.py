from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                              QDialog, QListWidget, QLineEdit, QMessageBox,
                              QHBoxLayout, QLabel, QListWidgetItem, QFrame)
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtCore import QUrl, Qt, QSize
from PySide6.QtGui import QPixmap, QIcon, QFont, QColor, QPalette, QFontDatabase
import json
from adward_API import AdwardAPI
from config import AdwardConfig
from config_dialog import ConfigDialog

class StyledButton(QPushButton):
    """Custom styled button class"""
    def __init__(self, text, parent=None, primary=False):
        super().__init__(text, parent)
        self.setMinimumHeight(36)
        self.setCursor(Qt.PointingHandCursor)
        self.primary = primary
        self.apply_style(False)  # Default to light theme
        
    def apply_style(self, dark_mode):
        """Apply appropriate style based on theme"""
        if self.primary:
            if dark_mode:
                self.setStyleSheet("""
                    QPushButton {
                        background-color: #0d6efd;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px 16px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #0b5ed7;
                    }
                    QPushButton:pressed {
                        background-color: #0a58ca;
                    }
                    QPushButton:disabled {
                        background-color: #6c757d;
                        color: #e9ecef;
                    }
                """)
            else:
                self.setStyleSheet("""
                    QPushButton {
                        background-color: #2c3e50;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px 16px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #34495e;
                    }
                    QPushButton:pressed {
                        background-color: #1a252f;
                    }
                    QPushButton:disabled {
                        background-color: #7f8c8d;
                        color: #ecf0f1;
                    }
                """)
        else:
            if dark_mode:
                self.setStyleSheet("""
                    QPushButton {
                        background-color: #343a40;
                        color: #e0e0e0;
                        border: 1px solid #495057;
                        border-radius: 4px;
                        padding: 8px 16px;
                    }
                    QPushButton:hover {
                        background-color: #495057;
                    }
                    QPushButton:pressed {
                        background-color: #212529;
                    }
                    QPushButton:disabled {
                        background-color: #343a40;
                        color: #6c757d;
                        border: 1px solid #343a40;
                    }
                """)
            else:
                self.setStyleSheet("""
                    QPushButton {
                        background-color: #ecf0f1;
                        color: #2c3e50;
                        border: 1px solid #bdc3c7;
                        border-radius: 4px;
                        padding: 8px 16px;
                    }
                    QPushButton:hover {
                        background-color: #bdc3c7;
                    }
                    QPushButton:pressed {
                        background-color: #95a5a6;
                    }
                    QPushButton:disabled {
                        background-color: #ecf0f1;
                        color: #bdc3c7;
                        border: 1px solid #ecf0f1;
                    }
                """)

class StyledListWidget(QListWidget):
    """Custom styled list widget"""
    def __init__(self, parent=None, dark_mode=False):
        super().__init__(parent)
        self.apply_style(dark_mode)
        
    def apply_style(self, dark_mode):
        """Apply theme-appropriate style"""
        if dark_mode:
            self.setStyleSheet("""
                QListWidget {
                    background-color: #2d2d2d;
                    border: 1px solid #444444;
                    border-radius: 4px;
                    padding: 2px;
                    outline: none;
                    color: #e0e0e0;
                }
                QListWidget::item {
                    padding: 6px;
                    border-bottom: 1px solid #3d3d3d;
                }
                QListWidget::item:selected {
                    background-color: #0d6efd;
                    color: white;
                }
                QListWidget::item:hover:!selected {
                    background-color: #3d3d3d;
                }
            """)
        else:
            self.setStyleSheet("""
                QListWidget {
                    background-color: #f5f5f5;
                    border: 1px solid #dcdcdc;
                    border-radius: 4px;
                    padding: 2px;
                    outline: none;
                }
                QListWidget::item {
                    padding: 6px;
                    border-bottom: 1px solid #eeeeee;
                }
                QListWidget::item:selected {
                    background-color: #3498db;
                    color: white;
                }
                QListWidget::item:hover:!selected {
                    background-color: #e5e5e5;
                }
            """)

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = AdwardConfig()
        self.network_manager = QNetworkAccessManager(self)
        self.api = AdwardAPI()
        self.dark_mode = False  
        # Set application font
        self.setup_fonts()
        
        # Connect API signals
        self.api.status_updated.connect(self.update_status_display)
        self.api.error_occurred.connect(self.show_error)
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
            }
            QLabel {
                color: #2c3e50;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: #ecf0f1;
                selection-background-color: #3498db;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
                background-color: white;
            }
        """)
        
        # Initialize UI
        self.setup_ui()
        
        # Check initial configuration
        self.check_configuration()
        
        self.apply_theme()

    def setup_fonts(self):
        """Set up application fonts"""
        # You could load custom fonts here if needed
        # For system fonts, we can specify preferred fonts
        app_font = self.font()
        app_font.setFamily("Segoe UI")  # You can change to any system font
        app_font.setPointSize(10)
        self.setFont(app_font)

    def setup_ui(self):
        """Set up the user interface"""
        # Create central widget and layout
        central_widget = QWidget(self)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Add logo at the top
        logo_layout = QHBoxLayout()
        logo_label = QLabel()

        pixmap = QPixmap("GUI/transparent_Adward")
        
        # Scale the image if needed (adjust size as appropriate)
        scaled_pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        # Set the pixmap to the label
        logo_label.setPixmap(scaled_pixmap)
        
        # Title next to logo
        title_label = QLabel("Current Configuration")
        title_font = QFont(self.font())
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        # Add the logo and title to the layout
        logo_layout.addWidget(logo_label, 0, Qt.AlignLeft | Qt.AlignVCenter)
        logo_layout.addWidget(title_label, 0, Qt.AlignLeft | Qt.AlignVCenter)
        logo_layout.addStretch(1)  # Push everything else to the right
    
        main_layout.addLayout(logo_layout)
        
        # Add separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #e0e0e0;")
        main_layout.addWidget(separator)
        
        # Status section with card-like container
        status_card = QFrame()
        status_card.setFrameShape(QFrame.StyledPanel)
        status_card.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #e9ecef;
            }
        """)
        status_layout = QVBoxLayout(status_card)
        
        # Add this near the other buttons in logo_layout
        self.theme_button = StyledButton("🌙 Dark Mode", primary=False)
        self.theme_button.clicked.connect(self.toggle_theme)
        logo_layout.addWidget(self.theme_button)

        # Config button at the top of the status card
        self.config_button = StyledButton("⚙️ Configure Server", status_card)
        self.config_button.clicked.connect(self.show_config_dialog)
        status_layout.addWidget(self.config_button)
        
        # Status display with toggle
        status_row = QHBoxLayout()
        
        self.status_label = QLabel("Status: Unknown")
        status_font = QFont(self.font())
        status_font.setBold(True)
        status_font.setPointSize(11)
        self.status_label.setFont(status_font)
        
        self.toggle_button = StyledButton("Toggle On/Off", status_card, primary=True)
        self.toggle_button.clicked.connect(self.toggle_adward)
        self.toggle_button.setMinimumWidth(120)
        
        status_row.addWidget(self.status_label)
        status_row.addStretch(1)
        status_row.addWidget(self.toggle_button)
        
        status_layout.addLayout(status_row)
        main_layout.addWidget(status_card)
        
        # Create list management section
        lists_card = QFrame()
        lists_card.setFrameShape(QFrame.StyledPanel)
        lists_card.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #e9ecef;
            }
        """)
        lists_layout = QVBoxLayout(lists_card)
        
        # Section title
        list_title = QLabel("Domain Lists")
        list_title_font = QFont(self.font())
        list_title_font.setBold(True)
        list_title_font.setPointSize(11)
        list_title.setFont(list_title_font)
        lists_layout.addWidget(list_title)
        
        # Buttons in horizontal layout
        buttons_layout = QHBoxLayout()
        
        self.blocklist_button = StyledButton("🛑 Manage Blocklist", lists_card, primary=True)
        self.allowlist_button = StyledButton("✓ Manage Allowlist", lists_card, primary=True)
        
        buttons_layout.addWidget(self.blocklist_button)
        buttons_layout.addWidget(self.allowlist_button)
        
        lists_layout.addLayout(buttons_layout)
        main_layout.addWidget(lists_card)
        
        # Add a stretcher to push everything up
        main_layout.addStretch(1)
        
        # Connect signals
        self.blocklist_button.clicked.connect(self.show_blocklist_modal)
        self.allowlist_button.clicked.connect(self.show_allowlist_modal)
        
        # Set up the central widget
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.setWindowTitle("AdWard Block/Allowlist Manager")
        self.resize(500, 400)
        
        self.setWindowIcon(QIcon("GUI/transparent_Adward.png"))

    def check_configuration(self):
        """Check if server is configured and update UI accordingly"""
        is_configured = self.config.is_configured()
        self.toggle_button.setEnabled(is_configured)
        self.blocklist_button.setEnabled(is_configured)
        self.allowlist_button.setEnabled(is_configured)
        
        if is_configured:
            # Setup API with stored credentials
            self.api.set_credentials(self.config.get_api_url(), self.config.token)
            self.fetch_status()
        else:
            self.status_label.setText("Status: Not Configured")
            self.status_label.setStyleSheet("color: #f39c12; font-weight: bold;")

    def show_config_dialog(self):
        dialog = ConfigDialog(self.config, self)
        if dialog.exec() == QDialog.Accepted:
            self.check_configuration()

    def show_blocklist_modal(self):
        self.blocklist_modal = QDialog(self)
        self.blocklist_modal.setWindowTitle("Manage Blocklist")
        self.blocklist_modal.resize(450, 550)
        if self.dark_mode:
            self.blocklist_modal.setStyleSheet("""
                QDialog {
                    background-color: #1e1e1e;
                }
                QLabel {
                    color: #e0e0e0;
                    font-weight: bold;
                    margin-bottom: 4px;
                }
            """)
        else:
            self.blocklist_modal.setStyleSheet("""
                QDialog {
                    background-color: white;
                }
                QLabel {
                    color: #2c3e50;
                    font-weight: bold;
                    margin-bottom: 4px;
                }
            """)
        
        modal_layout = QVBoxLayout(self.blocklist_modal)
        modal_layout.setContentsMargins(20, 20, 20, 20)
        modal_layout.setSpacing(12)
        
        # Header with icon
        header_layout = QHBoxLayout()
        header_icon = QLabel()
        header_icon.setText("🛑")
        header_icon.setFont(QFont(self.font().family(), 18))
        
        header_text = QLabel("AdWard Blocklist")
        header_font = QFont(self.font())
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_text.setFont(header_font)
        
        header_layout.addWidget(header_icon)
        header_layout.addWidget(header_text)
        header_layout.addStretch(1)
        modal_layout.addLayout(header_layout)
        
        # Instructions label
        instructions = QLabel("Add domains to blocklist:")
        instructions.setStyleSheet("color: #34495e; font-weight: normal;")
        modal_layout.addWidget(instructions)
        
        # List display
        self.blocklist_view = StyledListWidget(self.blocklist_modal, self.dark_mode)
        self.blocklist_view.setSelectionMode(QListWidget.ExtendedSelection)
        self.blocklist_view.setAlternatingRowColors(True)
        modal_layout.addWidget(self.blocklist_view)
        
        # Input area
        input_layout = QHBoxLayout()
        self.blocklist_input = QLineEdit(self.blocklist_modal)
        self.blocklist_input.setPlaceholderText("example.com")
        
        add_button = StyledButton("Add", self.blocklist_modal, primary=True)
        add_button.setMinimumWidth(80)
        
        input_layout.addWidget(self.blocklist_input)
        input_layout.addWidget(add_button)
        modal_layout.addLayout(input_layout)
        
        # Remove button
        remove_button = StyledButton("Remove Selected", self.blocklist_modal)
        modal_layout.addWidget(remove_button)
        
        # Connect actions
        add_button.clicked.connect(self.add_to_blocklist)
        remove_button.clicked.connect(self.remove_from_blocklist)
        
        # Fetch existing entries
        self.fetch_blocklist()
        
        self.blocklist_modal.exec()
        
    def show_allowlist_modal(self):
        self.allowlist_modal = QDialog(self)
        self.allowlist_modal.setWindowTitle("Manage Allowlist")
        self.allowlist_modal.resize(450, 550)
        if self.dark_mode:
            self.blocklist_modal.setStyleSheet("""
                QDialog {
                    background-color: #1e1e1e;
                }
                QLabel {
                    color: #e0e0e0;
                    font-weight: bold;
                    margin-bottom: 4px;
                }
            """)
        else:
            self.blocklist_modal.setStyleSheet("""
                QDialog {
                    background-color: white;
                }
                QLabel {
                    color: #2c3e50;
                    font-weight: bold;
                    margin-bottom: 4px;
                }
            """)
        
        modal_layout = QVBoxLayout(self.allowlist_modal)
        modal_layout.setContentsMargins(20, 20, 20, 20)
        modal_layout.setSpacing(12)
        
        # Header with icon
        header_layout = QHBoxLayout()
        header_icon = QLabel()
        header_icon.setText("✓")
        header_icon.setFont(QFont(self.font().family(), 18))
        
        header_text = QLabel("AdWard Allowlist")
        header_font = QFont(self.font())
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_text.setFont(header_font)
        
        header_layout.addWidget(header_icon)
        header_layout.addWidget(header_text)
        header_layout.addStretch(1)
        modal_layout.addLayout(header_layout)
        
        # Instructions label
        instructions = QLabel("Add domains to allowlist:")
        instructions.setStyleSheet("color: #34495e; font-weight: normal;")
        modal_layout.addWidget(instructions)
        
        # List display
        self.allowlist_view = StyledListWidget(self.allowlist_modal, self.dark_mode)
        self.allowlist_view.setSelectionMode(QListWidget.ExtendedSelection)
        self.allowlist_view.setAlternatingRowColors(True)
        modal_layout.addWidget(self.allowlist_view)
        
        # Input area
        input_layout = QHBoxLayout()
        self.allowlist_input = QLineEdit(self.allowlist_modal)
        self.allowlist_input.setPlaceholderText("example.com")
        
        add_button = StyledButton("Add", self.allowlist_modal, primary=True)
        add_button.setMinimumWidth(80)
        
        input_layout.addWidget(self.allowlist_input)
        input_layout.addWidget(add_button)
        modal_layout.addLayout(input_layout)
        
        # Remove button
        remove_button = StyledButton("Remove Selected", self.allowlist_modal)
        modal_layout.addWidget(remove_button)
        
        # Connect actions
        add_button.clicked.connect(self.add_to_allowlist)
        remove_button.clicked.connect(self.remove_from_allowlist)
        
        # Fetch existing entries
        self.fetch_allowlist()
        
        self.allowlist_modal.exec()


    def toggle_theme(self):
        """Toggle between light and dark mode"""
        self.dark_mode = not self.dark_mode
        self.theme_button.setText("☀️ Light Mode" if self.dark_mode else "🌙 Dark Mode")
        self.apply_theme()

    def apply_theme(self):
        """Apply the current theme to all UI elements"""
        if self.dark_mode:
            # Dark theme
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #1e1e1e;
                }
                QLabel {
                    color: #e0e0e0;
                }
                QLineEdit {
                    padding: 8px;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    background-color: #333333;
                    color: #e0e0e0;
                    selection-background-color: #3498db;
                }
                QLineEdit:focus {
                    border: 1px solid #3498db;
                    background-color: #404040;
                }
            """)

            # Update card styles
            for card in self.findChildren(QFrame):
                if card.frameShape() == QFrame.StyledPanel:
                    card.setStyleSheet("""
                        QFrame {
                            background-color: #2d2d2d;
                            border-radius: 8px;
                            border: 1px solid #444444;
                        }
                    """)
        else:
            # Light theme (original style)
            self.setStyleSheet("""
                QMainWindow {
                    background-color: white;
                }
                QLabel {
                    color: #2c3e50;
                }
                QLineEdit {
                    padding: 8px;
                    border: 1px solid #bdc3c7;
                    border-radius: 4px;
                    background-color: #ecf0f1;
                    selection-background-color: #3498db;
                }
                QLineEdit:focus {
                    border: 1px solid #3498db;
                    background-color: white;
                }
            """)

            # Reset card styles
            for card in self.findChildren(QFrame):
                if card.frameShape() == QFrame.StyledPanel:
                    card.setStyleSheet("""
                        QFrame {
                            background-color: #f8f9fa;
                            border-radius: 8px;
                            border: 1px solid #e9ecef;
                        }
                    """)
    def update_button_styles(self):
        """Update all buttons with the current theme"""
        for button in self.findChildren(StyledButton):
            button.apply_style(self.dark_mode)

    def add_to_blocklist(self):
        domain = self.blocklist_input.text().strip()
        if not domain:
            QMessageBox.warning(self, "Error", "Domain cannot be empty.")
            return
            
        url = QUrl(f"{self.config.get_api_url()}/admin/api.php?list=black&add={domain}&auth={self.config.token}")
        request = QNetworkRequest(url)
        reply = self.network_manager.get(request)
        reply.finished.connect(lambda: self._handle_add_response(reply, self.blocklist_view, domain))
        
    def add_to_allowlist(self):
        domain = self.allowlist_input.text().strip()
        if not domain:
            QMessageBox.warning(self, "Error", "Domain cannot be empty.")
            return
            
        url = QUrl(f"{self.config.get_api_url()}/admin/api.php?list=white&add={domain}&auth={self.config.token}")
        request = QNetworkRequest(url)
        reply = self.network_manager.get(request)
        reply.finished.connect(lambda: self._handle_add_response(reply, self.allowlist_view, domain))
    
    def remove_from_blocklist(self):
        selected_items = self.blocklist_view.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No domains selected.")
            return
            
        for item in selected_items:
            domain = item.text()
            url = QUrl(f"{self.config.get_api_url()}/admin/api.php?list=black&sub={domain}&auth={self.config.token}")
            request = QNetworkRequest(url)
            reply = self.network_manager.get(request)
            reply.finished.connect(lambda reply=reply, item=item: self._handle_remove_response(reply, self.blocklist_view, item))
    
    def remove_from_allowlist(self):
        selected_items = self.allowlist_view.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No domains selected.")
            return
            
        for item in selected_items:
            domain = item.text()
            url = QUrl(f"{self.config.get_api_url()}/admin/api.php?list=white&sub={domain}&auth={self.config.token}")
            request = QNetworkRequest(url)
            reply = self.network_manager.get(request)
            reply.finished.connect(lambda reply=reply, item=item: self._handle_remove_response(reply, self.allowlist_view, item))
        
    def fetch_blocklist(self):
        self.blocklist_view.clear()
        url = QUrl(f"{self.config.get_api_url()}/admin/api.php?list=black&auth={self.config.token}")
        request = QNetworkRequest(url)
        reply = self.network_manager.get(request)
        reply.finished.connect(lambda: self._handle_list_response(reply, self.blocklist_view))
        
    def fetch_allowlist(self):
        self.allowlist_view.clear()
        url = QUrl(f"{self.config.get_api_url()}/admin/api.php?list=white&auth={self.config.token}")
        request = QNetworkRequest(url)
        reply = self.network_manager.get(request)
        reply.finished.connect(lambda: self._handle_list_response(reply, self.allowlist_view))

    def fetch_status(self):
        """Fetch the AdWard status"""
        if self.config.is_configured():
            self.api.fetch_status(self.config.get_api_url(), self.config.token)
            
    def update_status_display(self, enabled: bool):
        """Update the UI based on AdWard status"""
        status_text = "Enabled" if enabled else "Disabled"
        self.status_label.setText(f"Status: {status_text}")
    
    # Use theme-appropriate colors
        if self.dark_mode:
            enabled_color = "#4bb543"  # Darker green for dark mode
            disabled_color = "#ff3333"  # Darker red for dark mode
        else:
            enabled_color = "#27ae60"  # Original green
            disabled_color = "#e74c3c"  # Original red
        
        self.status_label.setStyleSheet(
            f"color: {enabled_color if enabled else disabled_color}; font-weight: bold;"
        )
        
        self.toggle_button.setText("Disable" if enabled else "Enable")
        
    def toggle_adward(self):
        """Toggle AdWard enabled/disabled status"""
        current_status = self.status_label.text() == "Status: Enabled"
    
        self.api.toggle_status(not current_status, self.config.get_api_url(), self.config.token)
    
    def show_error(self, error_message):
        """Show error message from API"""
        error_dialog = QMessageBox(self)
        error_dialog.setWindowTitle("API Error")
        error_dialog.setText(error_message)
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setStandardButtons(QMessageBox.Ok)
        error_dialog.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        error_dialog.exec()
    
    def _handle_add_response(self, reply, list_widget, domain):
        """Handle response after adding domain to list"""
        if reply.error() == QNetworkReply.NoError:
            try:
                response = str(reply.readAll(), 'utf-8')
                data = json.loads(response)
                if data.get("success"):
                    self.blocklist_input.clear()
                    item = QListWidgetItem(domain)
                    list_widget.addItem(item)
                    
                    # Show success message
                    success_dialog = QMessageBox(self)
                    success_dialog.setWindowTitle("Success")
                    success_dialog.setText(f"Domain '{domain}' added successfully.")
                    success_dialog.setIcon(QMessageBox.Information)
                    success_dialog.setStandardButtons(QMessageBox.Ok)
                    success_dialog.setStyleSheet("""
                        QMessageBox {
                            background-color: white;
                        }
                        QPushButton {
                            background-color: #2ecc71;
                            color: white;
                            border: none;
                            border-radius: 4px;
                            padding: 6px 12px;
                            min-width: 80px;
                        }
                        QPushButton:hover {
                            background-color: #27ae60;
                        }
                    """)
                    success_dialog.exec()
                else:
                    QMessageBox.warning(self, "Warning", f"Failed to add domain: {data.get('message', 'Unknown error')}")
            except (json.JSONDecodeError, UnicodeDecodeError):
                QMessageBox.warning(self, "Error", "Invalid response from server.")
        else:
            QMessageBox.critical(self, "Error", f"Network error: {reply.errorString()}")
        reply.deleteLater()
        
    def _handle_remove_response(self, reply, list_widget, item):
        """Handle response after removing domain from list"""
        if reply.error() == QNetworkReply.NoError:
            try:
                response = str(reply.readAll(), 'utf-8')
                data = json.loads(response)
                if data.get("success"):
                    row = list_widget.row(item)
                    list_widget.takeItem(row)
                else:
                    QMessageBox.warning(self, "Warning", f"Failed to remove domain: {data.get('message', 'Unknown error')}")
            except (json.JSONDecodeError, UnicodeDecodeError):
                QMessageBox.warning(self, "Error", "Invalid response from server.")
        else:
            QMessageBox.critical(self, "Error", f"Network error: {reply.errorString()}")
        reply.deleteLater()
        
    def _handle_list_response(self, reply, list_widget):
        """Handle response from fetching list"""
        if reply.error() == QNetworkReply.NoError:
            try:
                response = str(reply.readAll(), 'utf-8')
                data = json.loads(response)
                
                # Clear the list first
                list_widget.clear()
                
                # Add domains to the list
                if isinstance(data, list):
                    list_widget.addItems(data)
                elif isinstance(data, dict) and "data" in data:
                    if isinstance(data["data"], list):
                        list_widget.addItems(data["data"])
            except (json.JSONDecodeError, UnicodeDecodeError):
                QMessageBox.warning(self, "Error", "Invalid response from server.")
        else:
            QMessageBox.critical(self, "Error", f"Failed to fetch list: {reply.errorString()}")
        reply.deleteLater()