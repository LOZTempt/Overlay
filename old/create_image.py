from PIL import Image, ImageDraw
import pyautogui

def create_blank_image():
    # Get screen size
    screen_width, screen_height = pyautogui.size()

    # Create a blank image with a black background and transparency
    black_image = Image.new('RGBA', (screen_width, screen_height), color=(0, 0, 0, 255))

    # Define the file path within the package1 directory
    black_image_path = "package1/overlay_image.png"

    # Now save the image to the specified path
    black_image.save(black_image_path)
