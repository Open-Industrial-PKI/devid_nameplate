from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QPixmap, QMovie
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QDialog, QPushButton
import logging

from gui.funs.rest_threads import RestThread


class NameplateLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(250, 40)
        self.move(30, 30)
        self.setWordWrap(True)
        font = QFont()
        font.setItalic(True)
        font.setPointSize(12)
        self.setFont(font)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw border
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor("black"), 2))
        painter.drawRoundedRect(self.rect(), 10, 10)

        super().paintEvent(event)


class OutputLabel(QLabel):
    def __init__(self, size_height=250, size_width=320, parent=None):
        super(OutputLabel, self).__init__(parent)
        dpi = self.logicalDpiX()  # Get the DPI of the screen in X direction
        radius_mm = 2  # Corner radius in millimeters
        radius_px = int(radius_mm * dpi / 25.4)  # Convert millimeters to pixels
        margin_px = 20  # Margin in pixels
        self.setFixedSize(size_width, size_height)
        self.move(40, 40)
        self.setWordWrap(True)
        self.setStyleSheet(f"background-color: white; border-radius: {radius_px}px; padding: {margin_px}px;")
        self.setContentsMargins(margin_px, margin_px, margin_px, margin_px)


class StatusIndicator(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(20, 20)

        self.setStyleSheet("""
                   StatusIndicator {
                       background-color: #d9d9d9;
                   }
               """)

    def postive(self):
        self.setStyleSheet("background-color: green;")

    def negative(self):
        self.setStyleSheet("background-color: red;")

    def reset(self):
        self.setStyleSheet("background-color: #d9d9d9;")

class ProductQrCode(QDialog):
    def __init__(self):
        super(ProductQrCode, self).__init__()

        # Set dialog properties
        self.setWindowTitle('Product QR Code')
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setModal(True)

        # Create layout for the dialog
        layout = QVBoxLayout()

        # Add label to the layout
        label = QLabel("Scan code to see product information")
        label.setWordWrap(True)
        layout.addWidget(label)

        icon_product_info = IconWithSize(icon_path="/home/admin/devid_nameplate/icons/qr_open_ind_pki.png", width=100, height=100)
        layout.addWidget(icon_product_info)

        # Add "Close" button to the layout
        close_button = QPushButton("Close")
        layout.addWidget(close_button)
        close_button.clicked.connect(self.close)

        self.setLayout(layout)

        self.setFixedSize(300, 150)

        # Set background color
        self.setStyleSheet("background-color: #FFFFFF;")

class KeyLimitedReachedDialog(QDialog):
    def __init__(self):
        super(KeyLimitedReachedDialog, self).__init__()

        # Set dialog properties
        self.setWindowTitle('Key limit reached')
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setModal(True)

        self.loading_spinner = LoadingSpinner()


        # Create layout for the dialog
        layout = QVBoxLayout()

        # Add label to the layout
        label = QLabel("Maximum number of keys on HSM reached. Please delete keys if you want to continue provisioning")
        label.setWordWrap(True)
        layout.addWidget(label)

        # Add "Close" button to the layout
        close_button = QPushButton("Close")
        layout.addWidget(close_button)
        close_button.clicked.connect(self.close)

        # Delete all objects

        self.rest_thread_delete_all_keys = RestThread(base_url='http://0.0.0.0:5000/v1',
                                                    endpoint="/mgmt/delete/keys-all",
                                                    delete=True)
        self.rest_thread_delete_all_keys.rest_response.connect(self.delete_all_keys_complete)


        button_delete_all_objects = QPushButton("Delete All Objects")
        layout.addWidget(button_delete_all_objects)
        button_delete_all_objects.clicked.connect(self.delete_all_keys)

        # Delete LDev Objects

        self.rest_thread_delete_ldev_keys = RestThread(base_url='http://0.0.0.0:5000/v1',
                                                    endpoint="/mgmt/delete/keys-ldev",
                                                    delete=True)
        self.rest_thread_delete_ldev_keys.rest_response.connect(self.delete_ldev_keys_complete)


        button_delete_ldev_objects = QPushButton("Delete LDev Objects")
        layout.addWidget(button_delete_ldev_objects)
        button_delete_ldev_objects.clicked.connect(self.delete_ldev_keys)

        self.setLayout(layout)

        self.setFixedSize(300, 150)

        # Set background color
        self.setStyleSheet("background-color: #FFFFFF;")

    def delete_all_keys(self):
        # Show loading spinner in full screen when button is clicked
        self.loading_spinner.setWindowState(
            self.loading_spinner.windowState() | Qt.WindowFullScreen)  # Set the window to be fullscreen
        self.loading_spinner.show()

        self.rest_thread_delete_all_keys.start()

    def delete_all_keys_complete(self):
        # Hide loading spinner when REST call is complete
        self.loading_spinner.hide()

        response = self.rest_thread_delete_all_keys.response
        #self.logger.info(repr(json.dumps(response["message"]))[2:-2])

    def delete_ldev_keys(self):
        # Show loading spinner in full screen when button is clicked
        self.loading_spinner.setWindowState(
            self.loading_spinner.windowState() | Qt.WindowFullScreen)  # Set the window to be fullscreen
        self.loading_spinner.show()

        self.rest_thread_delete_ldev_keys.start()

    def delete_ldev_keys_complete(self):
        # Hide loading spinner when REST call is complete
        self.loading_spinner.hide()

        response = self.rest_thread_delete_ldev_keys.response
        #self.logger.info(repr(json.dumps(response["message"]))[2:-2])



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


class NameplateLabelHeader(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setFixedSize(150, 40)
        self.move(15, 15)
        font = QFont()
        font.setPointSize(20)
        self.setFont(font)


class CertOutput(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(350, 250)
        self.move(15, 15)
        self.setWordWrap(True)
        font = QFont()
        font.setPointSize(6)
        self.setFont(font)


class StatusLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setFixedSize(150, 40)
        self.move(30, 30)
        self.setWordWrap(True)
        font = QFont()
        font.setPointSize(16)
        self.setFont(font)


class NameplateHeader(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setFixedSize(200, 40)
        self.move(30, 30)
        self.setWordWrap(True)
        font = QFont()
        font.setBold(True)
        font.setPointSize(20)
        self.setFont(font)


class QTextEditHandler(logging.Handler):
    def __init__(self, widget):
        logging.Handler.__init__(self)
        self.widget = widget

    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)


class IconWithSize(QLabel):
    def __init__(self, icon_path, width=80, height=40):
        super().__init__()

        # Load the icon from the file path
        pixmap = QPixmap(icon_path)
        icon_size = QSize(width, height)

        scaled_pixmap = pixmap.scaled(icon_size)

        # Set the pixmap of the label
        self.setPixmap(scaled_pixmap)
