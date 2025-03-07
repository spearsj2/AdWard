from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
import json

class AdwardAPI(QObject):
    summary_updated = Signal(dict)
    error_occurred = Signal(str)
    status_updated = Signal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.network_manager = QNetworkAccessManager(self)
        self.network_manager.finished.connect(self._handle_network_reply)
        self.api_url = ""
        self.api_key = ""
        
    def set_credentials(self, api_url: str, api_key: str) -> None:
        """Store API credentials for reuse"""
        self.api_url = api_url
        self.api_key = api_key
        
    def fetch_status(self, api_url: str = None, api_key: str = None) -> None:
        """Fetch the current status from the API"""
        url = QUrl(f"{api_url or self.api_url}/admin/api.php?status&auth={api_key or self.api_key}")
        request = QNetworkRequest(url)
        request.setAttribute(QNetworkRequest.User, "status")
        self.network_manager.get(request)
        
    def fetch_summary(self) -> None:
        """Fetch summary data from the API"""
        url = QUrl(f"{self.api_url}/admin/api.php?summaryRaw&auth={self.api_key}")
        request = QNetworkRequest(url)
        request.setAttribute(QNetworkRequest.User, "summary")
        self.network_manager.get(request)
    
    def toggle_status(self, enable: bool, api_url: str = None, api_key: str = None) -> None:
        """Toggle the service status (enable/disable)"""
        action = "enable" if enable else "disable"
        url = QUrl(f"{api_url or self.api_url}/admin/api.php?{action}&auth={api_key or self.api_key}")
        request = QNetworkRequest(url)
        request.setAttribute(QNetworkRequest.User, "toggle")
        self.network_manager.get(request)
    
    def _handle_network_reply(self, reply: QNetworkReply) -> None:
        """Handle network responses"""
        try:
            if reply.error() == QNetworkReply.NoError:
                response = reply.readAll()
                data = json.loads(str(response, 'utf-8'))
                
                request_type = reply.request().attribute(QNetworkRequest.User)
                if request_type == "status":
                    self.status_updated.emit(data.get("status") == "enabled")
                elif request_type == "summary":
                    self.summary_updated.emit(data)
                elif request_type == "toggle":
                    # After toggle, fetch new status using stored credentials
                    self.fetch_status()
            else:
                self.error_occurred.emit(reply.errorString())
        except json.JSONDecodeError:
            self.error_occurred.emit("Invalid JSON response")
        except Exception as e:
            self.error_occurred.emit(f"Error processing response: {str(e)}")
        finally:
            reply.deleteLater()