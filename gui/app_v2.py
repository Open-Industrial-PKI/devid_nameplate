import json
import sys
import os

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QPushButton, \
    QGridLayout, QDesktopWidget, QTextEdit
from PyQt5.QtGui import QIcon

from gui.funs.custom_objects import StatusLabel, QTextEditHandler, StatusIndicator, IconWithSize, NameplateHeader, \
    NameplateLabel, NameplateLabelHeader, CertOutput, LoadingSpinner, OutputLabel, KeyLimitedReachedDialog, \
    ProductQrCode
from gui.funs.status_led import RestLed
from gui.funs.rest_threads import RestThread

import logging

os.environ['QT_LOGGING_RULES'] = 'qt.qpa.*=False'


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
            QPushButton:disabled { 
                background-color: #6c88b2; 
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
                font-size: 8pt;
            }
            QTabBar::tab:selected {
                background-color: #adacac;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #DDDDDD;
            }
        ''')

        self.results_control_ldev = []
        self.results_control_idev = []
        self.results_idev_cycle = []
        self.results_ldev_cycle = []

        self.color_on = QColor(124, 252, 0)
        self.color_off = QColor(255, 99, 71)
        # self.state = False

        # Create tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Get the size of the screen
        screen_size = QDesktopWidget().screenGeometry().size()
        # Set the maximum size of the label to fit on the screen
        max_width = int(screen_size.width() * 1)  # Use 90% of the screen width
        max_height = int(screen_size.height() * 0.9)  # Use 90% of the screen height

        # Create loading spinner
        self.loading_spinner = LoadingSpinner()
        self.key_limit_reached_dialog = KeyLimitedReachedDialog()
        self.product_qr_code_dialog = ProductQrCode()

        # ------------------
        # Tab for Status
        # ------------------

        self.log_grid = QGridLayout()

        # Create a QTextEdit widget to display log messages
        self.log_widget = QTextEdit()
        self.log_grid.addWidget(self.log_widget)

        # Create a logger and add the QTextEditHandler to it
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        handler = QTextEditHandler(self.log_widget)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.tab_logs = QWidget()
        self.tabs.addTab(self.tab_logs, 'Logs')
        self.tab_logs.setLayout(self.log_grid)

        # ------------------
        # Tab for Status
        # ------------------

        self.status_grid = QGridLayout()
        self.status_grid.setSpacing(5)

        # Status for REST API
        self.status_label_rest = StatusLabel("REST API")
        self.status_grid.addWidget(self.status_label_rest, 0, 0)
        rest_led = RestLed(url="http://0.0.0.0:5000/v1", endpoint="/mgmt/status/rest")
        self.status_grid.addWidget(rest_led, 0, 1)

        # Status for HSM
        self.status_label_hsm = StatusLabel("HSM")
        self.status_grid.addWidget(self.status_label_hsm, 1, 0)
        hsm_led = RestLed(url="http://0.0.0.0:5000/v1", endpoint="/mgmt/status/hsm")
        self.status_grid.addWidget(hsm_led, 1, 1)

        # Status for IDevID
        self.status_label_idev = StatusLabel("IDevID")
        self.status_grid.addWidget(self.status_label_idev, 2, 0)
        idev_led = RestLed(url="http://0.0.0.0:5000/v1", endpoint="/mgmt/status/idevid")
        self.status_grid.addWidget(idev_led, 2, 1)

        # Status for LDevID
        self.status_label_ldev = StatusLabel("LDevID")
        self.status_grid.addWidget(self.status_label_ldev, 3, 0)
        ldev_led = RestLed(url="http://0.0.0.0:5000/v1", endpoint="/mgmt/status/ldevid")
        self.status_grid.addWidget(ldev_led, 3, 1)

        # Status for EJBCA
        self.status_label_ejbca = StatusLabel("EJBCA")
        self.status_grid.addWidget(self.status_label_ejbca, 4, 0)
        ejbca_led = RestLed(url="http://0.0.0.0:5000/v1", endpoint="/mgmt/status/ejbca")
        self.status_grid.addWidget(ejbca_led, 4, 1)

        self.tab0 = QWidget()
        self.tabs.addTab(self.tab0, 'Status')
        self.tab0.setLayout(self.status_grid)

        close_button = QPushButton('Close Application', self)
        close_button.clicked.connect(self.close)
        self.status_grid.addWidget(close_button)

        # ------------------
        # Control IDevID
        # ------------------

        # Create first tab
        self.control_grid_idev = QGridLayout()
        self.control_grid_idev.setSpacing(5)

        self.result_label_idev = OutputLabel(size_width=320, size_height=250, parent=self)

        self.control_grid_idev.addWidget(self.result_label_idev, 0, 2, 3, 2)

        self.rest_thread_provision_idev = RestThread(base_url='http://0.0.0.0:5000/v1',
                                                     endpoint="/idev-highlvl/provision",
                                                     post=True)
        self.rest_thread_provision_idev.rest_response.connect(self.provision_idev_complete)
        self.rest_thread_validate_idev = RestThread(base_url='http://0.0.0.0:5000/v1',
                                                    endpoint="/idev-highlvl/validate",
                                                    post=True)
        self.rest_thread_validate_idev.rest_response.connect(self.validate_idev_complete)
        self.rest_thread_delete_idev = RestThread(base_url='http://0.0.0.0:5000/v1',
                                                  endpoint="/idev-highlvl/delete",
                                                  delete=True)
        self.rest_thread_delete_idev.rest_response.connect(self.delete_idev_complete)

        # Create buttons for first tab
        self.button_bootstrap_idev = QPushButton('Bootstrap\nIDev')
        self.button_delete_idev = QPushButton('Delete\nIDev')
        self.button_validate_idev = QPushButton('Validate\nIDev')
        self.button_bootstrap_idev.setFixedSize(100, 40)
        self.button_delete_idev.setFixedSize(100, 40)
        self.button_validate_idev.setFixedSize(100, 40)
        self.control_grid_idev.addWidget(self.button_bootstrap_idev, 0, 0)
        self.control_grid_idev.addWidget(self.button_delete_idev, 1, 0)
        self.control_grid_idev.addWidget(self.button_validate_idev, 2, 0)

        # Create LED label and add to grid
        # Button 1
        self.led_provision_idev = StatusIndicator()
        self.control_grid_idev.addWidget(self.led_provision_idev, 0, 1)
        # Button 2
        self.led_delete_idev = StatusIndicator()
        self.control_grid_idev.addWidget(self.led_delete_idev, 1, 1)
        # Button 3
        self.led_validate_idev = StatusIndicator()
        self.control_grid_idev.addWidget(self.led_validate_idev, 2, 1)

        # Connect buttons to API calls and update labels
        self.button_delete_idev.clicked.connect(lambda: self.delete_idev())
        self.button_bootstrap_idev.clicked.connect(lambda: self.provision_idev())
        self.button_validate_idev.clicked.connect(lambda: self.validate_idev())

        self.tab_control_ldev = QWidget()
        self.tabs.addTab(self.tab_control_ldev, 'Control IDevID')
        self.tab_control_ldev.setLayout(self.control_grid_idev)

        # ------------------
        # Control LDevID
        # ------------------

        # Create first tab
        self.control_grid_ldev = QGridLayout()
        self.control_grid_ldev.setSpacing(5)

        self.result_label_ldev = OutputLabel(size_width=250, size_height=250, parent=self)

        self.control_grid_ldev.addWidget(self.result_label_ldev, 0, 4, 5, 4)

        # Create buttons for first tab
        self.icon_bootstrap_ldev_azure = IconWithSize(icon_path="/home/admin/devid_nameplate/icons/azure.png")
        self.icon_bootstrap_ldev_aws = IconWithSize(icon_path="/home/admin/devid_nameplate/icons/aws.png")
        self.icon_bootstrap_ldev_opc = IconWithSize(icon_path="/home/admin/devid_nameplate/icons/opc.png")

        # Create rest threads
        self.rest_thread_bootstrap_ldev_azure = RestThread(base_url='http://0.0.0.0:5000/v1',
                                                           endpoint="/ldev-highlvl/provision-azure",
                                                           post=True)
        self.rest_thread_bootstrap_ldev_azure.rest_response.connect(self.provision_ldev_azure_complete)
        self.rest_thread_bootstrap_ldev_aws = RestThread(base_url='http://0.0.0.0:5000/v1',
                                                         endpoint="/ldev-highlvl/provision-aws",
                                                         post=True)
        self.rest_thread_bootstrap_ldev_aws.rest_response.connect(self.provision_ldev_aws_complete)
        self.rest_thread_bootstrap_ldev_opc = RestThread(base_url='http://0.0.0.0:5000/v1',
                                                         endpoint="/ldev-highlvl/provision-opc-ua-server",
                                                         post=True)
        self.rest_thread_bootstrap_ldev_opc.rest_response.connect(self.provision_ldev_opc_complete)
        self.rest_thread_validate_ldev = RestThread(base_url='http://0.0.0.0:5000/v1',
                                                    endpoint="/ldev-highlvl/validate",
                                                    post=True)
        self.rest_thread_validate_ldev.rest_response.connect(self.validate_ldev_complete)
        self.rest_thread_delete_ldev = RestThread(base_url='http://0.0.0.0:5000/v1',
                                                  endpoint="/ldev-highlvl/delete",
                                                  delete=True)
        self.rest_thread_delete_ldev.rest_response.connect(self.delete_ldev_complete)

        self.button_bootstrap_ldev_azure = QPushButton('Bootstrap')
        self.button_bootstrap_ldev_aws = QPushButton('Bootstrap')
        self.button_bootstrap_ldev_opc = QPushButton('Bootstrap')

        self.button_delete_ldev = QPushButton('Delete\nLDev')
        self.button_validate_ldev = QPushButton('Validate\nLDev')
        self.button_delete_ldev.setFixedSize(80, 40)
        self.button_validate_ldev.setFixedSize(80, 40)

        self.control_grid_ldev.addWidget(self.icon_bootstrap_ldev_azure, 0, 0)
        self.control_grid_ldev.addWidget(self.icon_bootstrap_ldev_aws, 1, 0)
        self.control_grid_ldev.addWidget(self.icon_bootstrap_ldev_opc, 2, 0)

        self.control_grid_ldev.addWidget(self.button_bootstrap_ldev_azure, 0, 1)
        self.control_grid_ldev.addWidget(self.button_bootstrap_ldev_aws, 1, 1)
        self.control_grid_ldev.addWidget(self.button_bootstrap_ldev_opc, 2, 1)

        self.control_grid_ldev.addWidget(self.button_delete_ldev, 3, 0)
        self.control_grid_ldev.addWidget(self.button_validate_ldev, 4, 0)

        # Create LED label and add to grid
        # Button 1
        self.led_provision_ldev_azure = StatusIndicator()
        self.control_grid_ldev.addWidget(self.led_provision_ldev_azure, 0, 3)

        self.led_provision_ldev_aws = StatusIndicator()
        self.control_grid_ldev.addWidget(self.led_provision_ldev_aws, 1, 3)

        self.led_provision_ldev_opc = StatusIndicator()
        self.control_grid_ldev.addWidget(self.led_provision_ldev_opc, 2, 3)
        # Button 2
        self.led_delete_ldev = StatusIndicator()
        self.control_grid_ldev.addWidget(self.led_delete_ldev, 3, 1)
        # Button 3
        self.led_validate_ldev = StatusIndicator()
        self.control_grid_ldev.addWidget(self.led_validate_ldev, 4, 1)

        # Connect buttons to API calls and update labels
        self.button_delete_ldev.clicked.connect(lambda: self.delete_ldev())
        self.button_bootstrap_ldev_azure.clicked.connect(lambda: self.provision_ldev_azure())
        self.button_bootstrap_ldev_aws.clicked.connect(lambda: self.provision_ldev_aws())
        self.button_bootstrap_ldev_opc.clicked.connect(lambda: self.provision_ldev_opc_server())

        self.button_validate_ldev.clicked.connect(lambda: self.validate_ldev())

        self.tab_control_ldev = QWidget()
        self.tabs.addTab(self.tab_control_ldev, 'Control LDevID')
        self.tab_control_ldev.setLayout(self.control_grid_ldev)

        # ------------------
        # Tab for the IDevID
        # ------------------

        self.control_grid_act_idev = QGridLayout()
        self.control_grid_act_idev.setSpacing(3)

        self.actual_idev_nameplate = NameplateHeader('Nameplate')
        self.control_grid_act_idev.addWidget(self.actual_idev_nameplate, 0, 2)

        self.rest_thread_actual_idev = RestThread(base_url='http://0.0.0.0:5000/v1',
                                                  endpoint="/idev-highlvl/actual",
                                                  get=True)
        self.rest_thread_actual_idev.rest_response.connect(self.actual_idev_complete)

        self.button_reload_idev = QPushButton()
        icon = QIcon("/home/admin/devid_nameplate/icons/rotate-icon.png")  # Load the icon from a file path
        self.button_reload_idev.setIcon(icon)
        self.button_reload_idev.setIconSize(QSize(32, 32))
        self.button_reload_idev.setFixedSize(40, 40)
        self.control_grid_act_idev.addWidget(self.button_reload_idev, 0, 0)

        self.button_reload_idev.clicked.connect(lambda: self.load_actual_idev())


        # Button for product QR code
        self.button_qr_product_code = QPushButton()
        icon = QIcon("/home/admin/devid_nameplate/icons/rotate-icon.png")  # Load the icon from a file path
        self.button_qr_product_code.setIcon(icon)
        self.button_qr_product_code.setIconSize(QSize(32, 32))
        self.button_qr_product_code.setFixedSize(40, 40)
        self.control_grid_act_idev.addWidget(self.button_qr_product_code, 0, 1)
        self.button_reload_idev.clicked.connect(lambda: self.show_qr_dialog())

        # Producer / Organization
        self.actual_idev_producer = NameplateLabel(self)
        self.actual_idev_producer_label = NameplateLabelHeader('Producer:')

        self.control_grid_act_idev.addWidget(self.actual_idev_producer_label, 1, 0)
        self.control_grid_act_idev.addWidget(self.actual_idev_producer, 1, 1)

        # Produced
        self.actual_idev_produced = NameplateLabel(self)
        self.actual_idev_produced_label = NameplateLabelHeader("Produced:")

        self.control_grid_act_idev.addWidget(self.actual_idev_produced_label, 2, 0)
        self.control_grid_act_idev.addWidget(self.actual_idev_produced, 2, 1)

        # Pseudonym
        self.actual_idev_pseudonym = NameplateLabel(self)
        self.actual_idev_pseudonym_label = NameplateLabelHeader('Product:')

        self.control_grid_act_idev.addWidget(self.actual_idev_pseudonym_label, 3, 0)
        self.control_grid_act_idev.addWidget(self.actual_idev_pseudonym, 3, 1)

        # Serial Number
        self.actual_idev_serial = NameplateLabel(self)
        self.actual_idev_serial_label = NameplateLabelHeader('Serial No.:')

        self.control_grid_act_idev.addWidget(self.actual_idev_serial_label, 4, 0)
        self.control_grid_act_idev.addWidget(self.actual_idev_serial, 4, 1)

        # Country
        self.actual_idev_country = NameplateLabel(self)
        self.actual_idev_country_label = NameplateLabelHeader('Country:')

        self.control_grid_act_idev.addWidget(self.actual_idev_country_label, 5, 0)
        self.control_grid_act_idev.addWidget(self.actual_idev_country, 5, 1)

        self.tab_actual_idev = QWidget()
        self.tabs.addTab(self.tab_actual_idev, 'IDevID')
        self.tab_actual_idev.setLayout(self.control_grid_act_idev)

        # ------------------
        # Tab for the LDevID
        # ------------------
        self.control_grid_act_ldev = QGridLayout()
        self.control_grid_act_ldev.setSpacing(5)

        self.result_actual_ldev = CertOutput(self)

        self.control_grid_act_ldev.addWidget(self.result_actual_ldev, 0, 1, 1, 1)

        self.rest_thread_actual_ldev = RestThread(base_url='http://0.0.0.0:5000/v1',
                                                  endpoint="/ldev-highlvl/actual",
                                                  get=True)
        self.rest_thread_actual_ldev.rest_response.connect(self.actual_ldev_complete)

        self.button_reload_ldev = QPushButton()
        icon = QIcon("/home/admin/devid_nameplate/icons/rotate-icon.png")  # Load the icon from a file path
        self.button_reload_ldev.setIcon(icon)
        self.button_reload_ldev.setIconSize(QSize(32, 32))
        self.button_reload_ldev.setFixedSize(40, 40)
        self.control_grid_act_ldev.addWidget(self.button_reload_ldev, 0, 0)

        self.button_reload_ldev.clicked.connect(lambda: self.load_actual_ldev())

        self.tab_actual_ldev = QWidget()
        self.tabs.addTab(self.tab_actual_ldev, 'LDevID')
        self.tab_actual_ldev.setLayout(self.control_grid_act_ldev)

    ##################
    # IDevID functions
    ##################

    def reset_idev_status(self):
        self.led_validate_idev.reset()
        self.led_delete_idev.reset()
        self.led_provision_idev.reset()

    def delete_idev(self):
        # Show loading spinner in full screen when button is clicked
        self.loading_spinner.setWindowState(
            self.loading_spinner.windowState() | Qt.WindowFullScreen)  # Set the window to be fullscreen
        self.loading_spinner.show()
        self.reset_idev_status()

        self.rest_thread_delete_idev.start()

    def delete_idev_complete(self):
        # Hide loading spinner when REST call is complete
        self.loading_spinner.hide()

        response = self.rest_thread_delete_idev.response
        if response['success']:
            self.led_delete_idev.postive()
        else:
            self.led_delete_idev.negative()
        # print(response)
        self.results_control_idev.append(json.dumps(response["message"]))
        self.result_label_idev.setText(repr(json.dumps(response["message"]))[2:-2])

    def provision_idev(self):
        # Show loading spinner in full screen when button is clicked
        self.loading_spinner.setWindowState(
            self.loading_spinner.windowState() | Qt.WindowFullScreen)  # Set the window to be fullscreen
        self.loading_spinner.show()
        self.reset_idev_status()

        self.rest_thread_provision_idev.start()

    def provision_idev_complete(self):
        # Hide loading spinner when REST call is complete
        self.loading_spinner.hide()

        response = self.rest_thread_provision_idev.response
        if response['success']:
            self.led_provision_idev.postive()
        else:
            self.led_provision_idev.negative()
        # print(response)
        self.results_control_idev.append(json.dumps(response["message"]))
        self.result_label_idev.setText(repr(json.dumps(response["message"]))[2:-2])

    def validate_idev(self):
        # Show loading spinner in full screen when button is clicked
        self.loading_spinner.setWindowState(
            self.loading_spinner.windowState() | Qt.WindowFullScreen)  # Set the window to be fullscreen
        self.loading_spinner.show()
        self.reset_idev_status()

        self.rest_thread_validate_idev.start()

    def validate_idev_complete(self):
        # Hide loading spinner when REST call is complete
        self.loading_spinner.hide()

        response = self.rest_thread_validate_idev.response
        if response['success']:
            self.led_validate_idev.postive()
        else:
            self.led_validate_idev.negative()
        # print(response)
        self.results_control_idev.append(json.dumps(response["message"]))
        self.result_label_idev.setText(repr(json.dumps(response["message"]))[2:-2])

    ##################
    # LDevID functions
    ##################

    def reset_ldev_status(self):
        self.led_validate_ldev.reset()
        self.led_delete_ldev.reset()
        self.led_provision_ldev_opc.reset()
        self.led_provision_ldev_azure.reset()
        self.led_provision_ldev_aws.reset()

    def validate_ldev(self):
        # Show loading spinner in full screen when button is clicked
        self.loading_spinner.setWindowState(
            self.loading_spinner.windowState() | Qt.WindowFullScreen)  # Set the window to be fullscreen
        self.loading_spinner.show()
        self.reset_ldev_status()

        self.rest_thread_validate_ldev.start()

    def validate_ldev_complete(self):
        # Hide loading spinner when REST call is complete
        self.loading_spinner.hide()

        response = self.rest_thread_validate_ldev.response
        if response['success']:
            self.led_validate_ldev.postive()
        else:
            self.led_validate_ldev.negative()
        # print(response)
        self.results_control_ldev.append(json.dumps(response["message"]))
        self.result_label_ldev.setText(repr(json.dumps(response["message"]))[2:-2])

    def delete_ldev(self):
        # Show loading spinner in full screen when button is clicked
        self.loading_spinner.setWindowState(
            self.loading_spinner.windowState() | Qt.WindowFullScreen)  # Set the window to be fullscreen
        self.loading_spinner.show()
        self.reset_ldev_status()

        self.rest_thread_delete_ldev.start()

    def delete_ldev_complete(self):
        # Hide loading spinner when REST call is complete
        self.loading_spinner.hide()

        response = self.rest_thread_delete_ldev.response
        if response['success']:
            self.led_delete_ldev.postive()
        else:
            self.led_delete_ldev.negative()
        # print(response)
        self.results_control_ldev.append(json.dumps(response["message"]))
        self.result_label_ldev.setText(repr(json.dumps(response["message"]))[2:-2])

    def provision_ldev_opc_server(self):
        # Show loading spinner in full screen when button is clicked
        self.loading_spinner.setWindowState(
            self.loading_spinner.windowState() | Qt.WindowFullScreen)  # Set the window to be fullscreen
        self.loading_spinner.show()
        self.reset_ldev_status()

        self.rest_thread_bootstrap_ldev_opc.start()

    def provision_ldev_opc_complete(self):
        # Hide loading spinner when REST call is complete
        self.loading_spinner.hide()

        response = self.rest_thread_bootstrap_ldev_opc.response
        if response['success']:
            self.led_provision_ldev_opc.postive()
            if int(json.dumps(response["hsm_key_cnt"])) >= 8:
                self.key_limit_reached_dialog.show()
        else:
            self.led_provision_ldev_opc.negative()
        # print(response)
        self.results_control_ldev.append(json.dumps(response["message"]))
        self.result_label_ldev.setText(repr(json.dumps(response["message"]))[2:-2])

    def provision_ldev_azure(self):
        # Show loading spinner in full screen when button is clicked
        self.loading_spinner.setWindowState(
            self.loading_spinner.windowState() | Qt.WindowFullScreen)  # Set the window to be fullscreen
        self.loading_spinner.show()
        self.reset_ldev_status()

        self.rest_thread_bootstrap_ldev_azure.start()

    def provision_ldev_azure_complete(self):
        # Hide loading spinner when REST call is complete
        self.loading_spinner.hide()

        response = self.rest_thread_bootstrap_ldev_azure.response
        if response['success']:
            self.led_provision_ldev_azure.postive()
            if int(json.dumps(response["hsm_key_cnt"])) >= 8:
                self.key_limit_reached_dialog.show()
        else:
            self.led_provision_ldev_azure.negative()
        # print(response)
        self.results_control_ldev.append(json.dumps(response["message"]))
        self.result_label_ldev.setText(repr(json.dumps(response["message"]))[2:-2])

    def provision_ldev_aws(self):
        # Show loading spinner in full screen when button is clicked
        self.loading_spinner.setWindowState(
            self.loading_spinner.windowState() | Qt.WindowFullScreen)  # Set the window to be fullscreen
        self.loading_spinner.show()
        self.reset_ldev_status()

        self.rest_thread_bootstrap_ldev_aws.start()

    def provision_ldev_aws_complete(self):
        # Hide loading spinner when REST call is complete
        self.loading_spinner.hide()

        response = self.rest_thread_bootstrap_ldev_aws.response
        if response['success']:
            self.led_provision_ldev_aws.postive()
            if int(json.dumps(response["hsm_key_cnt"])) >= 8:
                self.key_limit_reached_dialog.show()
        else:
            self.led_provision_ldev_aws.negative()
        # print(response)
        self.logger.info("*** HSM Key count: {}".format(str(json.dumps(response["hsm_key_cnt"]))))
        self.results_control_ldev.append(json.dumps(response["message"]))
        self.result_label_ldev.setText(repr(json.dumps(response["message"]))[2:-2])

    def load_actual_idev(self):
        # Show loading spinner in full screen when button is clicked
        self.loading_spinner.setWindowState(
            self.loading_spinner.windowState() | Qt.WindowFullScreen)  # Set the window to be fullscreen
        self.loading_spinner.show()

        self.rest_thread_actual_idev.start()

    def actual_idev_complete(self):
        # Hide loading spinner when REST call is complete
        self.loading_spinner.hide()

        response = self.rest_thread_actual_idev.response
        if response["data"] is None:
            self.actual_idev_producer.setText("No IDevID set")
        else:
            self.actual_idev_producer.setText(repr(json.dumps(response["data"]["o"]))[2:-2])
            self.actual_idev_serial.setText(repr(json.dumps(response["data"]["serial_number"]))[2:-2])
            self.actual_idev_produced.setText(repr(json.dumps(response["data"]["validFrom"]))[2:-2])
            self.actual_idev_country.setText(repr(json.dumps(response["data"]["c"]))[2:-2])
            self.actual_idev_pseudonym.setText(repr(json.dumps(response["data"]["pseudonym"]))[2:-2])

    def load_actual_ldev(self):
        self.logger.info("- Load actual LDevID")
        # Show loading spinner in full screen when button is clicked
        self.loading_spinner.setWindowState(
            self.loading_spinner.windowState() | Qt.WindowFullScreen)  # Set the window to be fullscreen
        self.loading_spinner.show()

        self.rest_thread_actual_ldev.start()

    def actual_ldev_complete(self):
        # Hide loading spinner when REST call is complete
        self.loading_spinner.hide()

        response = self.rest_thread_actual_ldev.response
        try:
            if response["data"] is None:
                self.result_actual_ldev.setText("No LDevID set")
                self.logger.info("-- No LDevID set")
            else:
                orig_cert_string = repr(json.dumps(response["data"]["cert_str"]))[5:-5]
                new_cert_string = orig_cert_string.replace('\\\\n', '\n')
                new_cert_string = new_cert_string.replace('\\', '')
                self.logger.info("Result: {}".format(new_cert_string))
                self.result_actual_ldev.setText(new_cert_string)
        except Exception as err:
            self.result_actual_ldev.setText(str(err))

    def show_qr_dialog(self):
        self.product_qr_code_dialog.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
