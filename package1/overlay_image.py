from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QBrush
from PyQt5.QtCore import Qt
import sys

class CircleWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground, True)  # Make the window background transparent
        self.setGeometry(300, 300, 200, 200)  # Set the size and position of the window

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QBrush(Qt.black))  # Set the color of the circle
        painter.drawEllipse(50, 50, 100, 100)  # Draw a circle

app = QApplication(sys.argv)
circle_widget = CircleWidget()
circle_widget.show()
sys.exit(app.exec_())
