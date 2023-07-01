import sys

from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore
from gui.app_v2 import MyWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.setWindowState(window.windowState() | QtCore.Qt.WindowFullScreen)  # Set the window to be fullscreen
    window.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # Remove the title bar and border
    window.show()
    sys.exit(app.exec_())