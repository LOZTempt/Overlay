import time
import cv2
import mss
import numpy
import pytesseract

# Define the monitor region to capture
mon = {'top': 0, 'left': 0, 'width': 300, 'height': 150}

def scan_for_character():
    # Create a screen capture object
    with mss.mss() as sct:
        # Initialize the variable
        character_found = False
        while not character_found:
            # Capture the defined region of the screen
            im = numpy.asarray(sct.grab(mon))

            # Use pytesseract to convert the image to text
            text = pytesseract.image_to_string(im)

            # Check if the character '/' is in the text
            if '/' in text:
                print("Character found!")
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
            time.sleep(1)

    return character_found

# Use the function
character_found = scan_for_character()
print(f"Character found: {character_found}")
