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