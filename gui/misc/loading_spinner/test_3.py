from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QTabWidget, QPushButton, QDesktopWidget, QDialog
from PyQt5.QtGui import QMovie
import sys
import requests
import time

class LoadingSpinner(QDialog):
    def __init__(self):
        super(LoadingSpinner, self).__init__()

        # Set dialog properties
        self.setWindowTitle('Loading...')
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setModal(True)

        # Set spinner label properties
        self.spinner_label = QLabel()
        self.spinner_label.setAlignment(Qt.AlignCenter)

        # Set spinner movie
        movie = QMovie('/home/admin/devid_nameplate/gui/misc/loading_spinner/giphy.gif')
        self.spinner_label.setMovie(movie)
        movie.start()

        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(self.spinner_label)
        self.setLayout(layout)

        # Set background color
        self.setStyleSheet("background-color: #FFFFFF;")

class RestThread(QThread):
    rest_response = pyqtSignal()

    def __init__(self, rest_url):
        super(RestThread, self).__init__()
        self.rest_url = rest_url

    def run(self):
        response = requests.get(self.rest_url)
        self.response = response.json()
        time.sleep(3)

        self.rest_response.emit()

class RestCallHandler:
    def __init__(self):
        self.loading_spinner = LoadingSpinner()
        self.rest_threads = []

    def handle_button_click(self, rest_url):
        # Show loading spinner in full screen
        self.loading_spinner.setWindowState(self.loading_spinner.windowState() | Qt.WindowFullScreen)
        self.loading_spinner.show()

        # Create REST thread and start it
        rest_thread = RestThread(rest_url)
        rest_thread.rest_response.connect(self.handle_rest_complete)
        self.rest_threads.append(rest_thread)
        rest_thread.start()

    def handle_rest_complete(self):
        # Hide loading spinner
        self.loading_spinner.hide()

        # Get the response from the sender
        sender = self.sender()
        response = "Response: {}".format(sender.response)

        # Create a QLabel to display the response
        label = QLabel(response)

        # Add the QLabel to a layout
        layout = QVBoxLayout()
        layout.addWidget(label)

        # Create a new QDialog to display the response
        dialog = QDialog()
        dialog.setWindowTitle('REST Response')
        dialog.setLayout(layout)

        # Show the QDialog
        dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle('My Application')
    window.setGeometry(100, 100, 800, 600)

    central_widget = QTabWidget()
    window.setCentralWidget(central_widget)

    tab1 = QWidget()
    tab2 = QWidget()
    central_widget.addTab(tab1, 'Tab 1')
    central_widget.addTab(tab2, 'Tab 2')

    rest_call_handler = RestCallHandler()

    button1 = QPushButton('Trigger REST Call 1')
    button2 = QPushButton('Trigger REST Call 2')
    button1.clicked.connect(lambda: rest_call_handler.handle_button_click('https://jsonplaceholder.typicode.com/posts/1'))
    button2.clicked.connect(lambda: rest_call_handler.handle_button_click('https://jsonplaceholder.typicode.com/posts/2'))
    window.statusBar().addWidget(button1)
    window.status
