import sys
import time
from PyQt5.QtCore import Qt, QTimer, QPoint, QSize, QTime, QPropertyAnimation, QRect
from PyQt5.QtGui import QPainter, QBrush, QColor
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QPushButton
from detect_change import CharacterScanner

class AnimatedWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Set the window flags to make the window frameless and always on top
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # Set the window attribute to make the background translucent
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Get the primary screen of the application
        screen = QApplication.primaryScreen()
        # Get the geometry of the screen (i.e., its resolution)
        screen_geometry = screen.geometry()

        # Store the width and height of the screen
        self.screen_width = screen_geometry.width()
        self.screen_height = screen_geometry.height()

        # Set the geometry of the window to cover the entire screen
        self.setGeometry(0, 0, self.screen_width, self.screen_height)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.frame = QFrame(self)
        self.frame.setStyleSheet('background-color: black;')
        self.frame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.frame.resize(3840, 1600)

        # Create a QPropertyAnimation instance
        self.animation = QPropertyAnimation(self.frame, b"geometry")

        # Set the duration of the animation to 9000 ms (9 seconds)
        self.animation.setDuration(9000)
        
        initial_geometry = self.frame.geometry()
        # Set the start value of the animation to the initial geometry of the widget
        self.animation.setStartValue(initial_geometry)

        # Set the end value of the animation to the desired final geometry of the widget
        self.animation.setEndValue(QRect(-initial_geometry.x(), initial_geometry.height(), initial_geometry.width(), initial_geometry.height()))
        # Start the animation
        self.animation.start()

app = QApplication([])
window = AnimatedWidget()
window.show()
app.exec_()
