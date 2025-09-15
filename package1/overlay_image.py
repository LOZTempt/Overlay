import sys, pytesseract, time, cv2, mss, numpy, random
from PyQt5.QtCore import Qt, QMutex, QPropertyAnimation, QRect, QThread, pyqtSignal, QWaitCondition, QAbstractAnimation
from PyQt5.QtGui import QPainter, QBrush, QColor, QRegion
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QPushButton
from input_window import InputWindow
from enum import Enum


#TODO
# Make an option so it is just the delay then after that the box moves into place but doesn't move (have to offset it though)
# Make an option for the delay so that it will retain black during delay (is currently how it works)
# Change default behavior so that the black resets when the delay initiates
# Make option for a: delay but show black during delay b: delay but don't display black during c: keep current functionality, display the black from the prior. I think I mean hold the old position when a new image comes up for the delay length

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
        # Defining variables for use later with proper null checking
        self.current_state = ScannerState.IDLE
        self.delay = int(input_window.delay) if input_window.delay is not None else 0
        self.delay_range = int(input_window.random_delay_range) if input_window.random_delay_range is not None else 0
        self.black_toggled = False
        self._is_paused = False
        self._pause_value = None
        self._pause_time = None
        self._animation_in_progress = False
        self._should_reset_timer = True

        # Set the window flags to make the window frameless and always on top
        from PyQt5.QtCore import Qt
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # Set the window attribute to make the background translucent
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Get the primary screen of the application
        screen = QApplication.primaryScreen()
        # Get the geometry of the screen (i.e., its resolution)
        if screen:
            screen_geometry = screen.geometry()
            # Store the width and height of the screen
            self.screen_width = screen_geometry.width()
            self.screen_height = screen_geometry.height()
        else:
            # Fallback if no screen found
            self.screen_width = 1920
            self.screen_height = 1080

        # Set the geometry of the window to cover the entire screen
        self.setGeometry(0, 0, self.screen_width, self.screen_height)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

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
        
        self._pause_value = self.animation.currentValue()

        # Set the animation duration variable equal to the value input by the user
        self.animation_duration = (input_window.animation_duration * 1000) if input_window.animation_duration is not None else 5000
        # Set the duration of the animation
        self.animation.setDuration(self.animation_duration)
    
        self.initial_geometry = self.frame.geometry()
        # if loop curtain effect is on then connect the animation end signal to restart the animation
        if input_window.loop_curtain_effect == True:
           self.animation.finished.connect(self.onAnimationFinished) 
        
        # Connect animation finished signal to track animation state
        self.animation.finished.connect(self.onAnimationFinished)

    def onAnimationStarted(self):
        """Called when animation starts"""
        self._animation_in_progress = True
        self._should_reset_timer = False
    
    def onAnimationFinished(self):
        """Called when animation finishes"""
        self._animation_in_progress = False
        self._should_reset_timer = True
        
        # Only restart animation if loop curtain effect is enabled
        if input_window.loop_curtain_effect:
            self.startAnim()

    def startAnim(self):
        # Handle black screen behavior based on delay_behaviour setting
        if input_window.delay_behaviour == "Black":
            if self.black_toggled:
                self.toggleBlack()
        elif input_window.delay_behaviour == "Transparent":
            # Hide black frames to make screen transparent during transition
            if self.black_toggled:
                self.toggleBlack()
        elif input_window.delay_behaviour == "Hold last position":
            # Pause current animation if running and don't show black
            if self.animation.state() == QAbstractAnimation.State.Running:
                self.pause()
                # We'll resume after delay in a separate method
                if self.delay > 0:
                    if self.delay_range > 0:
                        sleep_time = self.randDur(self.delay_range, self.delay)/1000
                        print(f"Holding position for: {sleep_time}")
                        time.sleep(sleep_time)
                    else:
                        time.sleep(self.delay/1000)
                self.resume()
                return

        # Only stop and reset animation if loop_curtain_new_image is enabled
        # or if this is the first time the animation is starting
        if input_window.loop_curtain_new_image or self._should_reset_timer:
            self.animation.stop()
            
            # Only generate new random duration if we should reset the timer
            if self._should_reset_timer and hasattr(input_window, 'randomness') and input_window.randomness and input_window.randomness > 0:
                # Determines the random value based off the user input
                self.animation_duration = self.randDur(input_window.randomness, input_window.animation_duration)
                # Applies the random value to the animation
                self.animation.setDuration(self.animation_duration)
                print(f"New animation duration: {self.animation_duration}")
            
        # Apply delay if configured
        if self.delay > 0:
            if self.delay_range > 0:
                sleep_time = self.randDur(self.delay_range, self.delay)/1000
                print(f"Sleeping for: {sleep_time}")
                time.sleep(sleep_time)
            else:
                time.sleep(self.delay/1000)

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
                    print("Opening detected")
                elif '[' and ']' in text:
                    character_found = 1
                    print("Image loaded detected")
                else:
                    character_found = 0

                # Display the captured image in a window
                cv2.imshow('Image', im)

                # If the "q" key is pressed, break the loop and close the window
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    cv2.destroyAllWindows()
                    break
        return character_found
    
    def randDur(self, randomness, orig_bounds):
        random_high = orig_bounds*1000+randomness*1000 
        random_low = orig_bounds*1000-randomness*1000
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
            # Handle opening state based on delay behavior
            if input_window.delay_behaviour == "Black":
                self.toggleBlack()
            elif input_window.delay_behaviour == "Transparent":
                # Don't show black, keep current state
                pass
            # Pause any current animation and hold position
            if input_window.delay_behaviour == "Hold last position":
                # Pause any current animation and hold position
                if self.animation.state() == QAbstractAnimation.State.Running:
                    self.pause()
        elif new_state == ScannerState.IMAGE_LOADED:
            # Resume from hold position if needed
            if input_window.delay_behaviour == "Hold last position" and self._is_paused:
                self.resume()
            else:
                self.startAnim()
        elif new_state == ScannerState.IDLE:
            # Handle transition to idle state if needed
            pass
    # Added pause and resume functions for the animation, to be used later. Hopefully they work...
    def pause(self):
        # This is the only line im not sure if it will work
        if self.animation.state() == QAbstractAnimation.State.Running:
            self._is_paused = True
            self._pause_value = self.animation.currentValue()
            self._pause_time = self.animation.currentTime()
            self.animation.stop()

    def resume(self):
        if self._is_paused and self._pause_value is not None and self._pause_time is not None:
            self.animation.setStartValue(self._pause_value)
            self.animation.setCurrentTime(self._pause_time)
            self.animation.start()
            self._is_paused = False

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

window = AnimatedWidget()
window.startAnim()
window.show()

# Create a thread for the character scanning loop
scanner_thread = ScannerThread()
# Connect the signal to the handle_state_change function in the window class
scanner_thread.signal_state_changed.connect(window.handle_state_change)
# Start the thread
scanner_thread.start()

app.exec_()
