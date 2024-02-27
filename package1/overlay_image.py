import sys
import time
import threading
from PyQt5.QtCore import Qt, QTimer, QPoint, QSize, QTime
from PyQt5.QtGui import QPainter, QBrush, QColor
from PyQt5.QtWidgets import QApplication, QWidget
from detect_change import CharacterScanner

# Define the speed at which the box moves
box_speed = QPoint(0, 1)
# Define the monitor region to capture
mon = {'top': 0, 'left': 0, 'width': 150, 'height': 100}
scanner = CharacterScanner(mon)

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
        # Set the size of the box to be the same as the screen size
        self.box_size = QSize(self.screen_width, self.screen_height)
        # Set the initial position of the box to be in the middle of the screen
        self.box_position = QPoint(int((self.screen_width - self.box_size.width()) / 2), 0)

        # Show the window
        self.show()

        # Create a QTimer object for the animation
        self.animation_timer = QTimer(self)
        # Connect the timeout signal of the timer to the moveBox method
        self.animation_timer.timeout.connect(self.moveBox)
        # Set the duration of the animation to 9 seconds
        self.animation_duration = 9000
        # Start the timer to update approximately every 16 milliseconds (about 60 FPS)
        self.animation_timer.start(16)
        # Store the current time as the start time of the animation
        self.start_time = QTime.currentTime()

        # Create a QTimer object for the loop
        self.loop_timer = QTimer(self)
        # Connect the timeout signal of the timer to the resetBox method
        self.loop_timer.timeout.connect(self.resetBox)
        # Set the duration of the loop to 10 seconds
        self.loop_duration = 10000
        # Start the loop timer
        self.loop_timer.start(self.loop_duration)

    # Define the method to move the box
    def moveBox(self):
        # Calculate the elapsed time since the start of the animation
        elapsed_time = self.start_time.msecsTo(QTime.currentTime())
        # Calculate the progress of the animation
        progress = elapsed_time / self.animation_duration

        # Calculate the new y-coordinate of the box based on the progress
        new_y = round(progress * self.screen_height)

        # Update the y-coordinate of the box
        self.box_position.setY(new_y)

        # Repaint the widget to reflect the new position of the box
        self.update()

        # If the animation is complete, stop the timer
        if progress >= 1:
            self.animation_timer.stop()

    # Define the method to reset the box
    def resetBox(self):
        character_found = scanner.scan_for_character()

        if character_found:
            # Reset the y-coordinate of the box to the top of the screen
            self.box_position.setY(0)

             # Restart the animation timer
            self.animation_timer.start(16)

            # Reset the start time of the animation to the current time
            self.start_time = QTime.currentTime()

    # Define the method to paint the widget
    def paintEvent(self, event):
        # Create a QPainter object
        painter = QPainter(self)
        # Enable antialiasing
        painter.setRenderHint(QPainter.Antialiasing)

        # Set the brush to a transparent color and draw a rectangle covering the entire widget
        painter.setBrush(QBrush(QColor(0, 0, 0, 0)))
        painter.drawRect(self.rect())

        # Set the brush to black and draw the box
        painter.setBrush(QBrush(Qt.black))
        painter.drawRect(self.box_position.x(), self.box_position.y(), self.box_size.width(), self.box_size.height())

    # Define the method to handle mouse press events
    def mousePressEvent(self, event):
        # If the middle mouse button is pressed, close the window
        if event.button() == Qt.MiddleButton:
            self.close()

# Define the main function
def main():
    # Create a QApplication object
    app = QApplication(sys.argv)
    # Create a GameOverlay object
    overlay = GameOverlay()
    # Enter the main event loop of the application
    sys.exit(app.exec_())

# If this script is run directly (not imported as a module), call the main function
if __name__ == '__main__':
    main()

