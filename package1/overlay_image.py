import sys
from PyQt5.QtCore import Qt, QTimer, QPoint, QSize, QEasingCurve
from PyQt5.QtGui import QPainter, QBrush, QColor
from PyQt5.QtWidgets import QApplication, QWidget

box_speed = QPoint(0, 1)

class GameOverlay(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()

        self.screen_width = screen_geometry.width()
        self.screen_height = screen_geometry.height()

        self.setGeometry(0, 0, self.screen_width, self.screen_height)
        self.box_size = QSize(self.screen_width, self.screen_height)
        self.box_position = QPoint(int((self.screen_width - self.box_size.width()) / 2), 0)

        self.show()

        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.moveBox)
        self.animation_duration = 9000  # 9 seconds
        self.animation_timer.start(16)  # Update approximately every 16 milliseconds (about 60 FPS)

    def moveBox(self):
        self.box_position.setY(self.box_position.y() + box_speed.y())

        # Check if the box has reached the bottom of the screen
        if self.box_position.y() >= self.height():
            # Reset the box's position to the center of the screen
            self.box_position.setY((self.height() - self.box_size.height()) // 2)

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setBrush(QBrush(QColor(0, 0, 0, 0)))
        painter.drawRect(self.rect())

        painter.setBrush(QBrush(Qt.black))
        painter.drawRect(self.box_position.x(), self.box_position.y(), self.box_size.width(), self.box_size.height())

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.close()

def main():
    app = QApplication(sys.argv)
    overlay = GameOverlay()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
