import sys
from PyQt5.QtCore import Qt, QTimer, QPoint, QSize, QRect
from PyQt5.QtGui import QPainter, QBrush, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget

# Global variables for box parameters
box_size = QSize(100, 100)  # Size of the black box
box_speed = QPoint(1, 1)  # Speed of box movement

class GameOverlay(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()

        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        self.setGeometry(0, 0, screen_width, screen_height)  # Set the overlay size to match the screen
        self.box_position = QPoint(0, 0)  # Initial position of the black box
        self.show()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.moveBox)
        self.timer.start(16)  # Update the overlay approximately every 16 milliseconds (about 60 FPS)

    def moveBox(self):
        # Move the box
        self.box_position += box_speed

        # If the box reaches the edge of the screen, reverse its direction
        if self.box_position.x() <= 0 or self.box_position.x() + box_size.width() >= self.width():
            box_speed.setX(-box_speed.x())
        if self.box_position.y() <= 0 or self.box_position.y() + box_size.height() >= self.height():
            box_speed.setY(-box_speed.y())

        # Trigger a repaint
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw a transparent background
        painter.setBrush(QBrush(QColor(0, 0, 0, 0)))
        painter.drawRect(self.rect())

        # Draw the black box
        painter.setBrush(QBrush(Qt.black))
        painter.drawRect(QRect(self.box_position, box_size))
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:  # Check if middle mouse button is clicked
            self.close()  # Close the overlay window

def main():
    app = QApplication(sys.argv)
    overlay = GameOverlay()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
