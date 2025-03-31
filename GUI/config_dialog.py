from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLabel, QLineEdit, QPushButton, QMessageBox,
                             QCheckBox, QGroupBox)
from PySide6.QtCore import Qt

class ConfigDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("AdWard Configuration")
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)
        
        # DNS Server Configuration group
        dns_group = QGroupBox("DNS Server Configuration")
        dns_layout = QFormLayout(dns_group)
        
        # DNS Port
        self.port_input = QLineEdit(self.config.get_dns_port())
        self.port_input.setPlaceholderText("53")
        dns_layout.addRow("DNS Port:", self.port_input)
        
        # Alternative DNS
        self.alt_dns_input = QLineEdit(self.config.get_dns_alternative())
        self.alt_dns_input.setPlaceholderText("8.8.8.8")
        dns_layout.addRow("Alternative DNS:", self.alt_dns_input)
        
        # Logging
        self.logging_checkbox = QCheckBox("Enable Logging")
        self.logging_checkbox.setChecked(self.config.is_logging_enabled())
        dns_layout.addRow("", self.logging_checkbox)
        
        main_layout.addWidget(dns_group)
        
        # Help text
        help_label = QLabel(
            "These settings configure the local DNS server. The DNS Port is the port "
            "your AdWard DNS server will listen on (default 53). The Alternative DNS "
            "is the external DNS server used to resolve non-blocked domains."
        )
        help_label.setWordWrap(True)
        help_label.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(help_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save Configuration")
        self.save_button.clicked.connect(self.save_config)
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self.reset_config)
        
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch(1)
        button_layout.addWidget(self.save_button)
        
        main_layout.addLayout(button_layout)
        
        self.resize(400, 300)
        
    def save_config(self):
        # Validate DNS port
        dns_port = self.port_input.text().strip()
        if not dns_port.isdigit() or int(dns_port) <= 0 or int(dns_port) > 65535:
            QMessageBox.warning(self, "Error", "DNS port must be a valid port number (1-65535).")
            return
            
        # Validate Alternative DNS
        dns_alternative = self.alt_dns_input.text().strip()
        if not dns_alternative:
            QMessageBox.warning(self, "Error", "Alternative DNS is required.")
            return
            
        logging_enabled = "True" if self.logging_checkbox.isChecked() else "False"
        
        # Save configuration
        self.config.save_config(dns_port, dns_alternative, logging_enabled)
        
        QMessageBox.information(self, "Success", "Configuration saved successfully!")
        self.accept()
        
    def reset_config(self):
        """Reset all fields to default values"""
        self.port_input.setText("53")
        self.alt_dns_input.setText("8.8.8.8")
        self.logging_checkbox.setChecked(True)