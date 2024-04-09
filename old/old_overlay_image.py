import sys, time, threading, random
from PyQt5.QtCore import Qt, QTimer, QPoint, QSize, QTime, QPropertyAnimation, QRect
from PyQt5.QtGui import QPainter, QBrush, QColor
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QPushButton
from detect_change import CharacterScanner
from input_window import InputWindow

app = QApplication([])

input_window = InputWindow()
input_window.exec_()

animation_duration = input_window.animation_duration * 1000 

mon = {'top': 0, 'left': 0, 'width': 150, 'height': 50}
scanner = CharacterScanner(mon)

# scan_thread = threading.Thread(target=scanner.scan_for_character)
# scan_thread.start()
# scan_thread.join()

class GameOverlay(QWidget):
    def __init__(self):
        super().__init__()

        self.poop = 0
        self.loop_curtain_img = input_window.loop_curtain_new_image

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()

        self.screen_width = screen_geometry.width()
        self.screen_height = screen_geometry.height()

        self.setGeometry(0, 0, self.screen_width, self.screen_height)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.frame = QFrame(self)
        self.frame.setStyleSheet('background-color: black;')
        self.frame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.frame.resize(3840, 1600)

        self.animation = QPropertyAnimation(self.frame, b"geometry")
        scan_thread = threading.Thread(target=self.checkCharacter)
        scan_thread.start()
        scan_thread.join()

        self.initial_geometry = self.frame.geometry()
        self.animation.setStartValue(self.initial_geometry)
        
        self.animation.setEndValue(QRect(-self.initial_geometry.x(), self.initial_geometry.height(), self.initial_geometry.width(), self.initial_geometry.height()))
        #self.animation.finished.connect(self.resetBox)
        self.animation.setDuration(animation_duration)
        self.animation.start()

        self.check_thread = threading.Thread(target=self.checkCharacter)
        self.check_thread.start()
        
    def checkCharacter(self):
        if self.loop_curtain_img:
            while True:
                self.character_found = scanner.scan_for_character()
                if self.character_found:
                    print("Found")
                    # Re rolls randomness only when a character is detected
                    randomness = input_window.randomness 
                    if randomness > 0: 
                        self.animation.setDuration(self.randDur(randomness)) 
                    self.resetBox()
                    
    def resetBox(self):
        loop_curtain = input_window.loop_curtain_effect
        
        #print (loop_curtain, self.poop)
        if (not loop_curtain) and self.poop == 0:
            self.poop += 1
            #print("if triggered")
            

        elif self.poop > 0:
            self.poop -= 1
            # Set the start value to the current geometry
            self.animation.setStartValue(self.initial_geometry)
            # Set the end value to move the frame off the screen
            self.animation.setEndValue(QRect(-self.initial_geometry.x(), self.initial_geometry.height(), self.initial_geometry.width(), self.initial_geometry.height()))
            # Start the animation
            self.animation.start()       
            print("POOP!")
        else:
            self.animation.stop()
            initial_geometry = QRect(0, 40, 3840, 1600)
            self.animation.setStartValue(initial_geometry)  
            self.animation.setEndValue(QRect(-initial_geometry.x(), initial_geometry.height(), initial_geometry.width(), initial_geometry.height()))
            self.animation.start()
            print("else triggered")

    # Define the method to handle mouse press events
    def mousePressEvent(self, event):
        # If the middle mouse button is pressed, close the window
        if event.button() == Qt.MiddleButton:
            self.close()

    def randDur(randomness):
        random_high = animation_duration+randomness*1000 
        random_low = animation_duration-randomness*1000
        if random_low < 1000:                 
            random_low = 1000 
        random_duration = random.randint(random_low, random_high) 
        return random_duration

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

