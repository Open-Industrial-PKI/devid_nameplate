import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QPushButton, QLabel
import requests
import time


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('API Steuerung')

        # Create tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create first tab
        self.tab1 = QWidget()
        self.tabs.addTab(self.tab1, 'Steuerung')

        # Add buttons to first tab
        self.button1 = QPushButton('Button 1', self.tab1)
        self.button1.move(50, 50)
        self.button2 = QPushButton('Button 2', self.tab1)
        self.button2.move(50, 100)

        # Create second tab
        self.tab2 = QWidget()
        self.tabs.addTab(self.tab2, 'API Ergebnis')

        # Add label to second tab
        self.label = QLabel(self.tab2)
        self.label.move(50, 50)

        # Start timer to periodically update the label
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_label)
        self.timer.start(5000)  # Update every 5 seconds

    def update_label(self):
        # Perform API call and update label text
        response = requests.get('https://api.example.com')
        self.label.setText(response.text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())