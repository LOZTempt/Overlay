import sys, pytesseract, time, cv2, mss, numpy, random
from PyQt5.QtCore import Qt, QMutex, QPropertyAnimation, QRect, QThread, pyqtSignal, QWaitCondition
from PyQt5.QtGui import QPainter, QBrush, QColor, QRegion
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QPushButton
from input_window import InputWindow
from enum import Enum


#TODO
# Make an option so it is just the delay then after that the box moves into place but doesn't move (have to offset it though)
# Make an option for the delay so that it will retain black during delay (is currently how it works)
# Change default behavior so that the black resets when the delay initiates
# Make option for a: delay but show black during delay b: delay but don't display black during c: keep current functionality, display the black from the prior. I think I mean hold the old position when a new image comes up for the delay length

# New stuff TODO as of July:
# Make it so the "curtain" doesn't start moving until the image is actually loaded
# Idea is when opening is detected, just cover the screen (Except top left) completely in black, then when the text is detected when an image is open then start the 

app = QApplication([])

input_window = InputWindow()
input_window.exec_()

class ScannerState(Enum):
    IDLE = 0
    OPENING = 1
    IMAGE_LOADED = 2

class AnimatedWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.current_state = ScannerState.IDLE
        self.delay = int(input_window.delay * 1000)
        self.black_toggled = False
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

        # Frame to cover the entire screen except for the left 150 pixels
        self.full_black_main = QFrame(self)
        self.full_black_main.setGeometry(150, 0, self.screen_width - 150, self.screen_height)
        self.full_black_main.setStyleSheet('background-color: black;')

        # Frame to cover the top 50 pixels of the left 150 pixels
        self.full_black_cutout = QFrame(self)
        self.full_black_cutout.setGeometry(0, 50, 150, self.screen_height - 50)
        self.full_black_cutout.setStyleSheet('background-color: black;')

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
        # Initialize mutex and wait condition

    def startAnim(self):
        if self.black_toggled:
            self.toggleBlack()

        if input_window.loop_curtain_new_image == True:
            self.animation.stop()
            
        # if self.delay > 0:

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
            character_found = 0
            while character_found == 0 and scanner_thread.scanning:  # Check if scanning flag is True
                # Capture the defined region of the screen
                im = numpy.asarray(sct.grab(mon))

                # Use pytesseract to convert the image to text
                text = pytesseract.image_to_string(im)

                # Check if the character '/' is in the text
                if 'Opening..' in text:
                    character_found = 2
                    if input_window.randomness > 0: # if randomness is greater than 0
                        # Determines the random value based off the user input
                        self.animation_duration = self.randDur(input_window.randomness)
                        # Applies the random value to the animation
                        self.animation.setDuration(self.animation_duration)
                    print(self.animation_duration)
                elif '[' and ']' in text:
                    character_found = 1
                else:
                    character_found = 0

                # Display the captured image in a window
                cv2.imshow('Image', im)

                # If the "q" key is pressed, break the loop and close the window
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    cv2.destroyAllWindows()
                    break
        
        
        # if character_found == 1:
        #     time.sleep(2)
        # print(character_found)
        return character_found
    
    def randDur(self, randomness):
        print(input_window.animation_duration)
        random_high = input_window.animation_duration*1000+randomness*1000 
        random_low = input_window.animation_duration*1000-randomness*1000
        if random_low < 1000:                 
            random_low = 1000 
        random_duration = random.randint(random_low, random_high) 
        return random_duration

    def toggleBlack(self):
        if self.black_toggled:
            self.full_black_main.hide()
            self.full_black_cutout.hide()
        else:
            self.full_black_main.show()
            self.full_black_cutout.show()
        self.black_toggled = not self.black_toggled

    def handle_state_change(self, new_state):
        if new_state == ScannerState.OPENING:
            self.toggleBlack()
        elif new_state == ScannerState.IMAGE_LOADED:
            self.startAnim()
        elif new_state == ScannerState.IDLE:
            # Handle transition to idle state if needed
            pass
        

class ScannerThread(QThread):
    signal_new = pyqtSignal()
    signal_open = pyqtSignal()
    signal_state_changed = pyqtSignal(ScannerState)

    def __init__(self):
        super().__init__()
        self.scanning = True  # Flag to control the scanning loop
        self.current_state = ScannerState.IDLE
        self.state_change_time = 0

    def run(self):
        # Loop indefinitely
        while self.scanning:
            # Call the charScanner function to check for the target text
            scan_result = window.charScanner()
            new_state = None

            if scan_result == 2 and self.current_state != ScannerState.OPENING:
                new_state = ScannerState.OPENING
            elif scan_result == 1 and self.current_state != ScannerState.IMAGE_LOADED:
                new_state = ScannerState.IMAGE_LOADED
            elif scan_result == 0 and self.current_state != ScannerState.IDLE:
                new_state = ScannerState.IDLE

            if new_state is not None:
                self.current_state = new_state
                self.state_change_time = time.time()
                self.signal_state_changed.emit(new_state)

            time.sleep(0.1)  # Short sleep to prevent high CPU usage

            # # If 1 is returned, it means a new image is being loaded. So block the screen.
            # if scan_result == 1:
            #     # If the target text is found, emit the signal
            #     self.signal_new.emit()

            #     time.sleep(2)

            # # If 2 is returned, it means a new image has just been opened. So restart the animation.
            # elif scan_result == 2:
            #     # If the target text is found, emit the signal
            #     self.signal_open.emit()

            #     time.sleep(1.1)
            # # If neither are returned then wait before trying again.
            # else:
            #     # If the target text is not found, continue listening
            #     print("Target text not found. Listening...")
            #     # Add a delay to prevent high CPU usage
            #     time.sleep(1)

window = AnimatedWidget()
window.startAnim()
window.show()

# Create a thread for the character scanning loop
scanner_thread = ScannerThread()

scanner_thread.signal_state_changed.connect(window.handle_state_change)
# # Connect the signal from the thread to the startAnim method of the AnimatedWidget
# scanner_thread.signal_open.connect(window.toggleBlack)
# # Connect the signal from the thread to the startAnim method of the AnimatedWidget
# scanner_thread.signal_new.connect(window.startAnim)
# Start the thread
scanner_thread.start()

app.exec_()
