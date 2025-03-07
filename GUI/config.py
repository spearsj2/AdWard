from PySide6.QtCore import QSettings

class PiholeConfig:
    def __init__(self):
        self.settings = QSettings('PiholeManager', 'Config')
        self.ip = self.settings.value('ip', '')
        self.token = self.settings.value('token', '')
        
    def is_configured(self):
        return bool(self.ip and self.token)
    
    def save_config(self, ip, token):
        self.ip = ip
        self.token = token
        self.settings.setValue('ip', ip)
        self.settings.setValue('token', token)
        self.settings.sync()  # Ensure settings are saved immediately
        
    def clear_config(self):
        """Clear saved configuration"""
        self.ip = ''
        self.token = ''
        self.settings.remove('ip')
        self.settings.remove('token')
        self.settings.sync()
        
    def get_api_url(self):
        """Return formatted API URL"""
        if not self.ip:
            return ""
        # Format IP properly with protocol
        if not self.ip.startswith(('http://', 'https://')):
            return f"http://{self.ip}"
        return self.ip