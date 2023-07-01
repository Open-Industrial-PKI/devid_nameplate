import sys
import json
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('API Steuerung')

        # Set style sheet
        self.setStyleSheet('''
            QPushButton {
                background-color: #EFEFEF;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #DDDDDD;
            }
            QLabel {
                background-color: #EFEFEF;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px;
            }
        ''')

        # Create tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create first tab
        self.tab1 = QWidget()
        self.tabs.addTab(self.tab1, 'Steuerung')

        # Add buttons to first tab
        layout = QVBoxLayout(self.tab1)
        self.button1 = QPushButton('Button 1', self.tab1)
        self.button2 = QPushButton('Button 2', self.tab1)
        layout.addWidget(self.button1)
        layout.addWidget(self.button2)

        # Connect buttons to API calls
        self.button1.clicked.connect(self.api_call_1)
        self.button2.clicked.connect(self.api_call_2)

        # Create second tab
        self.tab2 = QWidget()
        self.tabs.addTab(self.tab2, 'API Ergebnis')

        # Add label to second tab
        self.label = QLabel(self.tab2)
        layout = QVBoxLayout(self.tab2)
        layout.addWidget(self.label)

    def api_call_1(self):
        # Perform API call 1 and update label text
        response = requests.get('https://api.example.com/1')
        data = json.loads(response.text)
        self.label.setText(str(data))

    def api_call_2(self):
        # Perform API call 2 and update label text
        response = requests.get('https://api.example.com/2')
        data = json.loads(response.text)
        self.label.setText(str(data))

    def update_label(self):
        # Perform API call and update label text
        response = requests.get('https://api.example.com')
        self.label.setText(response.text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())