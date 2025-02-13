from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                              QLabel, QLineEdit, QPushButton, QMessageBox)

class ConfigDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Server address input
        server_layout = QHBoxLayout()
        server_label = QLabel("Server Address:")
        self.server_input = QLineEdit(self.config.ip)
        server_layout.addWidget(server_label)
        server_layout.addWidget(self.server_input)
        
        # API key input
        api_layout = QHBoxLayout()
        api_label = QLabel("API Key:")
        self.api_input = QLineEdit(self.config.token)
        self.api_input.setEchoMode(QLineEdit.Password)  # Hide API key
        api_layout.addWidget(api_label)
        api_layout.addWidget(self.api_input)
        
        # Save button
        save_button = QPushButton("Save Configuration")
        save_button.clicked.connect(self.save_config)
        
        # Add everything to main layout
        layout.addLayout(server_layout)
        layout.addLayout(api_layout)
        layout.addWidget(save_button)
        
        self.setLayout(layout)
        self.setWindowTitle("Server Configuration")
        
    def save_config(self):
        server = self.server_input.text().strip()
        api_key = self.api_input.text().strip()
        
        if not server or not api_key:
            QMessageBox.warning(self, "Error", "Both server address and API key are required.")
            return
            
        self.config.save_config(server, api_key)
        QMessageBox.information(self, "Success", "Configuration saved successfully!")
        self.accept()