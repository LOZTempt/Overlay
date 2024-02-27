import sys
import time
import threading
from PyQt5.QtCore import Qt, QTimer, QPoint, QSize, QTime, QPropertyAnimation, QRect
from PyQt5.QtGui import QPainter, QBrush, QColor
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QPushButton
from detect_change import CharacterScanner

# Define the monitor region to capture
mon = {'top': 0, 'left': 0, 'width': 150, 'height': 100}
scanner = CharacterScanner(mon)

# Create a new thread to run the scan_for_character function
scan_thread = threading.Thread(target=scanner.scan_for_character)
# Start the new thread
scan_thread.start()
scan_thread.join()

# Define a new class, GameOverlay, that inherits from QWidget
class GameOverlay(QWidget):
    def __init__(self):
        # Call the constructor of the parent class, QWidget
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
        print(initial_geometry)
        # Set the start value of the animation to the initial geometry of the widget
        self.animation.setStartValue(initial_geometry)

        # Set the end value of the animation to the desired final geometry of the widget
        self.animation.setEndValue(QRect(-initial_geometry.x(), initial_geometry.height(), initial_geometry.width(), initial_geometry.height()))
        # Connect the finished signal of the animation to the resetBox method
        self.animation.finished.connect(self.resetBox)
        # Start the animation
        self.animation.start()

       # Create a new thread to run the checkCharacter function
        self.check_thread = threading.Thread(target=self.checkCharacter)
        # Start the new thread
        self.check_thread.start()
        
    def checkCharacter(self):
        while True:
            character_found = scanner.scan_for_character()
            if character_found:
                self.resetBox()
            time.sleep(1)  # Check every second
        
    # Define the method to reset the box
    def resetBox(self):
        initial_geometry = QRect(0, 0, 3840, 1600)

        self.animation.stop()
        # Reset the y-coordinate of the box to the top of the screen
        self.animation.setStartValue(initial_geometry)  
        self.animation.setEndValue(QRect(-initial_geometry.x(), initial_geometry.height(), initial_geometry.width(), initial_geometry.height()))
        self.animation.start()


    # Define the method to handle mouse press events
    def mousePressEvent(self, event):
        # If the middle mouse button is pressed, close the window
        if event.button() == Qt.MiddleButton:
            self.close()

# Define the main function
def main():
    app = QApplication(sys.argv)
    # Create a GameOverlay object
    overlay = GameOverlay()    
    overlay.show()
    # Enter the main event loop of the application
    sys.exit(app.exec_())

# If this script is run directly (not imported as a module), call the main function
if __name__ == '__main__':
    main()

