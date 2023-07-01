import sys
import json
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QPushButton, QLabel, \
    QGridLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QPainter
from gui.funs.rest import RestApiClient
from gui.funs.status_led import RestLed

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('IEEE 802.1 AR GUI')

        # Set style sheet
        self.setStyleSheet('''
            QPushButton {
                background-color: #EFEFEF;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 3px;
                color: black;
                font-size: 10pt;
            }
            QTabBar::tab {
                margin-left:2px;
                margin-right:2px;
                margin-top:2px;
                background-color: #EFEFEF;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px;
                color: black;
            }
            QPushButton:hover {
                background-color: #DDDDDD;
            }
            QLabel {
                background-color: #EFEFEF;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 3px;
                margin: 3px;
                color: black;
                font-size: 6pt;
            }
        ''')

        self.results_control = []
        self.results_idev_cycle = []
        self.results_ldev_cycle = []

        self.color_on = QColor(Qt.green)
        self.color_off = QColor(Qt.red)
        #self.state = False

        # Create tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # ------------------
        # Tab for Status
        # ------------------

        self.status_grid = QGridLayout()
        self.status_grid.setSpacing(5)

        # Status for REST API
        self.status_idev = QLabel("REST API")
        self.status_grid.addWidget(self.status_idev, 0, 0)
        rest_led = RestLed(url="https://api.example.com/check-status", endpoint="/v1")
        self.status_grid.addWidget(rest_led, 0, 1)

        # Status for HSM
        self.status_idev = QLabel("HSM")
        self.status_grid.addWidget(self.status_idev, 1, 0)
        rest_led = RestLed(url="https://api.example.com/check-status", endpoint="/v1")
        self.status_grid.addWidget(rest_led, 1, 1)

        # Status for IDevID
        self.status_idev = QLabel("IDevID")
        self.status_grid.addWidget(self.status_idev, 2, 0)
        rest_led = RestLed(url="https://api.example.com/check-status", endpoint="/v1")
        self.status_grid.addWidget(rest_led, 2, 1)

        # Status for IDevID
        self.status_idev = QLabel("LDevID")
        self.status_grid.addWidget(self.status_idev, 3, 0)
        rest_led = RestLed(url="https://api.example.com/check-status", endpoint="/v1")
        self.status_grid.addWidget(rest_led, 3, 1)

        self.tab0 = QWidget()
        self.tabs.addTab(self.tab0, 'Status')
        self.tab0.setLayout(self.status_grid)

        # ------------------
        # Tab for Control
        # ------------------

        # Create first tab
        self.control_grid = QGridLayout()
        self.control_grid.setSpacing(5)

        self.result_label = QLabel(self)
        self.result_label.move(80, 80)
        self.result_label.setWordWrap(True)

        self.control_grid.addWidget(self.result_label, 0, 2, 3, 2)


        # Create buttons for first tab
        self.button1 = QPushButton('Button 1')
        self.button2 = QPushButton('Button 2')
        self.button3 = QPushButton('Button 3')
        self.control_grid.addWidget(self.button1, 0, 0)
        self.control_grid.addWidget(self.button2, 1, 0)
        self.control_grid.addWidget(self.button3, 2, 0)

        # Create LED label and add to grid
        # Button 1
        self.button_1_led = QLabel()
        self.button_1_led.setFixedSize(20, 20)
        self.control_grid.addWidget(self.button_1_led, 0, 1)
        # Button 2
        self.button_2_led = QLabel()
        self.button_2_led.setFixedSize(20, 20)
        self.control_grid.addWidget(self.button_2_led, 1, 1)
        # Button 2
        self.button_3_led = QLabel()
        self.button_3_led.setFixedSize(20, 20)
        self.control_grid.addWidget(self.button_3_led, 2, 1)


        # Connect buttons to API calls and update labels
        self.button1.clicked.connect(lambda: self.api_call_1())
        self.button2.clicked.connect(lambda: self.api_call_2())
        self.button3.clicked.connect(lambda: self.api_call_3())

        self.tab1 = QWidget()
        self.tabs.addTab(self.tab1, 'Control')
        self.tab1.setLayout(self.control_grid)

        # ------------------
        # Tab for the IDevID
        # ------------------
        self.tab2 = QWidget()
        self.tabs.addTab(self.tab2, 'IDevID')

        # Add label for IDevID
        self.output_idev = QLabel(self.tab2)
        self.output_idev.setWordWrap(True)
        layout = QVBoxLayout(self.tab2)
        layout.addWidget(self.output_idev)



        # Set up timer for IDevID API call
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.cycle_idev_api_call)
        self.timer.start(5000)

        # ------------------
        # Tab for the LDevID
        # ------------------
        self.tab3 = QWidget()
        self.tabs.addTab(self.tab3, 'LDevID')

        # Add label for LDevID
        self.output_ldev = QLabel(self.tab3)
        self.output_ldev.setWordWrap(True)

        layout = QVBoxLayout(self.tab3)
        layout.addWidget(self.output_ldev)

        # Set up timer for LDevID API call
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.cycle_ldev_api_call)
        self.timer.start(5000)

    def api_call_1(self):
        # Perform API call 1 and store result in data_1 variable
        call = RestApiClient(base_url='https://api.example.com/1')
        response = call.get(endpoint="/v1")
        print(response)
        if response['success']:
            self.button_1_led.setStyleSheet("background-color: green")
        else:
            self.button_1_led.setStyleSheet("background-color: red")
        #print(response)
        self.results_control.append(json.dumps(response))
        self.result_label.setText(json.dumps(self.results_control[-1]))

    def api_call_2(self):
        # Perform API call 1 and store result in data_1 variable
        call = RestApiClient(base_url='https://api.example.com/1')
        response = call.get(endpoint="/v1")
        print(response)
        if response['success']:
            self.button_2_led.setStyleSheet("background-color: green")
        else:
            self.button_2_led.setStyleSheet("background-color: red")
        #print(response)
        self.results_control.append(json.dumps(response))
        self.result_label.setText(json.dumps(self.results_control[-1]))

    def api_call_3(self):
        # Perform API call 1 and store result in data_1 variable
        call = RestApiClient(base_url='https://api.example.com/1')
        response = call.get(endpoint="/v1")
        print(response)
        if response['success']:
            self.button_3_led.setStyleSheet("background-color: green")
        else:
            self.button_3_led.setStyleSheet("background-color: red")
        #print(response)
        self.results_control.append(json.dumps(response))
        self.result_label.setText(json.dumps(self.results_control[-1]))

    def cycle_idev_api_call(self):
        # Perform API call 3 and update label text
        call = RestApiClient(base_url='https://api.example.com/1')
        response = call.post(endpoint="/v1")
        self.results_idev_cycle.append(json.dumps(response))
        self.output_idev.setText(json.dumps(self.results_idev_cycle[-1]))

    def cycle_ldev_api_call(self):
        # Perform API call 3 and update label text
        call = RestApiClient(base_url='https://api.example.com/1')
        response = call.post(endpoint="/v1")
        self.results_ldev_cycle.append(json.dumps(response))
        self.output_ldev.setText(json.dumps(self.results_ldev_cycle[-1]))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())