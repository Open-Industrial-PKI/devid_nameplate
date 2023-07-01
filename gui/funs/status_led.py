from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import QWidget
import threading
import requests
from requests.exceptions import Timeout

from gui.funs.rest import RestApiClient


class RestLed(QWidget):
    def __init__(self, url, endpoint, parent=None):
        super().__init__(parent)

        self.url = url
        self.endpoint = endpoint
        self.color_on = QColor(124,252,0)
        self.color_off = QColor(255,99,71)
        self.state = False

        self.update_state()  # Call update_state when initialized

        # Create a timer to call update_state every 30 seconds
        self.timer = QTimer(self)
        self.timer.setInterval(30000)  # call API every 30 seconds
        self.timer.timeout.connect(self.update_state)
        self.timer.start()

    def update_state(self):
        try:
            call = RestApiClient(base_url=self.url)
            response = None
            try:
                response = call.post(endpoint=self.endpoint)
            except Timeout:
                print("Timeout occurred while making REST call.")
                self.state = False
            if response and "success" in response:
                self.state = response["success"]
            else:
                self.state = False
        except Exception as e:
            print("Error:", e)
            self.state = False

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        #painter.setRenderHint(QPainter.Antialiasing)

        if self.state:
            painter.setBrush(self.color_on)
        else:
            painter.setBrush(self.color_off)

        painter.drawEllipse(0, 5, 30, 30)
