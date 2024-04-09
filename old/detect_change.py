import time
import cv2
import mss
import numpy
import pytesseract

class CharacterScanner:
    def __init__(self, mon):
        self.mon = mon

        self.character_found = None

    def scan_for_character(self):
        # Create a screen capture object
        with mss.mss() as sct:
            # Initialize the variable
            character_found = False
            while not character_found:
                # Capture the defined region of the screen
                im = numpy.asarray(sct.grab(self.mon))

                # Use pytesseract to convert the image to text
                text = pytesseract.image_to_string(im)

                # Check if the character '/' is in the text
                if 'Opening..' in text:
                    #print("Character found!")
                    character_found = True
                else:
                    character_found = False

                # Display the captured image in a window
                cv2.imshow('Image', im)

                # If the "q" key is pressed, break the loop and close the window
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    cv2.destroyAllWindows()
                    break

                # One screenshot per second
                #time.sleep(.1)

        #time.sleep(.3)
        return character_found
