from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
import json

class AdwardAPI(QObject):
    summary_updated = Signal(dict)
    error_occurred = Signal(str)
    status_updated = Signal(bool)  # True for enabled, False for disabled
    
    def fetch_status(self, api_url: str, api_key: str) -> None:
        url = QUrl(f"{api_url}/admin/api.php?status&auth={api_key}")
        request = QNetworkRequest(url)
        request.setAttribute(QNetworkRequest.User, "status")
        self.network_manager.get(request)

    def toggle_status(self, api_url: str, api_key: str, enable: bool) -> None:
        action = "enable" if enable else "disable"
        url = QUrl(f"{api_url}/admin/api.php?{action}&auth={api_key}")
        request = QNetworkRequest(url)
        self.network_manager.get(request)

    def _handle_network_reply(self, reply: QNetworkReply) -> None:
        try:
            if reply.error() == QNetworkReply.NoError:
                response = reply.readAll()
                data = json.loads(str(response, 'utf-8'))
                
                request_type = reply.request().attribute(QNetworkRequest.User)
                if request_type == "status":
                    self.status_updated.emit(data.get("status") == "enabled")
                elif request_type == "summary":
                    self.summary_updated.emit(data)
            else:
                self.error_occurred.emit(reply.errorString())
        except json.JSONDecodeError:
            self.error_occurred.emit("Invalid JSON response")
        finally:
            reply.deleteLater()