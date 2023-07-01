import sys
import json
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, QTimer
from gui.funs.rest import RestApiClient

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

        self.results_control = []
        self.results_cycle = []

        # Create tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create first tab
        self.tab1 = QWidget()
        self.tabs.addTab(self.tab1, 'Steuerung')

        # Add labels to first tab
        layout = QVBoxLayout(self.tab1)

        self.result_label = QLabel(self)
        self.result_label.move(50, 50)

        layout.addWidget(self.result_label)

        # Create buttons for first tab
        self.button1 = QPushButton('Button 1', self.tab1)
        self.button2 = QPushButton('Button 2', self.tab1)
        layout.addWidget(self.button1)
        layout.addWidget(self.button2)

        # Connect buttons to API calls and update labels
        self.button1.clicked.connect(lambda: self.api_call_1())
        #self.button1.clicked.connect(lambda: self.label1.setText(str(self.data_1)))
        self.button2.clicked.connect(lambda: self.api_call_2())
        #self.button2.clicked.connect(lambda: self.label2.setText(str(self.data_2)))

        # Create second tab
        self.tab2 = QWidget()
        self.tabs.addTab(self.tab2, 'API Ergebnis')

        # Add label to second tab
        self.label = QLabel(self.tab2)
        layout = QVBoxLayout(self.tab2)
        layout.addWidget(self.label)

        # Set up timer for API call
        self.timer = QTimer(self)
        #self.timer.setInterval(5000)  # set interval in milliseconds
        self.timer.timeout.connect(self.api_call_3)
        self.timer.start(5000)

    def api_call_1(self):
        # Perform API call 1 and store result in data_1 variable
        call = RestApiClient(base_url='https://api.example.com/1')
        response = call.get(endpoint="/v1")
        #print(response)
        self.results_control.append(json.dumps(response))
        self.result_label.setText(json.dumps(self.results_control[-1]))

    def api_call_2(self):
        # Perform API call 2 and store result in data_2 variable
        call = RestApiClient(base_url='https://api.example.com/1')
        response = call.post(endpoint="/v1")
        #print(response)
        self.results_control.append(json.dumps(response))
        self.result_label.setText(json.dumps(self.results_control[-1]))

    def api_call_3(self):
        # Perform API call 3 and update label text
        call = RestApiClient(base_url='https://api.example.com/1')
        response = call.post(endpoint="/v1")
        print(response)
        self.results_cycle.append(json.dumps(response))
        self.label.setText(json.dumps(self.results_cycle[-1]))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())