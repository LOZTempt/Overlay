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
        
        # Validate input_window configuration
        self.validate_configuration()
        
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
        self._last_animation_duration = None
        self._curtain_direction = input_window.curtain_direction if input_window.curtain_direction is not None else "Left to Right"

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

        # Create frames for different curtain directions
        self.create_curtain_frames()
        
        # Create a QPropertyAnimation instance
        self.animation = QPropertyAnimation(self.frame, b"geometry")
        
        self._pause_value = self.animation.currentValue()

        # Set the animation duration variable equal to the value input by the user
        self.animation_duration = (input_window.animation_duration * 1000) if input_window.animation_duration is not None else 5000
        # Set the duration of the animation
        self.animation.setDuration(self.animation_duration)
    
        self.initial_geometry = self.frame.geometry()
        
        # Connect animation signals
        self.animation.started.connect(self.onAnimationStarted)
        self.animation.finished.connect(self.onAnimationFinished)
        
        # if loop curtain effect is on then connect the animation end signal to restart the animation
        if input_window.loop_curtain_effect == True:
           self.animation.finished.connect(self.onAnimationFinished)
           
        # Add keyboard shortcuts for testing (optional)
        self.setup_keyboard_shortcuts()

    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for testing and debugging"""
        try:
            from PyQt5.QtWidgets import QShortcut
            from PyQt5.QtGui import QKeySequence
            
            # Add shortcut for manual animation test (Ctrl+T)
            test_shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
            test_shortcut.activated.connect(self.test_animation)
            
            # Add shortcut for reset (Ctrl+R) 
            reset_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
            reset_shortcut.activated.connect(self.reset_to_initial_position)
            
            print("Keyboard shortcuts enabled: Ctrl+T (test), Ctrl+R (reset)")
        except Exception as e:
            print(f"Could not setup keyboard shortcuts: {e}")

    def validate_configuration(self):
        """Validate the input window configuration and set defaults if needed"""
        try:
            if not hasattr(input_window, 'delay_behaviour') or input_window.delay_behaviour is None:
                input_window.delay_behaviour = "Hold last position"
                print("Warning: delay_behaviour not set, defaulting to 'Hold last position'")
                
            if not hasattr(input_window, 'curtain_direction') or input_window.curtain_direction is None:
                input_window.curtain_direction = "Left to Right"
                print("Warning: curtain_direction not set, defaulting to 'Left to Right'")
                
            if not hasattr(input_window, 'loop_curtain_new_image'):
                input_window.loop_curtain_new_image = True
                print("Warning: loop_curtain_new_image not set, defaulting to True")
                
            print(f"Configuration validated - Delay behaviour: {input_window.delay_behaviour}, Direction: {input_window.curtain_direction}")
        except Exception as e:
            print(f"Error validating configuration: {e}")
            # Set safe defaults
            input_window.delay_behaviour = "Hold last position"
            input_window.curtain_direction = "Left to Right"
            input_window.loop_curtain_new_image = True

    def create_curtain_frames(self):
        """Create the black frames for curtain effect based on direction"""
        # Frame to cover the entire screen except for the left 150 pixels
        self.full_black_main = QFrame(self)
        self.full_black_main.setGeometry(150, 0, self.screen_width - 150, self.screen_height)
        self.full_black_main.setStyleSheet('background-color: black;')

        # Frame to cover the top 50 pixels of the left 150 pixels
        self.full_black_cutout = QFrame(self)
        self.full_black_cutout.setGeometry(0, 50, 150, self.screen_height - 50)
        self.full_black_cutout.setStyleSheet('background-color: black;')

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
        """Start or restart the curtain animation with proper state management"""
        print(f"startAnim called - current state: {self.current_state}")
        print(f"Animation in progress: {self._animation_in_progress}")
        print(f"Should reset timer: {self._should_reset_timer}")
        print(f"Loop curtain new image: {input_window.loop_curtain_new_image}")
        
        # Handle delay behavior first
        if input_window.delay_behaviour == "Hold last position":
            print("Using Hold last position behavior")
            # In hold last position mode, we DON'T reset the animation or start a new one
            # We just apply the delay and continue with the current position
            if self.delay > 0:
                delay_time = self.delay
                if self.delay_range > 0:
                    delay_time = self.randDur(self.delay_range, self.delay) / 1000
                print(f"Holding position for: {delay_time} seconds")
                time.sleep(delay_time)
            # Don't start a new animation, just return and keep current position
            return
        elif input_window.delay_behaviour == "Transparent":
            print("Using Transparent behavior")
            # Set transparent mode during transition
            self.setTransparentMode(True)
        elif input_window.delay_behaviour == "Black":
            print("Using Black behavior")
            # Ensure transparent mode is off and show black overlay
            self.setTransparentMode(False)
            if not self.black_toggled:
                self.toggleBlack()

        # Apply delay before starting animation
        if self.delay > 0:
            delay_time = self.delay
            if self.delay_range > 0:
                delay_time = self.randDur(self.delay_range, self.delay) / 1000
            print(f"Applying delay: {delay_time} seconds")
            time.sleep(delay_time)

        # Only reset animation and generate new duration under specific conditions
        should_start_new_animation = False
        
        if input_window.loop_curtain_new_image:
            # If loop on new image is enabled, always start fresh
            should_start_new_animation = True
            print("Starting new animation because loop_curtain_new_image is enabled")
        elif not self._animation_in_progress and self._should_reset_timer:
            # If no animation is running and we should reset, start new
            should_start_new_animation = True
            print("Starting new animation because no animation is running")
        elif self._animation_in_progress:
            # If animation is already running, don't interfere
            print("Animation already running, not starting new one")
            return
        
        if should_start_new_animation:
            # Stop any existing animation
            self.animation.stop()
            
            # Generate new random duration only if enabled and conditions are met
            if (input_window.loop_curtain_new_image or self._should_reset_timer) and \
               hasattr(input_window, 'randomness') and input_window.randomness and input_window.randomness > 0:
                # Generate new random duration
                self.animation_duration = self.randDur(input_window.randomness, input_window.animation_duration)
                self.animation.setDuration(self.animation_duration)
                print(f"Generated new animation duration: {self.animation_duration}ms")
            else:
                # Use last duration or default
                if self._last_animation_duration:
                    self.animation.setDuration(self._last_animation_duration)
                    print(f"Using previous animation duration: {self._last_animation_duration}ms")
                else:
                    self.animation.setDuration(self.animation_duration)
                    print(f"Using default animation duration: {self.animation_duration}ms")
            
            # Store the current duration for future use
            self._last_animation_duration = self.animation.duration()
            
            # Set animation geometry based on curtain direction
            self.setup_animation_geometry()
            
            # Start the animation
            print("Starting curtain animation")
            self.animation.start()
        
    def setup_animation_geometry(self):
        """Setup start and end geometry based on curtain direction"""
        direction = self._curtain_direction
        
        if direction == "Random Mix":
            # Randomly choose direction for this iteration
            direction = random.choice(["Left to Right", "Top to Bottom", "Bottom to Top"])
            print(f"Random direction chosen: {direction}")
        
        if direction == "Left to Right":
            # Original left-to-right animation
            self.animation.setStartValue(self.initial_geometry)
            self.animation.setEndValue(QRect(-self.initial_geometry.x(), self.initial_geometry.y(), 
                                           self.initial_geometry.width(), self.initial_geometry.height()))
        elif direction == "Top to Bottom":
            # Top to bottom animation
            self.animation.setStartValue(QRect(self.initial_geometry.x(), -self.initial_geometry.height(), 
                                             self.initial_geometry.width(), self.initial_geometry.height()))
            self.animation.setEndValue(QRect(self.initial_geometry.x(), self.screen_height,
                                           self.initial_geometry.width(), self.initial_geometry.height()))
        elif direction == "Bottom to Top":
            # Bottom to top animation
            self.animation.setStartValue(QRect(self.initial_geometry.x(), self.screen_height, 
                                             self.initial_geometry.width(), self.initial_geometry.height()))
            self.animation.setEndValue(QRect(self.initial_geometry.x(), -self.initial_geometry.height(),
                                           self.initial_geometry.width(), self.initial_geometry.height()))
        
        print(f"Animation geometry set for direction: {direction}")

    def charScanner(self):
        """Scan for specific text patterns in the defined screen region"""
        try:
            mon = {'top': 0, 'left': 0, 'width': 150, 'height': 50}
            self.character_found = None

            # Create a screen capture object
            with mss.mss() as sct:
                # Initialize the variable
                character_found = 0
                while character_found == 0 and scanner_thread.scanning:  # Check if scanning flag is True
                    try:
                        # Capture the defined region of the screen
                        im = numpy.asarray(sct.grab(mon))

                        # Use pytesseract to convert the image to text
                        text = pytesseract.image_to_string(im)

                        # Check if the character '/' is in the text
                        if 'Opening..' in text:
                            character_found = 2
                            print("Opening detected")
                        elif '[' in text and ']' in text:
                            character_found = 1
                            print("Image loaded detected")
                        else:
                            character_found = 0

                        # Display the captured image in a window (optional for debugging)
                        cv2.imshow('Image', im)

                        # If the "q" key is pressed, break the loop and close the window
                        if cv2.waitKey(25) & 0xFF == ord('q'):
                            cv2.destroyAllWindows()
                            break
                    except Exception as e:
                        print(f"Error in charScanner loop: {e}")
                        time.sleep(0.1)  # Small delay on error
                        
            return character_found
        except Exception as e:
            print(f"Error in charScanner: {e}")
            return 0
    
    def randDur(self, randomness, orig_bounds):
        random_high = orig_bounds*1000+randomness*1000 
        random_low = orig_bounds*1000-randomness*1000
        if random_low < 1000:                 
            random_low = 1000 
        random_duration = random.randint(random_low, random_high) 
        return random_duration

    def toggleBlack(self):
        """Toggle the black overlay frames on/off"""
        if self.black_toggled:
            self.full_black_main.hide()
            self.full_black_cutout.hide()
            print("Black overlay hidden")
        else:
            self.full_black_main.show()
            self.full_black_cutout.show()
            print("Black overlay shown")
        self.black_toggled = not self.black_toggled
    
    def setTransparentMode(self, transparent=True):
        """Set the overlay to transparent mode"""
        if transparent:
            # Hide all black frames to make everything transparent
            self.full_black_main.hide()
            self.full_black_cutout.hide()
            # Also hide the main curtain frame if needed
            self.frame.hide()
            self.black_toggled = False
            print("Transparent mode enabled")
        else:
            # Show the appropriate frames based on current state
            if not self.black_toggled:
                self.full_black_main.show()
                self.full_black_cutout.show()
            self.frame.show()
            print("Transparent mode disabled")

    def handle_state_change(self, new_state):
        """Handle state changes from the scanner thread"""
        print(f"State change: {self.current_state} -> {new_state}")
        
        if new_state == ScannerState.OPENING:
            self.current_state = new_state
            # Handle opening state based on delay behavior
            if input_window.delay_behaviour == "Black":
                if not self.black_toggled:
                    self.toggleBlack()
            elif input_window.delay_behaviour == "Transparent":
                # Enable transparent mode during opening
                self.setTransparentMode(True)
            elif input_window.delay_behaviour == "Hold last position":
                # In hold last position mode, we don't change anything during opening
                # The curtain should stay exactly where it is
                print("Opening detected - holding current position")
                pass
                
        elif new_state == ScannerState.IMAGE_LOADED:
            self.current_state = new_state
            # Disable transparent mode if it was enabled
            if input_window.delay_behaviour == "Transparent":
                self.setTransparentMode(False)
            # Start animation when image is loaded
            self.startAnim()
            
        elif new_state == ScannerState.IDLE:
            self.current_state = new_state
            # Handle transition to idle state if needed
            pass
    # Added pause and resume functions for the animation (kept for potential future use)
    def pause(self):
        """Pause the current animation"""
        if self.animation.state() == QAbstractAnimation.State.Running:
            self._is_paused = True
            self._pause_value = self.animation.currentValue()
            self._pause_time = self.animation.currentTime()
            self.animation.pause()
            print("Animation paused")

    def resume(self):
        """Resume the paused animation"""
        if self._is_paused:
            self.animation.resume()
            self._is_paused = False
            print("Animation resumed")
            
    def test_animation(self):
        """Test method to manually trigger animation for debugging"""
        print("Testing animation manually")
        self.startAnim()
        
    def reset_to_initial_position(self):
        """Reset the curtain to its initial position"""
        self.animation.stop()
        self.frame.setGeometry(self.initial_geometry)
        self._animation_in_progress = False
        self._should_reset_timer = True
        print("Curtain reset to initial position")
        
    def cleanup(self):
        """Clean up resources and stop all animations"""
        try:
            self.animation.stop()
            # Hide all frames
            self.frame.hide()
            self.full_black_main.hide()
            self.full_black_cutout.hide()
            print("Cleanup completed")
        except Exception as e:
            print(f"Error during cleanup: {e}")
            
    def closeEvent(self, event):
        """Handle window close event"""
        self.cleanup()
        super().closeEvent(event)

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
        """Main scanning loop with optimized performance"""
        # Loop indefinitely
        consecutive_errors = 0
        max_errors = 5
        
        while self.scanning:
            try:
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

                # Reset error counter on successful scan
                consecutive_errors = 0
                
                # Adaptive sleep based on current state
                if self.current_state == ScannerState.IDLE:
                    time.sleep(0.2)  # Longer sleep when idle
                else:
                    time.sleep(0.1)  # Shorter sleep when active
                    
            except Exception as e:
                consecutive_errors += 1
                print(f"Scanner thread error {consecutive_errors}/{max_errors}: {e}")
                
                if consecutive_errors >= max_errors:
                    print("Too many consecutive errors, stopping scanner thread")
                    self.scanning = False
                    break
                    
                time.sleep(0.5)  # Longer sleep on error

window = AnimatedWidget()
# Don't start animation immediately - wait for image detection
window.show()

# Create a thread for the character scanning loop
scanner_thread = ScannerThread()
# Connect the signal to the handle_state_change function in the window class
scanner_thread.signal_state_changed.connect(window.handle_state_change)
# Start the thread
scanner_thread.start()

try:
    app.exec_()
finally:
    # Cleanup on exit
    print("Shutting down...")
    scanner_thread.scanning = False
    scanner_thread.wait(2000)  # Wait up to 2 seconds for thread to finish
    window.cleanup()
    cv2.destroyAllWindows()
