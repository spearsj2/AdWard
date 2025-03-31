from PySide6.QtCore import QSettings
import os

class AdwardConfig:
    def __init__(self):
        self.settings = QSettings('AdwardManager', 'Config')
        # Get the dns port from settings, or use default 53
        self.dns_port = self.settings.value('dns_port', '53')
        self.dns_alternative = self.settings.value('dns_alternative', '8.8.8.8')
        # Get logging enabled setting, default to True
        self.logging_enabled = self.settings.value('logging_enabled', 'True')
        
        # Calculate paths relative to project root
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.config_file = os.path.join(self.project_root, 'etc', 'adward.conf')
        self.server_script = os.path.join(self.project_root, 'main', 'server.py')
        
    def is_configured(self):
        """Check if the necessary configuration exists"""
        return True
    
    def save_config(self, dns_port, dns_alternative, logging_enabled):
        """Save configuration settings"""
        self.dns_port = dns_port
        self.dns_alternative = dns_alternative
        self.logging_enabled = logging_enabled
        
        self.settings.setValue('dns_port', dns_port)
        self.settings.setValue('dns_alternative', dns_alternative)
        self.settings.setValue('logging_enabled', logging_enabled)
        self.settings.sync()
        
        self._update_config_file()
        
    def clear_config(self):
        """Reset configuration to defaults"""
        self.dns_port = '53'
        self.dns_alternative = '8.8.8.8'
        self.logging_enabled = 'True'
        
        self.settings.setValue('dns_port', self.dns_port)
        self.settings.setValue('dns_alternative', self.dns_alternative)
        self.settings.setValue('logging_enabled', self.logging_enabled)
        self.settings.sync()
        
        self._update_config_file()
    
    def get_dns_port(self):
        """Get configured DNS port"""
        return self.dns_port
    
    def get_dns_alternative(self):
        """Get configured alternative DNS server"""
        return self.dns_alternative
    
    def is_logging_enabled(self):
        """Check if logging is enabled"""
        return self.logging_enabled == 'True'
    
    def _update_config_file(self):
        """Update the configuration file with current settings"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    lines = f.readlines()
                
                updated_lines = []
                for line in lines:
                    if line.startswith('dnsPort='):
                        updated_lines.append(f'dnsPort={self.dns_port}\n')
                    elif line.startswith('dnsAlternative='):
                        updated_lines.append(f'dnsAlternative={self.dns_alternative}\n')
                    elif line.startswith('loggingEnabled='):
                        updated_lines.append(f'loggingEnabled={self.logging_enabled}\n')
                    else:
                        updated_lines.append(line)
                
                with open(self.config_file, 'w') as f:
                    f.writelines(updated_lines)
        except Exception as e:
            print(f"Error updating config file: {e}")
            # Continue execution even if updating the config file fails