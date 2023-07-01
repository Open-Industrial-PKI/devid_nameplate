from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import QWidget

import requests


class RestLed(QWidget):
    def __init__(self, url, parent=None):
        super().__init__(parent)

        self.url = url
        self.color_on = QColor(Qt.green)
        self.color_off = QColor(Qt.red)
        self.state = False

        self.timer = QTimer(self)
        self.timer.setInterval(5000)  # call API every 5 seconds
        self.timer.timeout.connect(self.update_state)
        self.timer.start()

    def update_state(self):
        try:
            response = requests.get(self.url)
            data = response.json()
            self.state = data["result"]
        except Exception as e:
            print("Error:", e)
            self.state = False

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.state:
            painter.setBrush(self.color_on)
        else:
            painter.setBrush(self.color_off)

        painter.drawEllipse(0, 0, self.width(), self.height())