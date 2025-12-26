import json
from PyQt5.QtCore import QObject, pyqtSignal, QUrl, QUrlQuery
from PyQt5.QtNetwork import QNetworkRequest
from qgis.core import QgsNetworkAccessManager

class OverpassService(QObject):
    """
    Handles all communication with the Overpass API asynchronously.
    """
    # Define custom signals to communicate results back to the UI
    buildingFound = pyqtSignal(int)      # Emits the OSM ID
    errorOccurred = pyqtSignal(str)     # Emits error messages

    def __init__(self, parent=None):
        super().__init__(parent)
        self.nam = QgsNetworkAccessManager.instance()

    def get_building_id_at(self, lat, lon):
        """Triggers an asynchronous search for a building."""
        url = QUrl("https://overpass-api.de/api/interpreter")
        query = f'[out:json];way["building"](around:15,{lat},{lon});out ids;'
        
        # Prepare the POST data
        params = QUrlQuery()
        params.addQueryItem("data", query)
        data_bytes = params.toString(QUrl.FullyEncoded).encode('utf-8')
        
        request = QNetworkRequest(url)
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/x-www-form-urlencoded")
        
        # Send request
        reply = self.nam.post(request, data_bytes)
        
        # Connect to the internal handler
        reply.finished.connect(lambda: self._handle_reply(reply))

    def _handle_reply(self, reply):
        """Processes the raw response from the server."""
        if reply.error():
            self.errorOccurred.emit(f"Network Error: {reply.errorString()}")
        else:
            try:
                content = reply.readAll()
                data = json.loads(str(content, 'utf-8'))
                elements = data.get('elements', [])
                
                if elements:
                    osm_id = elements[0].get('id')
                    self.buildingFound.emit(osm_id)
                else:
                    self.errorOccurred.emit("No building found near this coordinate.")
            except Exception as e:
                self.errorOccurred.emit(f"Parsing Error: {str(e)}")
        
        reply.deleteLater() # Crucial for memory management