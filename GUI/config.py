from PySide6.QtCore import QSettings

class AdwardConfig:
    def __init__(self):
        self.settings = QSettings('AdWardManager', 'Config')
        self.ip = self.settings.value('ip', '')
        
    def is_configured(self):
        return bool(self.ip)
    
    def save_config(self, ip):
        self.ip = ip
        self.settings.setValue('ip', ip)
        self.settings.sync()  # Ensure settings are saved immediately
        
    def clear_config(self):
        """Clear saved configuration"""
        self.ip = ''
        self.settings.remove('ip')
        self.settings.sync()
        
    def get_api_url(self):
        """Return formatted API URL"""
        if not self.ip:
            return ""
        # Format IP properly with protocol
        if not self.ip.startswith(('http://', 'https://')):
            return f"http://{self.ip}"
        return self.ip