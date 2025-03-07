from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                              QDialog, QListWidget, QLineEdit, QMessageBox,
                              QHBoxLayout, QLabel, QListWidgetItem)
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QPixmap, QIcon
import json
from adward_API import AdwardAPI
from config import PiholeConfig
from config_dialog import ConfigDialog

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = PiholeConfig()
        self.network_manager = QNetworkAccessManager(self)
        self.api = AdwardAPI()
        
        # Connect API signals
        self.api.status_updated.connect(self.update_status_display)
        self.api.error_occurred.connect(self.show_error)
        
        # Initialize UI
        self.setup_ui()
        
        # Check initial configuration
        self.check_configuration()

    def setup_ui(self):
        """Set up the user interface"""
        # Create central widget and layout
        central_widget = QWidget(self)
        main_layout = QVBoxLayout()

        # Add logo at the top
        logo_layout = QHBoxLayout()
        logo_label = QLabel()

        pixmap = QPixmap("GUI/transparent_Adward")
        
        # Scale the image if needed (adjust size as appropriate)
        scaled_pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        # Set the pixmap to the label
        logo_label.setPixmap(scaled_pixmap)
        
        # Add the logo to the layout with alignment
        logo_layout.addWidget(logo_label, 0, Qt.AlignLeft | Qt.AlignTop)
        logo_layout.addStretch(1)  # Push everything else to the right
    
        main_layout.addLayout(logo_layout)
        
        # Status section
        self.config_button = QPushButton("Configure Server", self)
        self.config_button.clicked.connect(self.show_config_dialog)
        main_layout.addWidget(self.config_button)
        
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Status: Unknown")
        self.status_label.setStyleSheet("font-weight: bold;")
        
        self.toggle_button = QPushButton("Toggle On/Off")
        self.toggle_button.clicked.connect(self.toggle_pihole)
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.toggle_button)
        main_layout.addLayout(status_layout)
        
        # Create list management buttons
        self.blocklist_button = QPushButton("Manage Blocklist", self)
        self.allowlist_button = QPushButton("Manage Allowlist", self)
        
        main_layout.addWidget(self.blocklist_button)
        main_layout.addWidget(self.allowlist_button)
        
        # Connect signals
        self.blocklist_button.clicked.connect(self.show_blocklist_modal)
        self.allowlist_button.clicked.connect(self.show_allowlist_modal)
        
        # Set up the central widget
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.setWindowTitle("Pi-hole Block/Allowlist Manager")
        self.resize(400, 300)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
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
            self.status_label.setStyleSheet("color: orange; font-weight: bold;")

    def show_config_dialog(self):
        dialog = ConfigDialog(self.config, self)
        if dialog.exec() == QDialog.Accepted:
            self.check_configuration()

    def show_blocklist_modal(self):
        self.blocklist_modal = QDialog(self)
        self.blocklist_modal.setWindowTitle("Manage Blocklist")
        self.blocklist_modal.resize(400, 500)
        
        modal_layout = QVBoxLayout(self.blocklist_modal)
        
        # Instructions label
        instructions = QLabel("Add domains to blocklist (one per line):")
        modal_layout.addWidget(instructions)
        
        # List display
        self.blocklist_view = QListWidget(self.blocklist_modal)
        self.blocklist_view.setSelectionMode(QListWidget.ExtendedSelection)
        modal_layout.addWidget(self.blocklist_view)
        
        # Input area
        self.blocklist_input = QLineEdit(self.blocklist_modal)
        self.blocklist_input.setPlaceholderText("example.com")
        modal_layout.addWidget(self.blocklist_input)
        
        # Button layout
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add Domain", self.blocklist_modal)
        remove_button = QPushButton("Remove Selected", self.blocklist_modal)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)
        modal_layout.addLayout(button_layout)
        
        # Connect actions
        add_button.clicked.connect(self.add_to_blocklist)
        remove_button.clicked.connect(self.remove_from_blocklist)
        
        # Fetch existing entries
        self.fetch_blocklist()
        
        self.blocklist_modal.exec()
        
    def show_allowlist_modal(self):
        self.allowlist_modal = QDialog(self)
        self.allowlist_modal.setWindowTitle("Manage Allowlist")
        self.allowlist_modal.resize(400, 500)
        
        modal_layout = QVBoxLayout(self.allowlist_modal)
        
        # Instructions label
        instructions = QLabel("Add domains to allowlist (one per line):")
        modal_layout.addWidget(instructions)
        
        # List display
        self.allowlist_view = QListWidget(self.allowlist_modal)
        self.allowlist_view.setSelectionMode(QListWidget.ExtendedSelection)
        modal_layout.addWidget(self.allowlist_view)
        
        # Input area
        self.allowlist_input = QLineEdit(self.allowlist_modal)
        self.allowlist_input.setPlaceholderText("example.com")
        modal_layout.addWidget(self.allowlist_input)
        
        # Button layout
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add Domain", self.allowlist_modal)
        remove_button = QPushButton("Remove Selected", self.allowlist_modal)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)
        modal_layout.addLayout(button_layout)
        
        # Connect actions
        add_button.clicked.connect(self.add_to_allowlist)
        remove_button.clicked.connect(self.remove_from_allowlist)
        
        # Fetch existing entries
        self.fetch_allowlist()
        
        self.allowlist_modal.exec()

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
        """Fetch the Pi-hole status"""
        if self.config.is_configured():
            self.api.fetch_status(self.config.get_api_url(), self.config.token)
            
    def update_status_display(self, enabled: bool):
        """Update the UI based on Pi-hole status"""
        status_text = "Enabled" if enabled else "Disabled"
        self.status_label.setText(f"Status: {status_text}")
        self.status_label.setStyleSheet(
            f"color: {'green' if enabled else 'red'}; font-weight: bold;"
        )
        # Update toggle button text
        self.toggle_button.setText("Disable" if enabled else "Enable")
        
    def toggle_pihole(self):
        """Toggle Pi-hole enabled/disabled status"""
        current_status = self.status_label.text() == "Status: Enabled"
        self.api.toggle_status(not current_status, self.config.get_api_url(), self.config.token)
    
    def show_error(self, error_message):
        """Show error message from API"""
        QMessageBox.critical(self, "API Error", error_message)
    
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
                    QMessageBox.information(self, "Success", f"Domain '{domain}' added successfully.")
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