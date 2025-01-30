from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                              QDialog, QListWidget, QLineEdit, QMessageBox)
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtCore import QUrl  # Added this import

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.network_manager = QNetworkAccessManager(self)
        
        # Create central widget and layout
        central_widget = QWidget(self)
        layout = QVBoxLayout()
        
        # Create buttons
        self.blocklist_button = QPushButton("Manage Blocklist", self)
        self.allowlist_button = QPushButton("Manage Allowlist", self)
        
        # Add buttons to layout
        layout.addWidget(self.blocklist_button)
        layout.addWidget(self.allowlist_button)
        
        # Connect signals
        self.blocklist_button.clicked.connect(self.show_blocklist_modal)
        self.allowlist_button.clicked.connect(self.show_allowlist_modal)
        
        # Set up the central widget
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.setWindowTitle("Pi-hole Block/Allowlist Manager")

    def show_blocklist_modal(self):
        self.blocklist_modal = QDialog(self)
        modal_layout = QVBoxLayout(self.blocklist_modal)
        
        self.blocklist_view = QListWidget(self.blocklist_modal)
        self.blocklist_input = QLineEdit(self.blocklist_modal)
        add_button = QPushButton("Add to Blocklist", self.blocklist_modal)
        
        modal_layout.addWidget(self.blocklist_view)
        modal_layout.addWidget(self.blocklist_input)
        modal_layout.addWidget(add_button)
        
        add_button.clicked.connect(self.add_to_blocklist)
        
        self.fetch_blocklist()
        self.blocklist_modal.setLayout(modal_layout)
        self.blocklist_modal.setWindowTitle("Manage Blocklist")
        self.blocklist_modal.exec()
        
    def show_allowlist_modal(self):
        self.allowlist_modal = QDialog(self)
        modal_layout = QVBoxLayout(self.allowlist_modal)
        
        self.allowlist_view = QListWidget(self.allowlist_modal)
        self.allowlist_input = QLineEdit(self.allowlist_modal)
        add_button = QPushButton("Add to Allowlist", self.allowlist_modal)
        
        modal_layout.addWidget(self.allowlist_view)
        modal_layout.addWidget(self.allowlist_input)
        modal_layout.addWidget(add_button)
        
        add_button.clicked.connect(self.add_to_allowlist)
        
        self.fetch_allowlist()
        self.allowlist_modal.setLayout(modal_layout)
        self.allowlist_modal.setWindowTitle("Manage Allowlist")
        self.allowlist_modal.exec()

    def add_to_blocklist(self):
        domain = self.blocklist_input.text()
        if not domain:
            QMessageBox.warning(self, "Error", "Domain cannot be empty.")
            return
            
        url = f"http://your-pihole-ip/admin/api.php?list=black&add={domain}&auth=your-api-token"
        request = QNetworkRequest(QUrl(url))
        self.network_manager.get(request)
        QMessageBox.information(self, "Success", "Domain added to blocklist.")
        
    def add_to_allowlist(self):
        domain = self.allowlist_input.text()
        if not domain:
            QMessageBox.warning(self, "Error", "Domain cannot be empty.")
            return
            
        url = f"http://your-pihole-ip/admin/api.php?list=white&add={domain}&auth=your-api-token"
        request = QNetworkRequest(QUrl(url))
        self.network_manager.get(request)
        QMessageBox.information(self, "Success", "Domain added to allowlist.")
        
    def fetch_blocklist(self):
        url = "http://your-pihole-ip/admin/api.php?list=black&auth=your-api-token"
        request = QNetworkRequest(QUrl(url))
        reply = self.network_manager.get(request)
        reply.finished.connect(lambda: self._handle_blocklist_response(reply))
        
    def fetch_allowlist(self):
        url = "http://your-pihole-ip/admin/api.php?list=white&auth=your-api-token"
        request = QNetworkRequest(QUrl(url))
        reply = self.network_manager.get(request)
        reply.finished.connect(lambda: self._handle_allowlist_response(reply))
        
    def _handle_blocklist_response(self, reply):
        if reply.error() == QNetworkReply.NoError:
            domains = str(reply.readAll(), 'utf-8').split('\n')
            self.blocklist_view.addItems(domains)
        else:
            QMessageBox.critical(self, "Error", "Failed to fetch blocklist.")
        reply.deleteLater()
        
    def _handle_allowlist_response(self, reply):
        if reply.error() == QNetworkReply.NoError:
            domains = str(reply.readAll(), 'utf-8').split('\n')
            self.allowlist_view.addItems(domains)
        else:
            QMessageBox.critical(self, "Error", "Failed to fetch allowlist.")
        reply.deleteLater()