from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton,
                              QDialog, QListWidget, QLineEdit, QMessageBox,
                              QHBoxLayout, QLabel)
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtCore import QUrl, QSettings
from adward_API import AdwardAPI
from config import PiholeConfig  
import json
import re

class AdwardConfig:
    def __init__(self):
        self.settings = QSettings('AdwardManager', 'Config')
        self.ip = self.settings.value('ip', '')
        self.token = self.settings.value('token', '')

    def is_configured(self):
        return bool(self.ip and self.token)

    def save_config(self, ip, token):
        self.ip = ip
        self.token = token
        self.settings.setValue('ip', ip)
        self.settings.setValue('token', token)

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.network_manager = QNetworkAccessManager(self) 
        self.network_manager.finished.connect(self._handle_network_reply)
        self.config = PiholeConfig() 
        self.api = AdwardAPI()
        self.api.status_updated.connect(self.update_status_display)
        self.setup_ui()
        
    def setup_ui(self):
        central_widget = QWidget(self)
        layout = QVBoxLayout()
        
        # Status section
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Status: Unknown")
        self.toggle_button = QPushButton("Toggle Pi-hole")
        self.toggle_button.clicked.connect(self.toggle_pihole)
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.toggle_button)
        
        layout.addLayout(status_layout)
        
        # Buttons
        self.blocklist_button = QPushButton("Manage Blocklist")
        self.allowlist_button = QPushButton("Manage Allowlist")
        config_button = QPushButton("Configure AdWard")
        
        layout.addWidget(self.blocklist_button)
        layout.addWidget(self.allowlist_button)
        layout.addWidget(config_button)
        
        self.blocklist_button.clicked.connect(lambda: self.show_list_modal("black"))
        self.allowlist_button.clicked.connect(lambda: self.show_list_modal("white"))
        config_button.clicked.connect(self.show_config_dialog)
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.setWindowTitle("AdWard Manager")
        self.fetch_status()
        
    def fetch_status(self):
        if self.config.is_configured():
            self.api.fetch_status(self.config.ip, self.config.token)
            
    def update_status_display(self, enabled: bool):
        status_text = "Enabled" if enabled else "Disabled"
        self.status_label.setText(f"Status: {status_text}")
        self.status_label.setStyleSheet(
            f"color: {'green' if enabled else 'red'}; font-weight: bold;"
        )
        
    def toggle_pihole(self):
        current_status = self.status_label.text() == "Status: Enabled"
        self.api.toggle_status(self.config.ip, self.config.token, not current_status)

    def show_config_dialog(self):
        dialog = QDialog(self)
        layout = QVBoxLayout()
        
        ip_input = QLineEdit(self.config.ip)
        token_input = QLineEdit(self.config.token)
        token_input.setEchoMode(QLineEdit.Password)
        
        layout.addWidget(QLabel("Pi-hole IP:"))
        layout.addWidget(ip_input)
        layout.addWidget(QLabel("API Token:"))
        layout.addWidget(token_input)
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(lambda: self.save_config(dialog, ip_input.text(), token_input.text()))
        
        layout.addWidget(save_button)
        dialog.setLayout(layout)
        dialog.exec()

    def show_list_modal(self, list_type):
        if not self.config.is_configured():
            QMessageBox.warning(self, "Error", "Please configure Pi-hole settings first.")
            return
            
        dialog = QDialog(self)
        layout = QVBoxLayout()
        
        list_view = QListWidget()
        input_layout = QHBoxLayout()
        domain_input = QLineEdit()
        add_button = QPushButton("Add")
        remove_button = QPushButton("Remove Selected")
        
        input_layout.addWidget(domain_input)
        input_layout.addWidget(add_button)
        
        layout.addWidget(list_view)
        layout.addLayout(input_layout)
        layout.addWidget(remove_button)
        
        add_button.clicked.connect(lambda: self.add_domain(list_type, domain_input, list_view))
        remove_button.clicked.connect(lambda: self.remove_domain(list_type, list_view))
        
        self.fetch_list(list_type, list_view)
        dialog.setLayout(layout)
        dialog.setWindowTitle(f"Manage {'Blocklist' if list_type == 'black' else 'Allowlist'}")
        dialog.exec()

    def add_domain(self, list_type, input_widget, list_view):
        domain = input_widget.text().strip()
        if not self.validate_domain(domain):
            QMessageBox.warning(self, "Error", "Invalid domain format.")
            return
            
        url = f"http://{self.config.ip}/admin/api.php"
        params = f"list={list_type}&add={domain}&auth={self.config.token}"
        request = QNetworkRequest(QUrl(f"{url}?{params}"))
        
        reply = self.network_manager.get(request)
        reply.finished.connect(lambda: self.handle_add_response(reply, domain, list_view, input_widget))

    def remove_domain(self, list_type, list_view):
        item = list_view.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Please select a domain to remove.")
            return
            
        domain = item.text()
        url = f"http://{self.config.ip}/admin/api.php"
        params = f"list={list_type}&sub={domain}&auth={self.config.token}"
        request = QNetworkRequest(QUrl(f"{url}?{params}"))
        
        reply = self.network_manager.get(request)
        reply.finished.connect(lambda: self.handle_remove_response(reply, item, list_view))

    def fetch_list(self, list_type, list_view):
        url = f"http://{self.config.ip}/admin/api.php"
        params = f"list={list_type}&auth={self.config.token}"
        request = QNetworkRequest(QUrl(f"{url}?{params}"))
        
        reply = self.network_manager.get(request)
        reply.finished.connect(lambda: self.handle_list_response(reply, list_view))

    def handle_add_response(self, reply, domain, list_view, input_widget):
        if reply.error() == QNetworkReply.NoError:
            try:
                response = json.loads(str(reply.readAll(), 'utf-8'))
                if response.get('success'):
                    list_view.addItem(domain)
                    input_widget.clear()
                else:
                    QMessageBox.warning(self, "Error", "Failed to add domain.")
            except json.JSONDecodeError:
                QMessageBox.warning(self, "Error", "Invalid response from server.")
        else:
            QMessageBox.critical(self, "Error", f"Network error: {reply.errorString()}")
        reply.deleteLater()

    def handle_remove_response(self, reply, item, list_view):
        if reply.error() == QNetworkReply.NoError:
            try:
                response = json.loads(str(reply.readAll(), 'utf-8'))
                if response.get('success'):
                    list_view.takeItem(list_view.row(item))
                else:
                    QMessageBox.warning(self, "Error", "Failed to remove domain.")
            except json.JSONDecodeError:
                QMessageBox.warning(self, "Error", "Invalid response from server.")
        else:
            QMessageBox.critical(self, "Error", f"Network error: {reply.errorString()}")
        reply.deleteLater()

    def handle_list_response(self, reply, list_view):
        if reply.error() == QNetworkReply.NoError:
            try:
                response = json.loads(str(reply.readAll(), 'utf-8'))
                domains = response.get('list', [])
                list_view.addItems(domains)
            except json.JSONDecodeError:
                QMessageBox.warning(self, "Error", "Invalid response from server.")
        else:
            QMessageBox.critical(self, "Error", f"Network error: {reply.errorString()}")
        reply.deleteLater()

    @staticmethod
    def validate_domain(domain):
        pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        return bool(re.match(pattern, domain))

    def save_config(self, dialog, ip, token):
        if not ip or not token:
            QMessageBox.warning(self, "Error", "Both IP and token are required.")
            return
        self.config.save_config(ip, token)
        dialog.accept()