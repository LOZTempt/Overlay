import sys, pytesseract, time, cv2, mss, numpy, random
from PyQt5.QtCore import Qt, QTimer, QPoint, QSize, QTime, QPropertyAnimation, QRect, QThread, pyqtSignal
from PyQt5.QtGui import QPainter, QBrush, QColor
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QPushButton
from input_window import InputWindow

app = QApplication([])

input_window = InputWindow()
input_window.exec_()

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

        # Set the animation duration variable equal to the value input by the user
        self.animation_duration = input_window.animation_duration * 1000
        # Set the duration of the animation to 9000 ms (9 seconds)
        self.animation.setDuration(self.animation_duration)
    
        self.initial_geometry = self.frame.geometry()
        # if loop curtain effect is on then connect the animation end signal to restart the animation
        if input_window.loop_curtain_effect == True:
           self.animation.finished.connect(self.startAnim) 

    def startAnim(self):
        if input_window.loop_curtain_new_image == True:
            self.animation.stop()
        # Set the start value of the animation to the initial geometry of the widget
        self.animation.setStartValue(self.initial_geometry)

        # Set the end value of the animation to the desired final geometry of the widget
        self.animation.setEndValue(QRect(-self.initial_geometry.x(), self.initial_geometry.height(), self.initial_geometry.width(), self.initial_geometry.height()))
        # Start the animation
        self.animation.start()

    def charScanner(self):
        mon = {'top': 0, 'left': 0, 'width': 150, 'height': 50}
        self.character_found = None

        # Create a screen capture object
        with mss.mss() as sct:
            # Initialize the variable
            character_found = False
            while not character_found and scanner_thread.scanning:  # Check if scanning flag is True
                # Capture the defined region of the screen
                im = numpy.asarray(sct.grab(mon))

                # Use pytesseract to convert the image to text
                text = pytesseract.image_to_string(im)

                # Check if the character '/' is in the text
                if 'Opening..' in text:
                    character_found = True
                    if input_window.randomness > 0: # if randomness is greater than 0
                        # Determines the random value based off the user input
                        self.animation_duration = self.randDur(input_window.randomness)
                        # Applies the random value to the animation
                        self.animation.setDuration(self.animation_duration)
                    print(self.animation_duration)
                else:
                    character_found = False

                # Display the captured image in a window
                cv2.imshow('Image', im)

                # If the "q" key is pressed, break the loop and close the window
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    cv2.destroyAllWindows()
                    break
        time.sleep(.3)
        return character_found
    
    def randDur(self, randomness):
        random_high = self.animation_duration+randomness*1000 
        random_low = self.animation_duration-randomness*1000
        if random_low < 1000:                 
            random_low = 1000 
        random_duration = random.randint(random_low, random_high) 
        return random_duration

class ScannerThread(QThread):
    signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.scanning = True  # Flag to control the scanning loop

    def run(self):
        # Loop indefinitely
        while self.scanning:
            # Call the charScanner function to check for the target text
            if window.charScanner():
                # If the target text is found, emit the signal
                self.signal.emit()
                
            else:
                # If the target text is not found, continue listening
                print("Target text not found. Listening...")
                # Add a delay to prevent high CPU usage
                time.sleep(1)

window = AnimatedWidget()
window.startAnim()
window.show()

# Create a thread for the character scanning loop
scanner_thread = ScannerThread()
# Connect the signal from the thread to the startAnim method of the AnimatedWidget
scanner_thread.signal.connect(window.startAnim)
# Start the thread
scanner_thread.start()

app.exec_()
