from PySide6.QtCore import QObject, QUrl
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtCore import QByteArray
import json
from PySide6.QtCore import qDebug

class AdwardAPI(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.network_manager = QNetworkAccessManager(self)
        self.network_manager.finished.connect(self.on_network_reply)
        
    def fetch_summary(self, api_url, api_key):
        """
        Fetch summary from the server application
        
        Args:
            api_url (str): Base API URL
            api_key (str): API authentication key
        """
        url = QUrl(f"{api_url}/admin/api.php?summaryRaw&auth={api_key}")
        request = QNetworkRequest(url)
        self.network_manager.get(request)
        
    def on_network_reply(self, reply):
        """
        Handle the network reply from the server
        
        Args:
            reply (QNetworkReply): The network reply object
        """
        if reply.error() == QNetworkReply.NoError:
            response = reply.readAll()
            json_response = json.loads(str(response, 'utf-8'))
            qDebug(f"Response Summary: {json_response}")
        else:
            qDebug(f"Error fetching data: {reply.errorString()}")
            
        reply.deleteLater()