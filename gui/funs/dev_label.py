import sys
from PyQt5.QtWidgets import  QLabel, QSizePolicy
from PyQt5.QtGui import QFont, QFontMetrics

class MyWidget(QLabel):
    def __init__(self, text, max_width, max_height):
        super().__init__(text)
        self.max_width = max_width
        self.max_height = max_height
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setAlignment(Qt.AlignCenter)
        self.adjust_font_size()

    def adjust_font_size(self):
        font_size = 1
        font = self.font()
        metrics = QFontMetrics(font)
        while (metrics.width(self.text()) < self.max_width and
               metrics.height() < self.max_height):
            font_size += 1
            font.setPointSize(font_size)
            metrics = QFontMetrics(font)
        font.setPointSize(font_size - 1)
        self.setFont(font)