import sys
import time
import json
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtCore import QTimer


class Example(QWidget):
    def __init__(self):
        super().__init__()

        self.result_label = QLabel(self)
        self.result_label.move(50, 50)

        # Create a timer that calls the function every 5 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.call_function)
        self.timer.start(5000)  # 5000 milliseconds = 5 seconds

    def call_function(self):
        # Call the function that returns a JSON-formatted string
        result = '{"name": "John", "age": 30}'

        # Parse the JSON string to a dictionary
        result_dict = json.loads(result)

        # Display the result in the label
        self.result_label.setText(f"Name: {result_dict['name']}, Age: {result_dict['age']}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    example = Example()
    example.show()

    sys.exit(app.exec_())