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
        
        # Save button
        save_button = QPushButton("Save Configuration")
        save_button.clicked.connect(self.save_config)
        
        # Add everything to main layout
        layout.addLayout(server_layout)
        layout.addWidget(save_button)
        
        self.setLayout(layout)
        self.setWindowTitle("Server Configuration")
        
    def save_config(self):
        server = self.server_input.text().strip()
        
        if not server:
            QMessageBox.warning(self, "Error", "Server address is required.")
            return
            
        self.config.save_config(server)
        QMessageBox.information(self, "Success", "Configuration saved successfully!")
        self.accept()